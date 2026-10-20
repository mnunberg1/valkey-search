# BugBot review guidance

This repository is a C++20 Valkey module. It is loaded into the Valkey server
process, so a defect here can take down the server.

## Report

- Memory errors: use-after-free, double free, leaks, out-of-bounds access.
- Lifetime and ownership mistakes, including objects that outlive their arena.
- Data races and lock-order inversions between command execution, keyspace
  notification handlers, and background index threads.
- Dropped `absl::Status` / unchecked `StatusOr`.
- Integer overflow or truncation in size and offset arithmetic.

Every finding must name the input, call order, or thread interleaving that
triggers it. If you cannot name one, do not report it.

## Do not report

- Formatting, naming, include order, `const` placement. `.clang-format` and
  `.clang-tidy` run in CI and are authoritative.
- Missing tests or missing comments as a standalone finding.
- Idiom preferences (raw loop vs. algorithm, etc.).
- Anything under `submodules/`, `third_party/`, `debs/`, or generated `*.pb.*`.

## Form

Two sentences maximum per finding: the consequence first, then the trigger.
