# Review rules (repository-wide)

These rules are additive: Greptile collects every `.greptile/rules.md` from the
repository root down to the directory of each changed file.

## What to report

Report a finding only when you can name the **trigger** — a concrete input,
call order, or thread interleaving that produces the wrong result. A comment
that says code "could" or "may" misbehave, without that path, is noise and
must not be posted.

Priority order:

1. Memory errors — use-after-free, double free, leaks, out-of-bounds.
2. Lifetime and ownership — dangling references, unclear transfer of ownership,
   objects outliving the allocator or arena they came from.
3. Concurrency — data races, lock-order inversion, missing synchronisation on
   state shared between the main thread and worker threads.
4. Error handling — a dropped `absl::Status`, a `StatusOr` unwrapped without
   checking, an error path that leaves an index or schema half-updated.
5. Integer overflow, truncation, and signed/unsigned mixups in size and offset
   arithmetic.

## What never to report

- Formatting, naming, include order, `const` placement, brace style.
  `.clang-format` and `.clang-tidy` run in CI and their output is the
  authoritative answer. Duplicating them wastes the reviewer's attention.
- Requests for more tests or more comments as a standalone finding.
- Replacing a raw loop with an algorithm, or other idiom preferences.
- Restating what the diff does.

## Form

One or two sentences. Lead with the consequence, then the trigger. For example:

> Leaks the index on the early return when `schema_name` is empty: the
> `unique_ptr` is released on line 112 but only re-owned on the success path.

Not:

> It might be worth considering whether this allocation is handled correctly
> in all cases, as there may be a path where the resource is not released...
