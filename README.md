<p align="center">
  <img src="assets/logo.svg" width="160" alt="bein logo: a grey cluster of usual ideas and one bright idea outside it">
</p>

<h1 align="center">bein</h1>

<p align="center">
  <strong>be innovative</strong><br>
  <em>An agent skill that finds ideas your AI would not normally propose, then checks they make sense.</em>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Claude%20Code-plugin-111111?style=flat-square" alt="Claude Code plugin">
  <img src="https://img.shields.io/badge/Agent%20Skills-3%20skills-111111?style=flat-square" alt="3 agent skills">
  <img src="https://img.shields.io/badge/python-stdlib%20only-111111?style=flat-square" alt="Python stdlib only">
  <img src="https://img.shields.io/badge/license-MIT-111111?style=flat-square" alt="MIT license">
</p>

---

Ask any AI for "innovative ideas" and you get the same ten ideas everyone gets. The model gives its most likely answers, and its most likely answers are the ones you have already seen.

bein turns that around. It first **measures** what the model would say by default, then searches for ideas **away** from those answers, and only then checks whether the new ideas are coherent, feasible and actually new.

## How it works

```
 your problem
      │
      ├─► Mirror ........ 3 fresh agents give the default answers (this is the "usual")
      ├─► World scan .... web search: what people already build, publish and sell
      │
      ├─► Atoms ......... ideas split into typed parts (need · mechanism · constraint · check)
      │                   plus "far" parts from other fields (biology, economics, geology...)
      ├─► Rank .......... score every combination by how unlike the defaults it is
      ├─► Known filter .. optional Jev decision model drops reworded known ideas (cheap, in bulk)
      ├─► Judge ......... a fresh agent scores coherence only, never novelty
      ├─► Feasibility ... the pack's rubric kills what can't be built
      ├─► Prior art ..... web search on the survivors; no novelty claim without a check
      │
      └─► Report ........ ideas + cheapest first experiment + diversity numbers vs the defaults
```

Three more things keep it honest over time:

- **Discard list** (`~/.bein/discarded.md`): approaches you rejected or called familiar. bein never proposes them again.
- **Gap ledger** (`~/.bein/ledger.json`): every idea that passed the prior-art check is saved with its search query. Later runs re-search it. If someone builds it, the gap was real. Over time this gives bein's **real-gap rate**, instead of trusting its own claims.
- **Coherence and novelty are kept apart.** Judges prefer familiar ideas, so they only ever score "does this make sense".

Based on *The Alien Space of Science* (Artiles et al., NeurIPS 2026, [arXiv 2603.01092](https://arxiv.org/abs/2603.01092)), which separates whether an idea is **coherent** from whether it is **available** (would the usual crowd think of it anyway).

## Install

### Claude Code

```
/plugin marketplace add tapankumarpatro/bein
/plugin install bein@bein
```

**Claude desktop app** (no `/plugin` command): Customize → the **+** by personal plugins → Create plugin / add marketplace → Add from repository → `https://github.com/tapankumarpatro/bein`.

### Any agent that reads Agent Skills (Cursor, Codex, Windsurf, OpenCode and others)

```
npx skills add tapankumarpatro/bein
```

### Manual

Copy the three folders in [`skills/`](skills/) into your agent's skills folder, for example `~/.claude/skills/`.

## Use

Just ask. The skill triggers on requests for new, non-obvious or "not the usual" ideas, or call it directly:

```
/bein what should our note-taking app do that no other note app does?
/bein-coding a different way to keep our test suite fast as it grows
/bein-design an onboarding that doesn't look like every other SaaS onboarding
```

| Skill | For | Idea parts (slots) |
|---|---|---|
| `bein` | anything: product, strategy, marketing, research | need · mechanism · constraint · check |
| `bein-coding` | architecture, algorithms, dev tooling, testing | problem · mechanism · constraint · check |
| `bein-design` | UI, UX, interaction, product and brand design | need · form · medium · interaction |

Every report shows the ideas next to the 3 most typical default ideas, plus a diversity table (bein vs default), so you can see the difference instead of taking it on trust.

## Optional: the Jev decision model (bring your own key)

bein works without any API key. With one, it adds a cheap bulk filter: the [TypeSafe](https://typesafe.ai) Jev decision model checks hundreds of candidates against everything known (default answers, world scan, discard list) and drops the reworded ones before the expensive judging step.

1. Get your own key at [typesafe.ai](https://typesafe.ai).
2. Add it **yourself** to `~/.bein/.env` (or your project's `.env`):
   ```
   TYPESAFE_API_KEY=your-key-here
   ```
3. Install the SDK: `pip install typesafe-sdk`
4. Check: `python <skill folder>/bein/scripts/jev_judge.py setup run.json`, which prints `key: found; sdk: ok`.

The key is read from your machine only. bein never asks you to paste it in chat and never prints it. Before the first paid call in a run, the agent tells you the call count and waits for your yes. A typical run is about 20 calls (a few hundred thousand input tokens, which costs cents).

Without a key, bein skips this step, says so, and still works, only less strictly.

## Good fit

bein fits any problem where **the hard part is coming up with something better than the usual answer.**

- **Product and feature ideas**: "what should our app do that no competitor does?"
- **Engineering approaches**: a different way to build, fix, scale or test something.
- **Design directions**: screens, flows or brands that don't look like every other app.
- **Strategy and positioning**: marketing angles, business models, what to build next.
- **Research directions**: candidate ideas, each with the cheapest experiment that would test it.
- **Whenever you think "I've seen all these ideas before."** That is exactly the problem it targets.

## Bad fit

- **You want the standard, proven answer.** bein pushes away from it on purpose.
- **Facts, debugging or a known fix.** There is nothing to invent.
- **Questions only a big experiment can settle**, like "will this raise the benchmark score?" or "will this drug work?" bein suggests what to try. It cannot tell you whether it works.
- **Dual-use topics** (weapons, pathogens, surveillance, intrusion). There, an unusual idea may be avoided for a good reason, and bein refuses to run.

## Limits, honestly

- **Tested on one problem so far** (improving bein itself, run twice), plus built-in self-tests. Other topics are untested.
- **Packs exist for general ideas, software and design.** Other fields (machine learning research, science, finance) run on the general pack and need their own feasibility rubric and far-field building blocks to be precise.
- **Most "far" combinations don't fit together.** In the second self-run, 23 of 60 candidates were coherent (up from 12 of 58 in the first). bein starts with a big pool so the judge can find the few that work.
- **Jev is only used for "is this already known?".** As a coherence judge it failed (rank correlation 0.09 with Claude judges), so bein doesn't use it for that.
- **The real-gap rate needs time.** Ledger rechecks come due 6 months after an idea is logged.
- **A run is heavy.** Several subagents and web searches take minutes, not seconds. Use it for decisions that deserve it.

## Files

```
.claude-plugin/          plugin + marketplace manifests
skills/bein/             core process (SKILL.md) and scripts
  scripts/score.py       ranking, fusing, diversity report (Python stdlib only)
  scripts/jev_judge.py   optional Jev known-idea filter (your key, your cost)
  scripts/ledger.py      gap ledger: add, recheck, real-gap rate
  discarded.md           template, copied to ~/.bein/ on first use
skills/bein-coding/      software pack: slots, far atoms, feasibility rubric
skills/bein-design/      design pack: slots, far atoms, feasibility rubric
```

Your own data (discard list, ledger, `.env`) lives in `~/.bein/` (change it with `BEIN_HOME`), so updating the plugin never wipes it.

Self-tests: `python skills/bein/scripts/score.py selftest` and `python skills/bein/scripts/ledger.py selftest`.

## License

MIT
