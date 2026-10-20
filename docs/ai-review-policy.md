# Controlling AI code review

How this repository keeps AI reviewers useful instead of exhausting, and what
levers exist if the current settings are still wrong.

Every AI reviewer has the same failure mode: it is cheap to generate a comment
and expensive to read one, so the default settings optimise for the vendor's
demo rather than your attention. The fix is not to turn them off. It is to make
them answer one question — *what is broken, and what input breaks it* — and to
make everything else impossible to say.

## The four control planes

| Plane | Where it lives | Works on | Strength |
|---|---|---|---|
| 1. Vendor config | `.coderabbit.yaml`, `.greptile/`, `.pr_agent.toml`, `.cursor/`, `.github/copilot-instructions.md` | one vendor each | Strong but per-vendor; the knobs differ wildly |
| 2. Runtime control | labels, `/ai` commands, vendor `@mentions` | per PR | Immediate, no merge needed |
| 3. Repo enforcement | `.github/workflows/ai-*.yml` | **every** vendor, incl. future ones | Strongest: works on bots that expose no config at all |
| 4. Policy | this file, branch protection | humans | The only plane that governs *what AI output is allowed to mean* |

Plane 3 is the one most teams skip, and it is the one that scales: it needs no
cooperation from the vendor.

## Plane 1 — vendor knobs

### CodeRabbit (`.coderabbit.yaml`)

The three settings that matter most, in order:

| Knob | Set to | Why |
|---|---|---|
| `reviews.profile` | `quiet` | `quiet` \| `chill` (default) \| `assertive`. `quiet` posts only the most important inline comments and groups the rest into the summary. One line, biggest effect. |
| `tone_instructions` | terse directive, ≤250 chars | Controls the *shape* of every comment. The length cap is real — spend it on "no praise, no restating the diff". |
| `reviews.auto_review.auto_pause_after_reviewed_commits` | `3` | Stops the pile-up where a 20-commit PR accrues 20 review passes. Re-arm with `@coderabbitai review`. |

Then switch off the ceremony. Each is a separate boolean, and they default to
**on**: `changed_files_summary`, `sequence_diagrams`, `estimate_code_review_effort`,
`assess_linked_issues`, `related_issues`, `related_prs`, `suggested_labels`,
`suggested_reviewers`, `in_progress_fortune`, `review_status`, `review_info`,
`enable_prompt_for_ai_agents`. `poem` defaults to off; leave it there.

`collapse_walkthrough: true` wraps the walkthrough in a `<details>` block —
native folding, no automation required.

`reviews.path_instructions` is the precision tool: per-glob instructions, up to
20 000 chars each. Use it to say *"clang-tidy owns this, you do not"*, which is
how you stop a reviewer duplicating your linter.

### Greptile (`.greptile/`)

Prefer the `.greptile/` folder over `greptile.json`. **If both exist in the same
directory, `.greptile/` wins and `greptile.json` is ignored entirely** — so do
not split settings across the two.

| Knob | Set to | Why |
|---|---|---|
| `strictness` | `3` | **Higher means fewer comments.** 1 = comments on everything, 2 = default, 3 = only the most critical. Easy to get backwards. |
| `commentTypes` | `["logic"]` | Array *replaces* the default `["logic","syntax","style"]`. Dropping `style` removes formatting and naming comments wholesale. |
| `statusCheck` | `true` | Documented way to stop the "X files reviewed" comments — they become a status check instead. |
| `statusCommentsEnabled` | `false` | Suppresses the main summary comment. |

The folder cascades: Greptile collects every `.greptile/` from the repo root
down to each changed file's directory. **Settings** take the closest value and
arrays are replaced; **rules and `rules.md`** accumulate. So put global policy at
the root and domain rules in `src/.greptile/rules.md` — which is what we do —
rather than fighting the merge rules with per-directory `strictness`.

At PR level, `strictness` takes the **maximum** across configs, `commentTypes`
the **union**, and booleans OR together.

### Qodo Merge / PR-Agent (`.pr_agent.toml`)

`[pr_reviewer] num_max_findings` is a hard cap — rare and valuable; most vendors
offer no count limit. `persistent_comment = true` edits the previous review in
place rather than posting a new one per push.

Caveat: there is a known issue where `extra_instructions` is reported as applied
but is not honoured. Run `/config` on a PR to print the configuration actually
in effect.

### Cursor BugBot (`.cursor/`)

`.cursor/config/bugbot.yaml` is read from the PR's **base** branch, so changes
only take effect once merged. `.cursor/BUGBOT.md` carries the review guidance,
and nested `BUGBOT.md` files are collected walking up from each changed file.
Note that `.cursor/rules/*.mdc` editor rules do **not** apply to BugBot — review
conventions must be duplicated into `BUGBOT.md`.

Running once per PR rather than per push is the main volume lever.

### Copilot code review (`.github/`)

`.github/copilot-instructions.md` is repo-wide. Path-scoped rules go in
`.github/instructions/*.instructions.md` and **must** declare an `applyTo` glob
in frontmatter — a file without `applyTo` is silently ignored.

There is no verbosity setting. The only lever is plain-language instruction.

## Plane 2 — runtime control

### The label

`no-ai-review` is the cross-vendor off switch. CodeRabbit honours it through
`reviews.auto_review.labels: ["!no-ai-review"]` and Greptile through
`disabledLabels`. One label, both bots, no merge required.

We drive it through a uniform front-end rather than asking anyone to remember
five vendor dialects:

| Command | Effect |
|---|---|
| `/ai off <reason>` | Applies `no-ai-review`. Collaborators only, reason required. |
| `/ai on` | Removes it. |
| `/ai fold` | Collapses superseded AI comments immediately. |
| `/ai status` | One digest of open AI findings across all bots. |
| `/ai help` | The table above. |

**Why labels and not `@mentions`:** a workflow that posts `@coderabbitai pause`
mostly does not work, because most bots ignore comments authored by other bots.
Config-driven label handling is the documented path and is reliable. Vendor
commands remain available to *humans*:

| Vendor | Pause | Resume | Resolve all |
|---|---|---|---|
| CodeRabbit | `@coderabbitai pause` | `@coderabbitai resume` | `@coderabbitai resolve` |
| CodeRabbit (permanent, per PR) | `@coderabbitai ignore` **in the PR description** | remove the line | — |
| Greptile | `disabledLabels` / `autoReview: []` | `@greptileai` | — |
| BugBot | run-once setting | `bugbot run` | — |
| Qodo | — | `/review` | — |

`@coderabbitai configuration` prints the resolved config with the origin of each
value — the fastest way to find out why a setting is not taking effect.

## Plane 3 — repo-side enforcement

### Folding (`ai-fold-comments.yml`)

GitHub has a first-class mechanism for this that almost nobody uses:
the `minimizeComment` GraphQL mutation. A minimised comment collapses to a
single greyed line with a "Show comment" toggle.

```graphql
mutation($id:ID!, $classifier:ReportedContentClassifiers!) {
  minimizeComment(input:{subjectId:$id, classifier:$classifier}) {
    minimizedComment { isMinimized }
  }
}
```

`ReportedContentClassifiers` accepts `ABUSE`, `DUPLICATE`, `LOW_QUALITY`,
`OFF_TOPIC`, `OUTDATED`, `RESOLVED`, `SPAM`. We use `OUTDATED` and `RESOLVED`.
`subjectId` is a GraphQL **node ID** — REST's numeric comment id will not work,
and cannot be converted, so the ids must be read back through GraphQL.
`unminimizeComment` reverses it; nothing is destroyed.

The workflow folds two things on every push:

1. Older top-level comments from a bot, once it has posted a newer one — keeping
   exactly the latest review open per bot. This is the single biggest visual win
   on a long PR.
2. Comments in review threads already resolved or outdated.

It works on any bot in `.github/ai-review/bots.json`, including ones with no
configuration surface of their own. Add a login there and it is covered.

### The gate (`ai-review-gate.yml`)

Two rules:

1. **An AI review is not an approval.** The PR needs an approving review from a
   human who is not the author. Without this, a repo that enables
   `request_changes_workflow` can have a bot auto-approve its way to merge.
2. **Every unresolved AI finding needs a human reply**, or a resolve.

Rule 2 is the one worth arguing about, so: it does **not** require you to agree
with the bot or to fix anything. Replying "not a bug — `idx` is bounded by the
caller" and resolving the thread satisfies it completely. What it removes is the
third option, the common one: scrolling past. An unread machine claim and a
rejected machine claim look identical in a PR's history, and only one of them is
fine.

The gate reports through the Checks UI and the job summary, and posts **no**
comments. A guardrail against noise must not add noise.

Bypass with a label in `bypassLabels` (`no-ai-gate`, `release`), and say why.

## Plane 4 — verifying AI output

Configuration makes reviewers quieter. It does nothing about whether they are
*right*. Treat every AI finding as a claim with an attached burden of proof:

- **Reproducer or it did not happen.** Both the Greptile `reproducer-required`
  rule and the CodeRabbit/Copilot instructions demand a concrete input, call
  order, or thread interleaving. A finding that says code "could" or "might"
  fail, with no path, is not a finding. This cuts volume *and* raises quality,
  because speculative comments are exactly the ones that waste a reviewer's
  afternoon.
- **Let the deterministic tools win.** clang-format, clang-tidy, ASan, TSan and
  the test suite produce checkable answers. Every config here forbids the
  reviewers from duplicating them. When a bot disagrees with a sanitiser, the
  sanitiser is right.
- **A suggested patch is not a reviewed patch.** Applying a bot's suggestion
  produces code no human wrote and no human read. It goes through CI like
  anything else; `fixWithAI` and CodeRabbit's docstring/unit-test "finishing
  touches" are off here for that reason.
- **Keep the human on the hook.** DCO sign-off and rule 1 of the gate mean a
  named person certifies every merge, whatever generated the diff.

## What we deliberately did not do

- **Disable summaries.** The high-level summary is the one AI output with a good
  cost/benefit ratio on a large PR. We kept it and capped it at five bullets.
- **Set CodeRabbit's `request_changes_workflow`.** It lets the bot approve. Rule
  1 of the gate exists precisely to prevent that.
- **Use `assertive` anywhere.** If a class of defect matters, write a rule for
  it; do not buy it with a global noise increase.
- **Auto-resolve bot threads.** Folding changes presentation. Resolving asserts
  the finding was handled, which is a human judgement.

## Verified vs. assumed

Settings below were taken from each vendor's official documentation at the time
of writing. Flagged items could not be confirmed and should be checked against a
live PR before being relied on.

| Item | Status |
|---|---|
| CodeRabbit keys, defaults, `profile` enum | Verified against the official configuration reference |
| Greptile keys, `strictness` direction, `.greptile/` precedence and cascade | Verified against official docs |
| `minimizeComment` input and classifier enum | Verified |
| Qodo `num_max_findings`, `persistent_comment`, `extra_instructions` | Verified for open-source PR-Agent; the hosted service may differ |
| Qodo `[pr_description] publish_description_as_comment` | **Assumed** — confirm with `/config` |
| BugBot `.cursor/config/bugbot.yaml`, key names `runOncePerPR` / `reviewDrafts` | **Assumed.** Cursor's page is stale and some settings are dashboard-only; the dashboard wins if they disagree |
| Bot logins in `bots.json` | **Assumed.** Verify each against a real PR — a wrong login silently disables folding for that bot |

The bot logins are the most important thing to check, and the easiest: run
`/ai status` on a PR that has bot comments. Any bot missing from the table has
the wrong login in `bots.json`.
