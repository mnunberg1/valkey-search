# Contributing to valkey-search

Welcome, and thank you for your interest in contributing!

## Get started

- **Questions?** Open a [GitHub Discussion](https://github.com/valkey-io/valkey-search/discussions) or join the [Valkey Slack](https://join.slack.com/t/valkey-oss-developer/shared_invite/zt-2nxs51chx-EB9hu9Qdch3GMfRcztTSkQ).
- **Found a bug?** [Open a bug report](https://github.com/valkey-io/valkey-search/issues/new?template=bug_report.md&title=%5BBUG%5D).
- **Have a feature idea?** [Open a feature request](https://github.com/valkey-io/valkey-search/issues/new?template=feature_request.md&title=%5BFEATURE%5D).

## Developer Certificate of Origin (DCO)

All commits must include a `Signed-off-by` line. This is how you certify that you authored the contribution and have the right to submit it under the project's license.

Add it automatically with the `-s` flag:

```bash
git commit -s -m "your commit message"
```

A signed commit looks like:

```
Signed-off-by: Jane Smith <jane@example.com>
```

PRs with unsigned commits will be blocked by the DCO check.

## How to contribute

1. **For significant changes**, open an issue first to discuss the approach before writing code.
2. Fork the repository and create a topic branch off `main`.
3. Make your changes and commit with a DCO sign-off (`git commit -s`).
4. Push your branch and open a pull request against `valkey-io/valkey-search:main`.
5. Address any CI failures and review feedback. All CI checks must pass before merging.

To link your PR to an existing issue, include `Fixes #<issue-number>` or `Resolves #<issue-number>` in the PR description.

## Finding issues to work on

- Issues labeled [**`good first issue`**](https://github.com/valkey-io/valkey-search/labels/good%20first%20issue) are explicitly flagged as good entry points for new contributors.
- Issues labeled [**`help wanted`**](https://github.com/valkey-io/valkey-search/labels/help%20wanted) are higher-priority items where extra community involvement is welcome.
- Before starting work on an issue, leave a comment expressing your intent — this avoids duplicate effort.

## Slash commands

Collaborators can use the following commands in PR and issue comments to help do some trivial tasks.

| Command | Where | What it does |
|---|---|---|
| `/label <name>` | PR or issue | Applies a label from the repo's defined label set. Rejects unknown labels; no-ops if already applied. |
| `/reviewer <username>` | PR only | Requests a review from the specified GitHub user. The user must be a repo collaborator. |
| `/resolves <issue-number>` | PR only | Appends `Resolves #<N>` to the PR body, linking the issue and auto-closing it on merge. |
| `/rerun` | PR only | Re-runs all failed or timed-out CI jobs for the PR's current head commit. |
| `/ai off <reason>` | PR only | Silences every AI reviewer on the PR by applying the `no-ai-review` label. Reason required. |
| `/ai on` | PR only | Re-enables AI review. |
| `/ai fold` | PR only | Collapses superseded AI review comments immediately. |
| `/ai status` | PR only | Posts one digest of open AI findings across all reviewers. |

**Example usage:**

```
/label bug
/reviewer allenss-amazon
/resolves 925
/rerun
/ai off rebasing, will re-request review when settled
```

## AI code review

This repository runs AI reviewers alongside CI. They are configured for low
volume: they report defects with a concrete reproducer and stay out of
anything `clang-format`, `clang-tidy`, or the sanitisers already decide.

Two rules are enforced automatically:

1. An AI review is never an approval — a human must approve.
2. Every unresolved AI finding needs a human reply or a resolve. You do not
   have to agree with it; replying "not a bug, because ..." and resolving the
   thread is a complete answer. The point is that dismissing a machine's
   claim should be a deliberate act rather than scrolling past it.

See [docs/ai-review-policy.md](docs/ai-review-policy.md) for the full set of
controls and how to tune them.

## Code of conduct

This project follows the [Valkey community code of conduct](https://github.com/valkey-io/valkey/blob/unstable/CODE_OF_CONDUCT.md).

## License

See [LICENSE](LICENSE) for the project's licensing. By contributing, you agree your contributions will be licensed under the same terms.
