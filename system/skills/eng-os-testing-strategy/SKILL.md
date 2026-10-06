---
name: eng-os-testing-strategy
description: "Use when writing or reviewing tests: what unit, integration, contract, property, and AI-evaluation layers must each cover."
sources: [meso/testing-strategy.md]
globs: ["**/*test*", "**/tests/**", "**/__tests__/**", "**/*.spec.*", "**/conftest.py"]
always_apply: false
verified_platforms: [claude-code]
---

# Testing Strategy

Apply these rules when writing or reviewing tests, at whichever layer the change lands on.

## Principles

- **Explicitness over implicitness.** Behavior must be explicitly asserted; contracts must be machine-verified, not assumed; thresholds are stated, not judged case by case.
- **Validation at boundaries.** Tests validate correctness where behavior, contracts, and data cross meaningful boundaries.
- **Determinism within defined boundaries.** Tests must be reproducible; property tests use fixed seeds; AI tests check structural equivalence, not verbatim output.
- **Contracts as source of truth.** Producer/consumer schema agreements are specification artifacts, verified automatically on every build.

## Testing Rules

- **Test behavior, not implementation.** Verify what a function does; implementation can change without breaking the test.
- **Fast feedback first.** Unit tests run in milliseconds, integration in seconds. Slow tests get skipped, so keep the commit loop fast.
- **Mock at the boundary, not inside.** Mock external dependencies at the crossing point; never mock internal helpers: that hides real failures.
- **AI outputs are probabilistic; evaluate properties.** Assert structural/behavioral properties, not exact strings.
- **Run the smallest relevant scope first.** For a given change, run the tests that exercise the changed code before running the full suite; a targeted file or module run gives the same signal for that change at a fraction of the cost and latency. Run the full suite when the change is cross-cutting (shared utility, schema, contract) or before merge, and state briefly why broader coverage is needed rather than running it by default.

## Test Layers

| Layer | Scope | Key requirement |
|---|---|---|
| 1. Unit | One function/class, all dependencies mocked | Every public function has ≥1 happy-path and ≥1 failure-path test; no real network/DB/file I/O; deterministic |
| 2. Integration | Multiple components against real/containerized dependencies | Controlled boundary (no third-party calls); state reset between tests; verifies end-to-end behavior |
| 3. Contract | Producer/consumer schema agreement | Contracts registered in a shared schema store; both sides test against the same artifact; runs in CI every build |
| 4. Property/Behavioral | Invariants across generated inputs | Fixed random seed; used when an invariant is easier to state than a specific expected output |
| 5. AI Evaluation | AI pipeline outputs | Versioned fixtures (not live prod data); explicit thresholds; runs on every model/prompt change; regressions block promotion |
| 6. Load / Soak | Whole system or one service with real dependencies under production-shaped traffic | Targets from the Scale Targets; step to peak, spike to twice peak, soak for hours; pass criteria are the SLOs; runs in stage before launch and on a schedule, never first in production |

Metrics for AI evaluation (schema compliance rate, violation rate by category, output variance,
latency/token cost) are defined once in `eng-os-observability`; do not redefine them here.

### Test Pyramid

```
      [Load / Soak Tests]           — run in stage before launch, on a schedule
         [AI Evaluation]         — run on model/prompt change
        [Property Tests]         — run in CI; seed-fixed
      [Contract Tests]           — run in CI every build
    [Integration Tests]          — run in CI on branch merge
  [Unit Tests]                   — run in CI on every commit
```

Inverting the pyramid (many integration tests, few unit tests) makes the suite slow, fragile, and
expensive to maintain.

## Flaky Test Policy

A test that fails intermittently on unchanged code is quarantined the same day: moved to a
non-blocking suite with an owner and a fix-by date, never retried-until-green in the main
pipeline. Quarantined longer than two weeks: fix or delete.
- Failure mode: retry-on-failure hides real race conditions behind green builds and teaches the team to ignore red ones.

## Failure Modes

- mocking internal helpers instead of boundary dependencies hides real integration failures
- integration tests with shared mutable state produce order-dependent, non-reproducible failures
- contract assumptions not machine-verified break silently across service boundaries
- AI evaluations against exact strings fail on equivalent outputs and track model verbatim, not model quality
- property tests without a fixed random seed fail non-reproducibly in CI
- no load test against the Scale Targets, so the first real load is the launch
- flaky tests retried until green hide race conditions and erode trust in red builds

## Definition of Done

- [ ] Every public function has at least one happy-path and one failure-path unit test
- [ ] Unit tests mock only at the external boundary and make no real network calls
- [ ] Integration tests use real components in a controlled, reset environment
- [ ] Producer/consumer schema contracts are machine-verified in CI
- [ ] AI evaluation asserts structural and behavioral properties with explicit thresholds
- [ ] The test suite runs in CI on every commit with a defined pass/fail gate
- [ ] The smallest relevant test scope was run first for this change; a full-suite run (if done) has a stated reason
- [ ] Load, spike, and soak tests ran in stage against the Scale Targets before launch and run on a schedule, with SLO-based pass criteria
- [ ] Flaky tests are quarantined to a non-blocking suite with an owner and fix-by date; no retry-until-green in the main pipeline

For a worked example, see `references/example.md`.
