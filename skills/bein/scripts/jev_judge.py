"""Jev (TypeSafe System One) as bein's cheap bulk filter.

  setup      run.json  checks the key and SDK, prints what a run would cost in calls
  known      run.json  P(candidate is an existing idea) -> pool[i].known_jev
                       known = mirror baseline + run.json["world"] (web research) + discarded.md
                       --keep N  keeps only the N least-known candidates in the pool
  coherence  run.json  0-3 rubric score -> pool[i].coherence_jev  (diagnostic only: failed the
                       2026-11-23 test, rank correlation 0.09 with Claude judges; never feed it to fuse)
  --dry-run  prints the call count, calls nothing

Key: TYPESAFE_API_KEY (or JEV_API_KEY): env, else the nearest .env upward, else ~/.bein/.env.
Get one at https://typesafe.ai. The key is only sent to TypeSafe and never printed.
SDK: pip install typesafe-sdk. Model: --model, else the account default.
"""
import argparse, json, os, pathlib, sys

HERE = pathlib.Path(__file__).resolve().parent
HOME = pathlib.Path(os.getenv("BEIN_HOME", pathlib.Path.home() / ".bein"))


def user_file(name):
    """bein's memory lives in ~/.bein so a skill update never wipes it; seeded from the shipped template."""
    HOME.mkdir(parents=True, exist_ok=True)
    f, tpl = HOME / name, HERE.parent / name
    if not f.exists() and tpl.exists():
        f.write_text(tpl.read_text(encoding="utf-8"), encoding="utf-8")
    return f
KEYS = ("TYPESAFE_API_KEY", "JEV_API_KEY", "jev_api_key")
BATCH = 20  # questions per call; they share the known-ideas prefix, so one prefill serves all
RUBRIC = [
    "No link: nothing makes these parts work together on the problem.",
    "Forced: the link is wordplay or needs a big leap.",
    "Plausible: you can state one concrete mechanism that links them.",
    "Tight: one mechanism where each part needs the others.",
]


def api_key():
    for k in KEYS:
        if os.getenv(k):
            return os.environ[k]
    for env in [d / ".env" for d in [pathlib.Path.cwd(), *pathlib.Path.cwd().parents]] + [HOME / ".env"]:
        if env.is_file():
            for line in env.read_text(encoding="utf-8", errors="ignore").splitlines():
                name, _, val = line.partition("=")
                if name.strip() in KEYS and val.strip():
                    return val.strip().strip('"').strip("'")
    return None


def discarded():
    d = user_file("discarded.md")
    if not d.is_file():
        return []
    return [l[2:].split(" — ")[0].strip() for l in d.read_text(encoding="utf-8").splitlines()
            if l.startswith("- ")]


def text(run, ids):
    by = {a["id"]: a["text"] for a in run["atoms"]}
    anchors = set(run.get("anchor_slots", []))
    slot = {a["id"]: a["slot"] for a in run["atoms"]}
    return " ".join(by[i] for i in ids if slot[i] not in anchors)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["setup", "known", "coherence"])
    ap.add_argument("run")
    ap.add_argument("--model")
    ap.add_argument("--keep", type=int)
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    run = json.load(open(a.run, encoding="utf-8"))
    pool = run["pool"]
    known = [text(run, b) for b in run["baseline"]] + run.get("world", []) + discarded()
    calls = -(-len(pool) // BATCH) if a.cmd in ("known", "setup") else len(pool)
    print(f"{a.cmd}: {len(pool)} candidates, {len(known)} known ideas "
          f"({len(run.get('world', []))} world, {len(discarded())} discarded), {calls} calls")

    if a.cmd == "setup":
        try:
            import typesafe_sdk  # noqa: F401
            sdk = "ok"
        except ImportError:
            sdk = "missing: pip install typesafe-sdk"
        print(f"key: {'found' if api_key() else 'missing: add TYPESAFE_API_KEY=... to ' + str(HOME / '.env')}; sdk: {sdk}")
        return
    if a.dry_run:
        return
    key = api_key()
    if not key:
        sys.exit("No Jev key: set TYPESAFE_API_KEY / jev_api_key, or put it in .env")
    from typesafe_sdk import Noul, Score, TypeSafeClient

    used = 0
    with TypeSafeClient(api_key=key) as client:
        if a.cmd == "known":
            state = {"known_ideas": known}
            for s in range(0, len(pool), BATCH):
                chunk = pool[s:s + BATCH]
                q = {f"c{i}": Noul(instructions="Is this candidate essentially the same idea as one of "
                                   "the known ideas, only reworded? Candidate: " + text(run, c["atoms"]))
                     for i, c in enumerate(chunk)}
                r = client.system_one(state=state, questions=q, model=a.model)
                used += (r.usage.input_tokens or 0) if r.usage else 0
                for i, c in enumerate(chunk):
                    c["known_jev"] = round(r.nouls[f"c{i}"].noul, 3)
            if a.keep:
                run["pool"] = sorted(pool, key=lambda c: c["known_jev"])[:a.keep]
                print(f"kept {len(run['pool'])} least-known (max known {run['pool'][-1]['known_jev']})")
        else:
            for c in pool:
                q = {"c": Score(instructions="Can ONE concrete mechanism make all these parts work together "
                                "on the problem? Do not reward novelty or familiarity.", criteria=RUBRIC)}
                r = client.system_one(state={"problem": run.get("problem", ""), "parts": text(run, c["atoms"])},
                                      questions=q, model=a.model)
                used += (r.usage.input_tokens or 0) if r.usage else 0
                c["coherence_jev"] = round(r.scores["c"].score, 3)
    json.dump(run, open(a.run, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    print(f"done, {used} input tokens")


if __name__ == "__main__":
    main()
