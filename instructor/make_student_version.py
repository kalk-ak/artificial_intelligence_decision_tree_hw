#!/usr/bin/env python3
# -----------------------------------------------------------------------------
# Project 4: Decision Trees, from Entropy to Ensembles (EN.601.464, Johns Hopkins University)
# Who worked on this: [Professor's name] (instructor of record); Kaleb Aklilu and
# [Second TA's name] (teaching assistants; design, requirements, grading policy, review);
# EN.601.464 course staff of previous semesters (the original Project 4); drafted with
# Claude Code (Anthropic, Claude Fable 5.1) under the TAs' direction, October 2026.
# License: MIT, see LICENSE. Repository: https://github.com/kalk-ak/artificial_intelligence_decision_tree_hw
# -----------------------------------------------------------------------------
"""Derive the student notebook from the solution notebook.

Usage:  python make_student_version.py project_4_decision_trees_SOLUTION.ipynb ../project_4_decision_trees.ipynb

Rules (nbgrader-style):
  * In code cells, the lines between `### BEGIN SOLUTION` and `### END SOLUTION` are replaced by
        # YOUR CODE HERE
        raise NotImplementedError()
    at the indentation of the BEGIN marker.
  * Lines between `### BEGIN HIDDEN TESTS` and `### END HIDDEN TESTS` are removed.
  * Cells tagged `solution-only` are dropped.
  * All outputs and execution counts are cleared.
Edit the SOLUTION notebook in Jupyter, re-run this script, and both files stay in sync.
"""
import copy
import re
import sys

import nbformat

SOLUTION_RE = re.compile(r"^(\s*)### BEGIN SOLUTION\s*$")


def strip_solution(src: str) -> str:
    out, in_solution, in_hidden = [], False, False
    for line in src.split("\n"):
        s = line.strip()
        if s.startswith("### BEGIN HIDDEN TESTS"):
            in_hidden = True
            continue
        if s.startswith("### END HIDDEN TESTS"):
            in_hidden = False
            continue
        if in_hidden:
            continue
        m = SOLUTION_RE.match(line)
        if m:
            in_solution = True
            out.append(f"{m.group(1)}# YOUR CODE HERE")
            out.append(f"{m.group(1)}raise NotImplementedError()")
            continue
        if s.startswith("### END SOLUTION"):
            in_solution = False
            continue
        if not in_solution:
            out.append(line)
    return "\n".join(out)


def student_version(master):
    nb = copy.deepcopy(master)
    kept = []
    for cell in nb.cells:
        if "solution-only" in cell.metadata.get("tags", []):
            continue
        if cell.cell_type == "code":
            cell.source = strip_solution(cell.source)
            cell.outputs = []
            cell.execution_count = None
        kept.append(cell)
    nb.cells = kept
    return nb


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    master = nbformat.read(sys.argv[1], as_version=4)
    student = student_version(master)
    leaks = [i for i, c in enumerate(student.cells) if c.cell_type == "code" and "### BEGIN SOLUTION" in c.source]
    assert not leaks, f"solution markers survived in cells {leaks}"
    nbformat.validate(student)
    nbformat.write(student, sys.argv[2])
    n = sum("raise NotImplementedError()" in c.source for c in student.cells if c.cell_type == "code")
    print(f"wrote {sys.argv[2]}: {len(student.cells)} cells, {n} cells with solution stubs")
