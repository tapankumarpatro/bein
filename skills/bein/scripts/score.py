"""bein scorer. Python 3 stdlib only.

  python score.py rank    run.json [--pool 40] [--seed 7] [--max-shared 1]   -> run.json["pool"]
                          (big pool for the Jev filter: --pool 400 --max-shared 2)
  python score.py fuse    run.json [--beta 0.6] [--top 8]   -> run.json["shortlist"]
  python score.py compare run.json                          -> diversity: bein vs baseline
  python score.py selftest

run.json:
  slots        ["problem", "mechanism", ...]      one atom per slot = one idea
  anchor_slots ["problem"]                        these slots only take source=home atoms
  atoms        [{"id","slot","text","source": home|far|mutation|default}]
  baseline     [["p1","m2",...], ...]             Claude's default ideas, tagged to atom ids
  pool[i].coherence  0-3, written by the judge before `fuse`
  final        [["p1","m7",...], ...]             finished bein ideas, for `compare`
"""
import itertools, json, math, random, sys
from collections import Counter

MAX_CANDIDATES = 200_000  # ponytail: random sample above this; smarter search if slots grow huge


def load(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def save(path, run):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(run, f, indent=2, ensure_ascii=False)


def availability_model(baseline):
    """Smoothed log-likelihood of a combination under Claude's own default ideas.
    High = the obvious answer. No hand-tuned weights: just counts."""
    n = max(len(baseline), 1)
    atom_c = Counter(a for idea in baseline for a in set(idea))
    pair_c = Counter(p for idea in baseline for p in itertools.combinations(sorted(set(idea)), 2))

    def score(atoms):
        a = sum(math.log((atom_c[x] + 1) / (n + 2)) for x in atoms) / len(atoms)
        pairs = list(itertools.combinations(sorted(atoms), 2))
        p = sum(math.log((pair_c[x] + 1) / (n + 2)) for x in pairs) / max(len(pairs), 1)
        return a + p

    return score


def candidates(run, rng):
    by_slot = []
    for s in run["slots"]:
        ok = [a["id"] for a in run["atoms"] if a["slot"] == s
              and (s not in run.get("anchor_slots", []) or a["source"] == "home")]
        if not ok:
            sys.exit(f"slot '{s}' has no usable atoms")
        by_slot.append(ok)
    total = math.prod(len(x) for x in by_slot)
    if total <= MAX_CANDIDATES:
        return list(itertools.product(*by_slot))
    return list({tuple(rng.choice(x) for x in by_slot) for _ in range(MAX_CANDIDATES)})


def diverse_top(ranked, k, ignore=(), max_shared=1):
    """Greedy pick: no two picks share more than max_shared atoms (paper's near-duplicate rule).
    Anchor atoms are ignored: every idea is meant to share the user's problem."""
    out, ignore = [], set(ignore)
    for c in ranked:
        if all(len((set(c["atoms"]) & set(o["atoms"])) - ignore) <= max_shared for o in out):
            out.append(c)
            if len(out) == k:
                break
    return out


def anchor_ids(run):
    return {a["id"] for a in run["atoms"] if a["slot"] in run.get("anchor_slots", [])}


def rank(run, pool=40, seed=7, max_shared=1):
    rng = random.Random(seed)
    avail = availability_model(run["baseline"])
    cands = candidates(run, rng)
    rng.shuffle(cands)  # random tie-break among equally unavailable combos
    scored = sorted(({"atoms": list(c), "unavail": round(-avail(c), 4)} for c in cands),
                    key=lambda c: -c["unavail"])
    # Stratify: equal picks from the 3 most-unavailable quartiles. Taking only the very top makes every
    # pool item tie on unavail (all non-default atoms), so beta in `fuse` would have nothing to trade.
    q = max(len(scored) // 4, 1)
    strata = [scored[:q], scored[q:2 * q], scored[2 * q:3 * q]]
    picked, ids = [], anchor_ids(run)
    for i, s in enumerate(strata):
        want = pool // 3 + (1 if i < pool % 3 else 0)
        picked += diverse_top([c for c in s if c not in picked], want, ids, max_shared)
    run["pool"] = sorted(picked, key=lambda c: -c["unavail"])
    return run


def z(xs):
    m = sum(xs) / len(xs)
    sd = (sum((x - m) ** 2 for x in xs) / len(xs)) ** 0.5 or 1.0
    return [(x - m) / sd for x in xs]


def fuse(run, beta=0.6, top=8):
    pool = [c for c in run["pool"] if c.get("coherence") is not None]
    if not pool:
        sys.exit("no pool item has 'coherence' yet; run the judge first")
    pool = [c for c in pool if c["coherence"] >= 2]  # 0-1 = mechanism does not connect
    if not pool:
        sys.exit("every candidate scored below 2; widen atoms or lower ambition")
    zc, zu = z([c["coherence"] for c in pool]), z([c["unavail"] for c in pool])
    for c, a, b in zip(pool, zc, zu):
        c["fused"] = round((1 - beta) * a + beta * b, 4)
    run["shortlist"] = diverse_top(sorted(pool, key=lambda c: -c["fused"]), top, anchor_ids(run))
    return run


def diversity(ideas, ignore=()):
    ideas = [set(i) - set(ignore) for i in ideas]
    if not ideas:
        return {}
    c = Counter(a for i in ideas for a in i)
    tot = sum(c.values())
    eff = math.exp(-sum(v / tot * math.log(v / tot) for v in c.values()))
    near = sum(any(len(i & j) >= 2 for k, j in enumerate(ideas) if k != n)
               for n, i in enumerate(ideas))
    return {"ideas": len(ideas), "atoms_used": len(c), "effective_atoms": round(eff, 2),
            "near_duplicate_rate": round(near / len(ideas), 2)}


def compare(run):
    avail = availability_model(run["baseline"])
    out = {}
    for name in ("baseline", "final"):
        ideas = run.get(name) or []
        d = diversity(ideas, anchor_ids(run))
        if ideas:
            d["mean_unavail"] = round(sum(-avail(i) for i in ideas) / len(ideas), 3)
        out[name] = d
    return out


def selftest():
    run = {
        "slots": ["problem", "mechanism", "check"],
        "anchor_slots": ["problem"],
        "atoms": [
            {"id": "p1", "slot": "problem", "source": "home"},
            {"id": "p2", "slot": "problem", "source": "far"},   # excluded: anchor needs home
            {"id": "m1", "slot": "mechanism", "source": "default"},
            {"id": "m2", "slot": "mechanism", "source": "far"},
            {"id": "m3", "slot": "mechanism", "source": "mutation"},
            {"id": "c1", "slot": "check", "source": "default"},
            {"id": "c2", "slot": "check", "source": "far"},
        ],
        "baseline": [["p1", "m1", "c1"]] * 5,
    }
    rank(run, pool=10)
    assert all(c["atoms"][0] == "p1" for c in run["pool"]), "anchor slot must stay home"
    assert run["pool"][-1]["atoms"] == ["p1", "m1", "c1"] or \
        ["p1", "m1", "c1"] not in [c["atoms"] for c in run["pool"][:1]], "default idea must not rank first"
    top = run["pool"][0]["atoms"]
    assert "m1" not in top and "c1" not in top, f"most unavailable should avoid defaults, got {top}"
    for i, c in enumerate(run["pool"]):
        c["coherence"] = [3, 1, 2, 3, 2, 0][i % 6]
    fuse(run, beta=0.6, top=3)
    assert all(c["coherence"] >= 2 for c in run["shortlist"])
    for a, b in itertools.combinations(run["shortlist"], 2):
        assert len(set(a["atoms"]) & set(b["atoms"]) - {"p1"}) <= 1, "shortlist must be diverse"
    run["final"] = [c["atoms"] for c in run["shortlist"]]
    r = compare(run)
    assert r["final"]["mean_unavail"] > r["baseline"]["mean_unavail"]
    print("selftest ok", json.dumps(r))


if __name__ == "__main__":
    args = sys.argv[1:]
    if not args or args[0] == "selftest":
        selftest()
        sys.exit()
    cmd, path, opts = args[0], args[1], dict(zip(args[2::2], args[3::2]))
    run = load(path)
    if cmd == "rank":
        rank(run, int(opts.get("--pool", 40)), int(opts.get("--seed", 7)), int(opts.get("--max-shared", 1)))
        print(f"pool: {len(run['pool'])} candidates")
    elif cmd == "fuse":
        fuse(run, float(opts.get("--beta", 0.6)), int(opts.get("--top", 8)))
        print(f"shortlist: {len(run['shortlist'])}")
    elif cmd == "compare":
        print(json.dumps(compare(run), indent=2))
        sys.exit()
    else:
        sys.exit(f"unknown command {cmd}")
    save(path, run)
