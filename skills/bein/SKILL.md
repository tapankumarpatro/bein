---
name: bein
description: Be innovative. Finds ideas that make sense but that Claude (and the crowd it learned from) would not normally propose. It measures Claude's own default answers, then searches combinations of typed idea atoms that avoid them, judges only the survivors, checks feasibility and prior art, and reports bein vs default diversity. Use when the user asks for a genuinely new, non-obvious, innovative or "not the usual" idea, approach, feature or direction, or says /bein. Category packs, bein-coding and bein-design, add slot grammars and far-domain atom banks.
---

# bein: be innovative

Based on "The Alien Space of Science" (Artiles et al., NeurIPS 2026, arXiv 2603.01092). That paper splits two things people mix up: is an idea **coherent**, and is it **available**, meaning would the usual crowd think of it anyway. LLMs are good at the first and stuck in the second. bein keeps that split, with no training and no corpus:

- **Typed slots** replace flat atoms. An idea is one atom per slot (for example problem · mechanism · constraint · check), so combinations are structurally sound by construction.
- **Availability is measured, not guessed.** Fresh agents give Claude's default answers, and `scripts/score.py` scores each combination by its smoothed likelihood under those answers. The obvious answer scores high and gets penalised.
- **Far atoms and mutations** add building blocks that no default answer contains, which fixes the paper's "it can only recombine" limit.
- **The judge scores coherence only, and only near the end.** The script prunes first, and judges never score novelty, because judges prefer the familiar.
- **Feasibility and prior art come before any write-up.** Atoms are pinned during write-up so ideas cannot drift back to the default.

Do not use bein when the user wants the standard, proven answer. Do not run it on dual-use domains (weapons, pathogens, surveillance, intrusion), because low availability there can mean "avoided for good reason".

## Setup (once per machine)

`<bein>` below means this skill's base directory. bein keeps its memory (discard list, gap ledger, optional `.env`) in `~/.bein/` (override with `BEIN_HOME`), so updating the skill never wipes it.

bein uses the Jev decision model (TypeSafe) as a cheap bulk filter. Run `python <bein>/scripts/jev_judge.py setup run.json` (any run.json works). It reports:
- **key:** it reads `TYPESAFE_API_KEY` (or `JEV_API_KEY`) from the environment, the nearest `.env` above the working folder, or `~/.bein/.env`. If missing, tell the user to get a key at https://typesafe.ai and add the line `TYPESAFE_API_KEY=...` to `~/.bein/.env` themselves. Never ask them to paste it in chat, and never print it.
- **sdk:** if missing, `pip install typesafe-sdk` (in the project venv if one exists).

Jev calls are paid but cheap (about $0.04 per million input tokens). Before the first paid call in a run, tell the user the call count from `--dry-run` and get a yes. Without a key, skip the Jev steps and say so; bein still works, only less strictly.

**Discard list:** `~/.bein/discarded.md` holds approaches bein must never generate again. Read it at step 3 and step 9.

**Gap ledger:** `~/.bein/ledger.json`, managed by `<bein>/scripts/ledger.py`. Every idea bein reports claims a gap. The ledger stores that claim with a date and rechecks it later, so over time bein learns its real-gap rate instead of trusting its own novelty claims.

## Steps

Work in a run folder: the scratchpad if one exists, otherwise `.bein/<slug>/`. Keep everything in `run.json`, whose schema is in the `scripts/score.py` docstring.

**0a. Recheck due gaps.** Run `python <bein>/scripts/ledger.py due`. For each due entry (at most 5 per run), web search its query and mark it:
- `filled`: someone has built or published it since. The gap was real. The script also adds it to `discarded.md`.
- `open`: still nothing. It comes due again in 6 months.
- `dead`: it already existed before bein claimed it, or the search shows nobody wants it.

Report the ledger stats line in the final report, including `real_gap_rate`.

**0. Load the pack.** If the ask is about code or software, follow `bein-coding`. If it is about UI, UX, visual, product or brand design, follow `bein-design`. A pack gives `slots`, `anchor_slots`, a far-atom bank and a feasibility rubric. With no pack, use the slots `need · mechanism · constraint · check` and anchor `need`.

**1. Frame.** Write the problem in one sentence. Read the real context (the code, the brief, the design system) and write **home** atoms from it. The anchor slot holds only home atoms, because every idea must solve *this* user's problem. Put **one** need in the anchor slot per run. Several needs get paired with mechanisms at random, and the judge rejects most of those pairings (in the self-test, 47 of 60 scored 1). For several needs, run once per need.

**1b. World scan (what people already do).** The mirror only shows what Claude would say. Ideas can also be familiar because people already do them. Research the user's topic on the web: run 4–6 searches covering recent papers, GitHub repos, products, and practitioner posts or forums, and read the best 5–10 results. Write 30–100 one-line existing approaches into `run.json["world"]` (plain strings), each with its source. Any concept that also fits a slot becomes a `default` atom at step 3. Report the scan in one line. Do this after the mirror agents have been started, so it cannot leak into them.

**2. Mirror (measure the default).** Spawn 3 fresh subagents. Give each only the one-sentence problem and the slot names, with no mention of bein, novelty or far domains, and ask for 10 ideas as one line each. These 30 ideas are the measurement, so do not contaminate them. For a quick run, use 1 agent and 15 ideas.

**3. Atoms.** Each atom is one self-contained sentence that says what it does and why it works, with no dangling references. Per slot:
- `home`: from the context.
- `default`: every concept the mirror ideas used. Add as many as needed so **every mirror idea can be tagged** with atom ids.
- `far`: 6–10 from the pack's bank, chosen because their *structure* fits the slot, from at least 3 different domains.
- `mutation`: 2–3 that invert, push to an extreme, or change the scale of a default atom.

Then tag each mirror idea to atom ids and write it into `baseline`.

Before writing `far` and `mutation` atoms, read `discarded.md`. Never write an atom that restates a discarded approach.

**4. Rank, then filter in bulk.**
- With Jev: `score.py rank run.json --pool 400 --max-shared 2`, then `jev_judge.py known run.json --keep 60`. Jev compares each candidate with every known idea (mirror + world + discard list) and keeps the 60 least known. That is about 20 calls.
- Without Jev: `score.py rank run.json --pool 40`.

Ranking draws evenly from the three least-available quarters, so β has something to trade. Most cells in the gap are empty because the parts do not fit together (in the self-test, only 12 of 58 did), so start with a big pool and let the judge find the few that fit.

**5. Judge coherence.** Spawn one fresh subagent. Give it the atom texts of each pool candidate and this rubric, nothing else:
> Score 0–3: can ONE concrete mechanism make all these atoms work together on the problem? 0 = no link, 1 = forced or wordplay, 2 = plausible link you can state, 3 = tight link where each atom needs the others. Name the link in one line. Do NOT reward novelty or familiarity.

Write `coherence` (and `link`) into each pool item. A single judge is noisy: in the first test, the same idea scored 3 in one run and 2 in the next. Use 2 judges and average their scores whenever the shortlist matters.

Claude judges coherence, not Jev. In the 2026-11-23 test, Jev's coherence scores had a rank correlation of 0.09 with two Claude judges. Jev is only good at "is this already known?".

**6. Fuse.** Run `python <bein>/scripts/score.py fuse run.json --beta 0.6 --top 8`. Candidates scored 0–1 are dropped. β trades coherence against unavailability (the paper used 0.7). Raise it for wilder ideas, lower it for safer ones.

**7. Feasibility, before writing anything up.** Apply the pack's feasibility rubric to the 8 shortlisted ideas. Kill or keep each one, with a reason.

**8. Prior art.** Web search the top ≤5 survivors. If an idea plainly exists, either drop it or mark it "known in X, new here" when moving it across domains is the point. Never claim novelty you did not check.

**9. Write up and pin.** For each survivor give:
- a title
- the one-line link
- how each atom carries weight
- the cheapest first experiment
- the main risk

Drop any survivor that matches a line in `discarded.md`. Then run the **pin check**: if you can delete an atom and the idea still stands, or the idea now reads like a mirror idea, rewrite it or drop it.

**10. Report.** Put the surviving atom lists in `final`, then run `python <bein>/scripts/score.py compare run.json`. Show the diversity table (bein vs default) and the 3 most typical mirror ideas for contrast, then the ideas. Report weak numbers as they are. Afterwards, add each idea the user rejects or calls familiar to `discarded.md`, with the reason and date.

Then record every reported idea whose prior-art check found nothing: `ledger.py add "title" "search query"`. Use the concept-level query that came back empty at step 8, so the recheck repeats the same search. Skip ideas marked "known in X, new here", since their gap is only the move across domains.

Self-test: `python <bein>/scripts/score.py selftest`.
