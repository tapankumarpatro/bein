---
name: bein-coding
description: bein pack for software. Finds non-obvious but sound engineering approaches (architecture, algorithms, features, dev tooling, testing strategies) by searching away from Claude's default answers. Use when the user wants an innovative, unusual or "not the standard" way to build, fix, scale, test or design code or a system, or says /bein-coding.
---

# bein-coding

Run the full process of the `bein` skill (its `SKILL.md` sits in the sibling folder `../bein/`) using this pack.

## Slot grammar

```json
"slots": ["problem", "mechanism", "constraint", "check"],
"anchor_slots": ["problem"]
```

| Slot | Holds | Home atoms come from |
|---|---|---|
| problem | the concrete pain, in this codebase | the files, issues and logs you read |
| mechanism | how it works: a pattern, algorithm or structure | the current design, plus the far bank |
| constraint | a rule the solution must obey and that shapes it | real limits (budget, latency, team), plus far or mutated ones |
| check | how we will know it works | the existing tests or CI, plus the far bank |

The constraint slot is where mutation pays off most. For example, "must be fully reversible", "no new service" or "works offline" each force a different mechanism.

## Far atoms

Pick from `references/far-atoms.md`. Choose on **structural fit** (does the shape of the mechanism match the shape of the problem?), never on surface words.

## Feasibility rubric (step 7)

Kill an idea if any answer is "no":
1. Can a first slice ship in **≤2 days** in this codebase, with no rewrite?
2. Does it use only the stack's existing languages and runtimes, or one small, well-known dependency?
3. Is the failure mode safe: does it fail closed, can it be rolled back, and does it lose no data?
4. Can the check slot actually run in CI or locally?
5. Does it respect this project's hard rules (read CLAUDE.md)?

Also note the cost (compute, money, review time) and the hardest unknown.
