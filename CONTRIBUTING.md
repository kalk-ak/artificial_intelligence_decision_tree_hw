# Contributing: how to submit a pull request

All changes to this assignment arrive as **pull requests** to the course repository:

**Destination:** <https://github.com/kalk-ak/artificial_intelligence_decision_tree_hw> · base branch `main`

This guide is for course staff, TAs and anyone who wants to improve the material (typos, clearer wording, stronger self-checks, new
deliberate problems, ports to other datasets). **Students do not submit homework here**; homework goes to Gradescope as `submission.zip`.
If you found a bug while doing the homework, a pull request or an issue is very welcome, but it is separate from your submission.

## 0. Before you start

- Look through the open issues and pull requests to avoid duplicate work.
- For anything bigger than a typo, open an issue first and describe the change in two or three sentences, so that the pedagogy
  (which concepts a part builds on, which problems students are meant to hit) can be discussed before you invest time.
- You need `git`, a GitHub account, and the course environment (`pip install -r requirements.txt` inside a Python 3.11 or 3.12
  environment). The GitHub CLI (`gh`) is optional but used in the shortcuts below.

## 1. Get the code

If you have write access to the repository:

```bash
git clone https://github.com/kalk-ak/artificial_intelligence_decision_tree_hw.git
cd artificial_intelligence_decision_tree_hw
```

If you do not (most contributors), fork first, then clone your fork and keep the course repository as `upstream`:

```bash
gh repo fork kalk-ak/artificial_intelligence_decision_tree_hw --clone      # or use the Fork button on GitHub
cd artificial_intelligence_decision_tree_hw
git remote add upstream https://github.com/kalk-ak/artificial_intelligence_decision_tree_hw.git   # if gh did not add it
git fetch upstream
```

## 2. Create a branch

Never work on `main`. Name the branch after the change:

```bash
git checkout -b fix/part5-threshold-wording        # or feat/part6-oob-error, docs/rubric-q12, ...
```

## 3. Make the change in the right place

The student notebook is **generated**; editing it directly will be overwritten. The rules:

| You want to change | Edit this | Then |
|---|---|---|
| anything in the notebook (text, code, tests, voice questions) | `instructor/project_4_decision_trees_SOLUTION.ipynb` | regenerate the student notebook (step 4) |
| the rubric | `TA_GRADING_RUBRIC.md` | regenerate the PDF if you can (`pandoc` + a browser print works; otherwise say so in the PR) |
| the autograder points | `CODING_QUESTIONS` in `instructor/autograde.py` **and** the code table in the rubric | keep the two in sync |
| the voice questions | the `VOICE_QUESTIONS` cell in the solution notebook **and** the rubric | ids `Q00`–`Q18` are referenced by the recorder, the checker and the rubric |

Conventions inside the solution notebook:

- Solution code lives between `### BEGIN SOLUTION` and `### END SOLUTION`; the generator replaces it with
  `# YOUR CODE HERE` / `raise NotImplementedError()`. Keep the markers on their own lines.
- Keep cell tags: `test` + `test:<name>` on self-check cells (the autograder scores them), `voice` on recorder cells, `infra` on
  infrastructure cells. Add `solution-only` to a cell that must not reach students.
- Extra-credit solution cells carry the tag `extra-credit`: the generator replaces their solution with `return None` instead of a
  `raise`, so that students who skip the task still pass *Restart & Run All*. Their check cells must print `checks passed` on success;
  the autograder looks for that text.
- Student-facing functions: docstrings on every function, about 20 lines or fewer, one job per function (the notebook's own
  `lint_notebook_functions()` enforces this for students, so the staff code should pass it too).
- If you change the data split, the dev-sample seed or an experiment, update the **reference values** in the rubric (section 7) from a
  fresh run of the solution notebook.

## 4. Regenerate and test

```bash
# 1. the solution must run top to bottom (about 4 minutes) with no errors
jupyter nbconvert --to notebook --execute --inplace instructor/project_4_decision_trees_SOLUTION.ipynb

# 2. regenerate the student notebook from it
python instructor/make_student_version.py instructor/project_4_decision_trees_SOLUTION.ipynb project_4_decision_trees.ipynb

# 3. the autograder must give the solution 100/100
mkdir -p /tmp/p4check && cp instructor/project_4_decision_trees_SOLUTION.ipynb /tmp/p4check/project_4_decision_trees.ipynb
python instructor/autograde.py /tmp/p4check/project_4_decision_trees.ipynb
```

Open the regenerated student notebook once and confirm that no solution leaked and that the text still reads correctly around your change.

## 5. Commit

Commit only source files. **Never commit** `recordings/`, `submission.zip`, CSV data, the kagglehub cache or `.ipynb_checkpoints/`
(`.gitignore` already excludes them). Write the message in the imperative and say *why*:

```bash
git add -A
git status                      # check that only intended files are staged
git commit -m "Part 5: explain why the categorical tree keeps a higher accuracy than the threshold tree

The comparison table shows similar accuracies but lower F1 for the categorical tree; the old
text claimed the opposite. Also regenerates the student notebook."
```

If you worked with someone else, add a `Co-authored-by: Name <email>` trailer so GitHub credits them.

## 6. Push and open the pull request

```bash
git push -u origin fix/part5-threshold-wording
```

Then either click **Compare & pull request** on GitHub (the base must be `kalk-ak/artificial_intelligence_decision_tree_hw`, branch `main`;
from a fork, make sure the base repository is the course repository, not your fork), or use the CLI:

```bash
gh pr create --repo kalk-ak/artificial_intelligence_decision_tree_hw --base main --fill
```

Use this template for the description:

```
## What changes
One or two sentences.

## Why
The problem it solves (link the issue if there is one).

## Checklist
- [ ] solution notebook runs top to bottom without errors
- [ ] student notebook regenerated with make_student_version.py (no solution markers leaked)
- [ ] autograder gives the solution 100/100
- [ ] rubric / reference values updated if tests, seeds, points or questions changed
- [ ] no recordings, data files or submission zips in the diff
```

## 7. Review and merge

A maintainer reviews within a week during the semester. Expect questions about pedagogy as much as about code: a change that makes a
self-check stricter, or a deliberate problem easier to avoid, affects how students learn, and that is what the review protects.
Address review comments with new commits on the same branch (do not force-push once review has started). Pull requests are merged with
**squash and merge**, so a tidy history on your branch is not required.

## 8. Reporting problems without a fix

Open an issue with the part number, the cell's first line, what you expected and what happened, and your Python and package versions
(`pip freeze | grep -E "numpy|pandas|scikit|anywidget|ipywidgets|kagglehub"`). Do **not** post recordings, student names or anything
from a graded submission in an issue; academic-integrity matters go to the course staff privately.

## Maintainer notes: first publication of this repository

The repository on GitHub is created but empty. To publish the current state from this folder:

```bash
git branch -M main
git add -A
git commit -m "Project 4: decision trees course with voice answers, rubric and tooling"
git push -u origin main
```

After that, protect `main` in the repository settings (require a pull request before merging) so that the workflow above applies to
everyone, including maintainers.
