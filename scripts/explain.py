# AI generated from scripts.md; do not edit by hand.
import argparse, json, re, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MAX_DIFF = 150_000

DEFAULT_QUESTION = (
    "Explain why you gave this overall rating and each comment. Quote the "
    "rubric or guideline text you relied on, and say where it was ambiguous.")

PREFIX = (
    "You previously reviewed the pull request below. Answer the question at the "
    "end in plain text, not JSON. The length limits in the grading prompt apply "
    "to the grade, not to this answer. Be honest if the rubric is ambiguous or "
    "you would now weigh something differently.\n")


def default_repo():
    m = re.search(r"github\.com/([\w.-]+)/([\w.-]+)", (ROOT / "REPO.md").read_text())
    return f"{m[1]}/{m[2]}"


def examples():
    out = ""
    for f in sorted((ROOT / "learning").glob("*.md")):
        out += f"## {f.stem}\n{f.read_text()}\n"
    return f"# Examples\n{out}" if out else ""


def build_prompt(d, answer, question):
    diff = (d / "diff.patch").read_text()
    if len(diff) > MAX_DIFF:
        diff = diff[:MAX_DIFF] + "\n[diff truncated]"
    return (f"{PREFIX}\n# Grading prompt you were given\n{(ROOT/'prompt.md').read_text()}\n"
            f"# Guidelines\n{(ROOT/'guidelines.md').read_text()}\n"
            f"# Rubric\n{(ROOT/'rubric.md').read_text()}\n{examples()}"
            f"# PR meta\n{(d/'meta.json').read_text()}\n"
            f"# Commits\n{(d/'commits.json').read_text()}\n# Diff\n{diff}\n"
            f"# Your previous answer\n{answer}\n# Question\n{question}\n")


def main():
    p = argparse.ArgumentParser(color=False)
    p.add_argument("run_id")
    p.add_argument("pr", type=int)
    p.add_argument("question", nargs="?", default=DEFAULT_QUESTION)
    p.add_argument("--repo", default=default_repo().replace("/", "_"))
    a = p.parse_args()
    d = ROOT / "data" / a.repo / "prs" / str(a.pr)
    answer = (ROOT / "results" / a.run_id / f"{a.pr}.json").read_text()
    r = subprocess.run(["claude", "-p", "--model", "sonnet", "--tools", "",
                        "--no-session-persistence"],
                       input=build_prompt(d, answer, a.question),
                       capture_output=True, text=True)
    if r.returncode:
        sys.exit(r.stderr)
    print(r.stdout.strip())


main()
