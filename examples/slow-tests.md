# Example: a 25-minute test suite nobody runs locally

**Ask:** Our test suite takes 25 minutes in CI as the codebase grows, and developers stopped running it locally before pushing.

Real run on 2026-11-23 with the `bein-coding` pack, no Jev key. Full data: [slow-tests/run.json](slow-tests/run.json).

## What Claude usually says

One fresh agent got only the problem and the slot names (no mention of novelty) and returned 15 ideas:

1. Test impact analysis: run only tests the diff touches
2. Parallel shards balanced by past runtime
3. Fast smoke set in a pre-push hook
4. Profile and fix the slowest 20 tests
5. Fakes for network and sleep calls
6. Reuse fixtures, one database per worker
7. Cache dependencies and build outputs
8. Quarantine flaky tests
9. Test-pyramid time budget per tier
10. Watch mode for local runs
11. Fail fast, run recently failed tests first
12. Merge queue with batched full runs
13. Bigger runners and in-process parallelism
14. Delete redundant tests found by mutation testing
15. Suite-time dashboard and a runtime check on PRs

A web scan found these are the standard playbook: Anthropic's test-impact service, CircleCI, Datadog Intelligent Test Runner, Bazel remote cache, Meta's predictive test selection.

## What bein returned

40 candidates were ranked away from those answers. Two judges scored coherence (they agreed within 1 point on all 40, and 14 averaged 2 or more). After fusing, the top 3 went to a prior-art search.

### 1. The team covers the suite together
*Herd sampling (epidemiology).*
Every push runs a different random slice of the suite locally, sized to finish in a minute or two. Each result is signed with the exact source-tree hash, so CI can count it. Across the team's pushes, the whole suite is covered every few hours, and the nightly full run measures what the slices missed.
**Prior art:** no tool found that pools local random slices into team coverage. Closest: CI sharding (Buildkite), which splits work across CI workers rather than people. *Logged in the gap ledger.*

### 2. A thermostat for suite time
*Homeostasis (biology): a setpoint plus negative feedback.*
Set a target suite time. When it is exceeded, the slowest tests that rarely fail (from failure history, no coverage map) move to nightly automatically, and move back if they start catching bugs.
**Prior art:** close cousin. The building blocks exist: Trunk's slow-test monitor flags tests, Shopify's test budget prioritises within a time limit, and Solr moved slow tests to nightly by hand. No tool closes the loop on its own.

### 3. CI runs only what you didn't
*Inversion of where tests run.*
CI skips tests the developer already passed locally on the identical tree, verified by a signature, and re-runs a random sample of the skipped ones to measure escapes.
**Prior art:** already exists as prooft, git-notes attestations and "Verified" commit trailers. bein marks it as known rather than claiming it, which is the point of the prior-art step.

## Numbers

| | Claude's usual ideas | bein |
|---|---|---|
| distance from the usual answers (higher = further) | 3.33 | 4.97 |
| near-duplicate rate | 0.40 | 0.00 |
