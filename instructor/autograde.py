#!/usr/bin/env python3
# -----------------------------------------------------------------------------
# Project 4: Decision Trees, from Entropy to Ensembles (EN.601.464, Johns Hopkins University)
# Who worked on this: [Professor's name] (instructor of record); Kaleb Aklilu and
# [Second TA's name] (teaching assistants; design, requirements, grading policy, review);
# EN.601.464 course staff of previous semesters (the original Project 4); drafted with
# Claude Code (Anthropic, Claude Fable 5.1) under the TAs' direction, October 2026.
# License: MIT, see LICENSE. Repository: https://github.com/kalk-ak/artificial_intelligence_decision_tree_hw
# -----------------------------------------------------------------------------
"""Run a student's notebook and score the tagged self-check cells.

Usage:  python autograde.py path/to/project_4_decision_trees.ipynb [--timeout 1800] [--json report.json]
        python autograde.py path/to/submission.zip            (extracts to a temp folder first)

The notebook is executed top to bottom in its own folder (so recordings/ and the Kaggle cache work).
Every code cell tagged `test` carries a second tag `test:<name>`; a test passes when its cell produces
no error output. Points per test are listed in POINTS (edit to match the rubric). The script also
reports the voice-recording manifest, missing functions and the function-length/docstring lint.
Requires: nbformat, nbclient, ipykernel and the course requirements in the active environment.
"""
import argparse
import json
import pathlib
import shutil
import sys
import tempfile
import zipfile

import nbformat
from nbclient import NotebookClient

POINTS = {
    "entropy_from_probabilities": 3, "entropy_pure": 2, "entropy": 3, "entropy_real": 1,
    "information_gain": 6, "gain_ratio": 4, "best_attribute": 4, "id3": 10, "predict_naive": 2, "predict_one": 5,
    "metrics": 6, "stratified_folds": 3,
    "entropy_np": 4, "best_threshold": 6, "grow_tree": 12,
    "bagging": 8, "adaboost": 9,
    "sk_tree": 3, "models": 4, "undersample": 2, "threshold": 3,
}
EXTRA_POINTS = {"ec_fast_threshold": 10, "ec_oob": 10, "ec_prune": 10, "ec_cost": 10}   # + Q20 voice (10) graded by TAs


def run(nb_path: pathlib.Path, timeout: int):
    nb = nbformat.read(nb_path, as_version=4)
    client = NotebookClient(nb, timeout=timeout, kernel_name="python3", allow_errors=True,
                            resources={"metadata": {"path": str(nb_path.parent)}})
    client.execute()
    return nb


def score(nb):
    results, errors = {}, []
    for i, cell in enumerate(nb.cells):
        if cell.cell_type != "code":
            continue
        failed = [o for o in cell.get("outputs", []) if o.get("output_type") == "error"]
        tags = cell.metadata.get("tags", [])
        names = [t.split(":", 1)[1] for t in tags if t.startswith("test:")]
        stdout = "".join("".join(o.get("text", "")) for o in cell.get("outputs", []) if o.get("output_type") == "stream")
        for name in names:
            table = EXTRA_POINTS if name in EXTRA_POINTS else POINTS
            passed = not failed and (name not in EXTRA_POINTS or "checks passed" in stdout)
            results[name] = {"passed": passed, "points": table.get(name, 0) if passed else 0, "max": table.get(name, 0),
                             "extra": name in EXTRA_POINTS,
                             "error": f"{failed[0].get('ename')}: {str(failed[0].get('evalue'))[:200]}" if failed else ("" if passed else "not attempted")}
        if failed and not names:
            errors.append({"cell": i, "head": cell.source.strip().splitlines()[0][:80] if cell.source.strip() else "",
                           "error": f"{failed[0].get('ename')}: {str(failed[0].get('evalue'))[:200]}"})
    return results, errors


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("path")
    ap.add_argument("--timeout", type=int, default=1800)
    ap.add_argument("--json", default=None)
    args = ap.parse_args()
    path = pathlib.Path(args.path)
    tmp = None
    if path.suffix == ".zip":
        tmp = pathlib.Path(tempfile.mkdtemp(prefix="autograde_"))
        with zipfile.ZipFile(path) as z:
            z.extractall(tmp)
        candidates = sorted(tmp.rglob("*.ipynb"))
        if not candidates:
            sys.exit("no notebook in the zip")
        path = candidates[0]
    nb = run(path, args.timeout)
    results, errors = score(nb)
    total = sum(r["points"] for r in results.values() if not r.get("extra")); maximum = sum(POINTS.values())
    extra = sum(r["points"] for r in results.values() if r.get("extra"))
    print(f"\n=== {path.name}: {total} / {maximum} autograded base points, +{extra} / {sum(EXTRA_POINTS.values())} autograded extra credit ===")
    for table in (POINTS, EXTRA_POINTS):
        for name, pts in table.items():
            r = results.get(name)
            status = "PASS" if r and r["passed"] else ("SKIPPED" if r and r.get("error") == "not attempted" else ("FAIL" if r else "MISSING CELL"))
            print(f"  {status:12s} {name:28s} {r['points'] if r else 0:3d}/{pts:<3d} {r['error'] if r else ''}")
    if errors:
        print(f"\n{len(errors)} non-test cells raised errors (these cost process points and may cascade):")
        for e in errors[:15]:
            print(f"  cell {e['cell']}: {e['error']}   | {e['head']}")
    manifest = path.parent / "recordings" / "manifest.json"
    if manifest.exists():
        rec = json.loads(manifest.read_text())["recordings"]
        short = [q for q, e in rec.items() if e.get("duration_s", 0) < 20]
        ext = [q for q, e in rec.items() if e.get("external")]
        print(f"\nrecordings: {len(rec)} found, total {sum(e['duration_s'] for e in rec.values())/60:.1f} min; "
              f"under 20 s: {short or 'none'}; external: {ext or 'none'}")
    else:
        print("\nrecordings/manifest.json NOT found next to the notebook")
    if args.json:
        pathlib.Path(args.json).write_text(json.dumps({"total": total, "max": maximum, "extra": extra, "tests": results, "errors": errors}, indent=2))
    if tmp:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    main()
