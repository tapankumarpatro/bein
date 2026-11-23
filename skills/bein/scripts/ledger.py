"""bein gap ledger. Python 3 stdlib only.

Every reported idea claims a gap: "nobody has built this yet". The ledger records that claim
with a date and a search query, and later checks whether someone filled the gap.
A filled gap means bein found a real gap (just early). A gap that stays empty for long
may mean nobody wants it. Over many runs this gives bein's real-gap rate.

  python ledger.py add  "title" "search query" [--months 6]   record a claimed gap
  python ledger.py due                                         open gaps due for a recheck, plus stats
  python ledger.py mark ID filled "evidence url or note"       someone built it -> also added to discarded.md
  python ledger.py mark ID open   "what the search found"      still empty -> due again in 6 months
  python ledger.py mark ID dead   "why"                        gap was never real (existed already, or no one wants it)
  python ledger.py selftest

File: ~/.bein/ledger.json (override the folder with BEIN_HOME).
"""
import datetime, json, os, pathlib, sys, tempfile

HERE = pathlib.Path(__file__).resolve().parent
HOME = pathlib.Path(os.getenv("BEIN_HOME", pathlib.Path.home() / ".bein"))


def user_file(name):
    """bein's memory lives in ~/.bein so a skill update never wipes it; seeded from the shipped template."""
    HOME.mkdir(parents=True, exist_ok=True)
    f, tpl = HOME / name, HERE.parent / name
    if not f.exists() and tpl.exists():
        f.write_text(tpl.read_text(encoding="utf-8"), encoding="utf-8")
    return f
LEDGER = HOME / "ledger.json"
DISCARDED = user_file("discarded.md")


def today():
    return datetime.date.today()


def later(months, start=None):
    d = start or today()
    return (d + datetime.timedelta(days=round(30.44 * months))).isoformat()


def load():
    return json.loads(LEDGER.read_text(encoding="utf-8")) if LEDGER.is_file() else []


def save(rows):
    LEDGER.write_text(json.dumps(rows, indent=1, ensure_ascii=False), encoding="utf-8")


def add(title, query, months=6):
    rows = load()
    row = {"id": max((r["id"] for r in rows), default=0) + 1, "title": title, "query": query,
           "added": today().isoformat(), "due": later(months), "status": "open", "checks": []}
    rows.append(row)
    save(rows)
    return row


def due(now=None):
    now = (now or today()).isoformat()
    rows = load()
    stats = {s: sum(r["status"] == s for r in rows) for s in ("open", "filled", "dead")}
    closed = stats["filled"] + stats["dead"]
    stats["real_gap_rate"] = round(stats["filled"] / closed, 2) if closed else None
    return [r for r in rows if r["status"] == "open" and r["due"] <= now], stats


def mark(rid, status, note):
    assert status in ("filled", "open", "dead"), status
    rows = load()
    row = next(r for r in rows if r["id"] == rid)
    row["checks"].append({"date": today().isoformat(), "status": status, "note": note})
    row["status"] = status
    if status == "open":
        row["due"] = later(6)
    save(rows)
    if status == "filled":  # now it exists, so bein must not propose it again
        with DISCARDED.open("a", encoding="utf-8") as f:
            f.write(f"- {row['title']} — gap filled: {note} ({today().isoformat()})\n")
    return row


def selftest():
    global LEDGER, DISCARDED
    tmp = pathlib.Path(tempfile.mkdtemp())
    LEDGER, DISCARDED = tmp / "l.json", tmp / "d.md"
    a = add("Idea A", "query a", months=0)
    b = add("Idea B", "query b", months=6)
    rows, stats = due()
    assert [r["id"] for r in rows] == [a["id"]], "only the past-due gap is due"
    mark(a["id"], "filled", "https://example.com/a")
    assert "Idea A" in DISCARDED.read_text(encoding="utf-8"), "filled gap goes to the discard list"
    mark(b["id"], "dead", "existed already")
    rows, stats = due(datetime.date(2100, 1, 1))
    assert rows == [] and stats["real_gap_rate"] == 0.5, stats
    print("selftest ok", stats)


if __name__ == "__main__":
    a = sys.argv[1:]
    if not a or a[0] == "selftest":
        selftest()
    elif a[0] == "add":
        months = float(a[a.index("--months") + 1]) if "--months" in a else 6
        print(json.dumps(add(a[1], a[2], months), ensure_ascii=False))
    elif a[0] == "due":
        rows, stats = due()
        for r in rows:
            print(f"{r['id']}. {r['title']} | search: {r['query']} | added {r['added']}")
        print(f"{len(rows)} due; ledger: {json.dumps(stats)}")
    elif a[0] == "mark":
        print(json.dumps(mark(int(a[1]), a[2], a[3]), ensure_ascii=False))
    else:
        sys.exit(f"unknown command {a[0]}")
