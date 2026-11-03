# AI generated from scripts.md; do not edit by hand.
import argparse, re, json, subprocess, sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

def default_repo():
    m = re.search(r"github\.com/([\w.-]+)/([\w.-]+)", (ROOT / "REPO.md").read_text())
    return f"{m[1]}/{m[2]}"

MAX_DIFF = 150_000

OUTPUT_FORMAT = """Return ONLY a JSON object, no prose, no code fences:
{"pr": <number>, "overall": <integer 1-5>, "comments": [{"sentiment": <integer 1-5>, "text": "<comment>"}, ...], "effort": {"author_minutes": <integer>, "review_minutes": <integer>}}
"""

def ignored(author, title):
    """True if REPO.md lists this author or a part of this title as ignored."""
    items, section = {}, None
    for line in (ROOT / "REPO.md").read_text().splitlines():
        if line.startswith("## "):
            section = line[3:].strip().lower()
        elif section and line.startswith("- "):
            items.setdefault(section, []).append(line[2:].strip().lower())
    return (author.lower() in items.get("ignored authors", [])
            or any(t in title.lower() for t in items.get("ignored titles", [])))


def examples():
    out = ""
    for f in sorted((ROOT / "learning").glob("*.md")):
        out += f"## {f.stem}\n{f.read_text()}\n"
    return f"# Examples\n{out}" if out else ""


def build_prompt(d):
    meta = (d / "meta.json").read_text()
    commits = (d / "commits.json").read_text()
    diff = (d / "diff.patch").read_text()
    if len(diff) > MAX_DIFF:
        diff = diff[:MAX_DIFF] + "\n[diff truncated]"
    return (f"{(ROOT/'prompt.md').read_text()}\n{OUTPUT_FORMAT}\n# Guidelines\n{(ROOT/'guidelines.md').read_text()}\n"
            f"# Rubric\n{(ROOT/'rubric.md').read_text()}\n{examples()}"
            f"# PR meta\n{meta}\n# Commits\n{commits}\n# Diff\n{diff}\n")


def grade(d, out):
    dest = out / f"{d.name}.json"
    if dest.exists():
        return
    meta = json.loads((d / "meta.json").read_text())
    if ignored(meta["author"], meta["title"]):
        return
    r = subprocess.run(["claude", "-p", "--model", "sonnet", "--tools", "",
                        "--no-session-persistence"],
                       input=build_prompt(d), capture_output=True, text=True)
    txt = r.stdout.strip()
    try:
        res = json.loads(txt[txt.index("{"):txt.rindex("}") + 1])
    except ValueError:
        print(f"PR {d.name}: bad output: {txt[:200]} {r.stderr[:200]}", file=sys.stderr)
        return
    dest.write_text(json.dumps(res, indent=2))
    print("graded", d.name)


def main():
    p = argparse.ArgumentParser(color=False)
    p.add_argument("--repo", default=default_repo().replace("/", "_"))
    p.add_argument("--run-id", required=True)
    p.add_argument("-j", type=int, default=4)
    p.add_argument("--pr", type=int, action="append")
    a = p.parse_args()
    out = ROOT / "results" / a.run_id
    out.mkdir(parents=True, exist_ok=True)
    base = ROOT / "data" / a.repo
    sel = base / "selected.json"
    dirs = (sorted(base / "prs" / n for n in json.loads(sel.read_text()))
            if sel.exists() else sorted((base / "prs").iterdir()))
    if a.pr:
        dirs = [base / "prs" / str(n) for n in a.pr]
    with ThreadPoolExecutor(a.j) as ex:
        list(ex.map(lambda d: grade(d, out), dirs))


main()
