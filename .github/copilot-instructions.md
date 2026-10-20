# Copilot code review instructions

Repository-wide guidance for GitHub Copilot code review.
Path-scoped rules live in `.github/instructions/*.instructions.md`.

This is a C++20 Valkey module loaded into the Valkey server process.

## Review for

1. Memory errors — use-after-free, double free, leaks, out-of-bounds.
2. Lifetime and ownership mistakes.
3. Data races and lock-order inversions.
4. Dropped `absl::Status` or unchecked `StatusOr`.
5. Integer overflow and truncation in size/offset arithmetic.

## Do not comment on

- Formatting, naming, include order, or `const` placement. `.clang-format` and
  `.clang-tidy` run in CI and their output is authoritative; repeating them
  costs the reviewer attention and changes nothing.
- Missing tests or docs as a standalone finding.
- Code under `submodules/`, `third_party/`, `debs/`, or generated `*.pb.*`.

## Form

State the consequence, then the input or call order that triggers it. Two
sentences maximum. If you cannot name a trigger, do not raise the comment.
