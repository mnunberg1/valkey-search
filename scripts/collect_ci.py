# AI generated from scripts.md; do not edit by hand.
# Pulls grades made by the pr-grader workflow into results/<run-id>/.
import argparse, json, re, shutil, subprocess, sys, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def default_repo():
    m = re.search(r"github\.com/([\w.-]+)/([\w.-]+)", (ROOT / "REPO.md").read_text())
    return f"{m[1]}/{m[2]}"


def mirror_repo():
    for line in (ROOT / "REPO.md").read_text().splitlines():
        m = re.search(r"github\.com/([\w.-]+)/([\w.-]+)", line)
        if m and "mirror" in line.lower():
            return f"{m[1]}/{m[2]}"
    sys.exit("REPO.md names no mirror repo")


def gh(*args):
    return subprocess.run(["gh", *args], check=True, capture_output=True, text=True).stdout


def main():
    p = argparse.ArgumentParser(color=False)
    p.add_argument("--mirror")
    p.add_argument("--repo", default=default_repo().replace("/", "_"))
    p.add_argument("--limit", type=int, default=100)
    a = p.parse_args()
    mirror = a.mirror or mirror_repo()

    # Filter by name: the workflow file lives only on base/* branches, so
    # --workflow may not resolve it.
    runs = [r for r in json.loads(gh("run", "list", "-R", mirror, "--json",
                                     "databaseId,workflowName,status", "-L", str(a.limit)))
            if r["workflowName"] == "pr-grader" and r["status"] == "completed"]
    collected = set()
    for r in runs:
        with tempfile.TemporaryDirectory() as td:
            dl = subprocess.run(["gh", "run", "download", str(r["databaseId"]), "-R", mirror,
                                 "-D", td], capture_output=True, text=True)
            if dl.returncode:
                continue
            for rid in Path(td).rglob("run-id.txt"):
                run_id = rid.read_text().strip()
                for f in rid.parent.glob("*.json"):
                    dest = ROOT / "results" / run_id / f.name
                    if dest.exists():
                        continue
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy(f, dest)
                    collected.add(int(f.stem))
                    print("collected", run_id, f.stem)

    prs = ROOT / "data" / a.repo / "prs"
    missing = sorted(n for n in collected if not (prs / str(n) / "meta.json").exists())
    if missing:
        subprocess.run([sys.executable, "-I", str(ROOT / "scripts" / "fetch_prs.py"),
                        *[x for n in missing for x in ("--pr", str(n))]], check=True)


main()
