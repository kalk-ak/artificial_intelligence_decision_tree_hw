# Project 4 — Instructor notes

*Decision Trees: from Entropy to Ensembles (medical screening edition).* EN.601.464 Artificial Intelligence.
These notes are for course staff only; do not distribute the `instructor/` folder.

## 1. What changed from the previous Project 4

| | Previous version | This version |
|---|---|---|
| Scope | implement `train` (ID3) for the mushroom data, then "use a library" | an 8-part course: entropy → information gain → ID3 → honest metrics on real data → failure modes → bagging, random forests, AdaBoost → scikit-learn / gradient boosting → clinical decision |
| Data | UCI mushrooms, 8,124 rows, shipped as a file | CDC BRFSS 2015 diabetes indicators, 253,680 rows × 21 features, downloaded from Kaggle by the notebook (`kagglehub`, public, no account needed) and held in memory |
| Written explanations | none / free text | 20 **voice answers** (+1 optional) recorded by a widget inside the notebook; prompts ask for general understanding in the student's own words, a few for a rough number from their own output |
| Pedagogy | one task | 8 deliberate problems the student must diagnose (crash on 0·log 0, identifier wins gain, `None` for unseen values, 86 % accuracy paradox, fragmentation, instability, correlated bagged trees, base-rate collapse) |
| Student-written code | 1 function | 32 functions in 19 solution cells, each with visible asserts (21 test cells, 100 autograded points) |
| Grading | 100 pts, 1-page rubric | 250 pts available, graded out of 200 (50 extra credit); `TA_GRADING_RUBRIC.md`; `autograde.py`; integrity manifest for recordings |
| Length | ~5–8 h | ~17 h plus an optional 2–3 h extra-credit part (see the time table in Part 0); can be split into two milestones, see §7 |

## 2. Files

Notebook structure: Parts 0–7 are the course, Part 8 is optional extra credit (EC1–EC4 code tasks + voice question Q20), Part 9 is the
submission checklist. Extra-credit stubs read `return None` instead of raising, so an unattempted task never breaks *Restart & Run All*;
their check cells print *skipped* and the autograder reports `SKIPPED`.

```
project_4_decision_trees.ipynb        student notebook (distribute this + requirements.txt)
requirements.txt                      numpy pandas matplotlib scikit-learn kagglehub anywidget ipywidgets jupyterlab (xgboost optional)
TA_GRADING_RUBRIC.md / .pdf           rubric with checklists, model answers and reference values (also shared as a Claude doc)
README.md                             public overview (learning outcomes, structure, voice-answer rationale, credits)
CONTRIBUTING.md                       how to submit a pull request to https://github.com/kalk-ak/artificial_intelligence_decision_tree_hw
LICENSE                               MIT, Copyright (c) 2026 Kaleb Aklilu
.gitignore                            keeps recordings, submission zips, data and caches out of the repository
instructor/
   project_4_decision_trees_SOLUTION.ipynb   master notebook with solutions (### BEGIN/END SOLUTION markers), executed, with outputs
   make_student_version.py                   strips solutions/outputs from the master -> student notebook
   autograde.py                              runs a submission and scores the tagged test cells (100 pts)
   INSTRUCTOR_NOTES.md                       this file
archive/                              the previous project_4.ipynb and rubric PDF
```

**Workflow for edits.** Edit `instructor/project_4_decision_trees_SOLUTION.ipynb` in Jupyter (keep the `### BEGIN SOLUTION` /
`### END SOLUTION` markers and the cell tags `test`, `test:<name>`, `voice`, `infra`), run it top to bottom, then regenerate the student
file: `python instructor/make_student_version.py instructor/project_4_decision_trees_SOLUTION.ipynb project_4_decision_trees.ipynb`.
Cells tagged `solution-only` are dropped from the student version if you want instructor-only commentary in the master.

## 3. The voice recorder

* Implementation: an [anywidget](https://anywidget.dev) widget. The browser side uses `navigator.mediaDevices.getUserMedia` +
  `MediaRecorder`; on *Stop & save* it base64-encodes the blob into a synced traitlet; the Python side decodes it, writes
  `recordings/<QID>.<ext>`, and appends an entry to `recordings/manifest.json` with duration, UTC timestamp, byte size, SHA-256, the
  question text and a flag for externally recorded files. The payload is cleared from the widget state after saving, so notebooks stay small.
* Formats: Chrome/Edge/Firefox produce `audio/webm;codecs=opus` (`.webm`), Safari produces `audio/mp4` (`.m4a`). Any modern browser
  plays both. Opus at the browser default bitrate is ≈ 250–500 KB per minute, so a full submission is 5–10 MB.
* Requirements: `anywidget>=0.9` and `ipywidgets>=8` (JupyterLab 4 / Notebook 7 need no extra extension), a browser tab served from
  `http://localhost` or `https://` (the microphone API is blocked on plain `http://` remote hosts, which matters for JupyterHub without TLS),
  and microphone permission. VS Code's notebook webview may not grant microphone access; the notebook tells students to use the browser.
* Fallbacks: `register_external_recording(qid, path, seconds)` attaches a file recorded with any app and flags it `external` in the
  manifest and in `review.html`. Without `anywidget`, `record_answer` prints install instructions and the question text.
* Re-running a recorder cell shows the existing take with a *Re-record* button, so *Restart & Run All* never erases audio.
* `build_submission()` re-hashes every file, refuses to package if a hash does not match, warns on short takes, writes
  `recordings/review.html` (table with inline players for TAs) and zips notebook + recordings.
* **Testing status.** The Python half (saving, manifest, re-record replacing files, external registration, status table, zip, review page,
  linter) is covered by an automated test. The JavaScript half was syntax-checked with Node and reviewed by hand, but **has not been
  exercised with a real microphone in this build** (no audio device in the build environment). Before release, open the student notebook in
  JupyterLab, run the Q00 cell, record a few seconds, and confirm `recordings/Q00.webm` appears and plays back. Try Safari once if your students
  use Macs. If something fails, the widget shows the browser's error text in red under the buttons.
* Privacy: recordings never leave the student's machine until they upload the zip. Say so in class; it is in Part 0.3 of the notebook.

## 4. The data

* `alexteboul/diabetes-health-indicators-dataset` on Kaggle, CC0, 6 MB zip. `kagglehub.dataset_download` works **without** a Kaggle
  account for public datasets (verified in a clean environment with no credentials); the files are cached in `~/.cache/kagglehub`.
  If a campus proxy blocks it, students can run `kagglehub.login()` or download the CSV manually and place it where `load_diabetes_data`
  expects it (the error message explains).
* The notebook uses `diabetes_binary_health_indicators_BRFSS2015.csv` (253,680 × 22, 13.93 % positive). The dataset also ships a
  50/50 file (70,692 rows) that is a subset of the same rows; the notebook deliberately builds its own balanced sample from the training
  split instead and explains why (leakage into the holdout).
* 24,206 rows are exact duplicates of earlier rows (35,575 rows have a twin). Part 4 uses this for the leakage discussion (Q10).
* Splits are deterministic: stratified 80/20 holdout with seed 0; a stratified 50,000-row development sample (seed 0) from the training part
  for Parts 4–6; the full 202,944-row training set for Part 7.

## 5. Deliberate problems and the intended "aha"

| # | Where | What the student sees | What they must say |
|---|---|---|---|
| 1 | Part 1 | `ValueError: math domain error` for `[1.0, 0.0]` | 0·log 0 is undefined but its limit is 0; skip zero probabilities |
| 2 | Part 2 | `patient_id` has gain 0.954 = H(parent) | many-valued attributes buy purity by fragmentation; gain ratio helps (0.243 vs 0.239) but barely |
| 3 | Part 3 | `predict_one_naive` returns `None` for an underweight patient; scoring refuses it | the walk has no branch; fall back to the node's stored majority |
| 4 | Part 4 | depths 0–6 all score ≈ 86 %, deeper is worse | prevalence 13.9 %; leaves must exceed 50 % positives to flip; accuracy hides the minority; sensitivity/specificity |
| 5 | Part 5 | categorical tree: 17,079 leaves, 8 % unseen-branch rate; BMI split into 68/58 branches | fragmentation = problem #2 at scale; thresholds fix it |
| 6 | Part 5 | two halves: roots `GenHlth ≤ 2.5` vs `HighBP`, 14.6 % disagreement | greedy root choice + full growth = high variance |
| 7 | Part 6 | 17 of 25 bagged trees rooted at `HighBP`; sensitivity falls at the 0.5 vote threshold | correlated trees; `max_features`; the vote fraction is a threshold dial |
| 8 | Part 7 | balanced-trained model: precision 0.73 on a balanced holdout, 0.30 at real prevalence | base rates; evaluate at deployment prevalence |

## 6. Expected results and runtime (solution notebook, 16-core laptop, Python 3.12)

Whole notebook: **≈ 5 minutes** for *Restart & Run All* (about 4 without the extra-credit cells). Heavy cells: bagging 25 trees ≈ 85 s, random forest ≈ 30 s,
`min_samples_leaf` sweep ≈ 27 s, learning curve ≈ 20 s, categorical full tree ≈ 10 s, AdaBoost ≈ 9 s, Part 7 models ≈ 7 s (XGBoost adds ≈ 15 s).
Students on slower machines should expect 8–10 minutes.

The full table of reference values (every number the voice questions ask for) is §7 of `TA_GRADING_RUBRIC.md`. Highlights:
label entropy 0.5825 bits; toy gains 0.3845 / 0.2054 / 0.2054 / 0.1635; pure-Python ID3 holdout accuracy by depth 0–6:
0.8607, 0.8607, 0.8619, 0.8581, 0.8464, 0.8293, 0.8184; learning-curve holdout error minimum ≈ 0.136 at depth 5–8, 0.168 at full depth;
bagging 25 trees at 0.5: acc 0.859 / sens 0.174 / F1 0.256, at 0.2: sens 0.62 / spec 0.80 / F1 0.436; HistGradientBoosting AUC 0.828,
80 % sensitivity at threshold ≈ 0.133 with specificity 0.70 and precision 0.30.

Versions tested: numpy 2.5, pandas 3.0, scikit-learn 1.9, matplotlib 3.11, anywidget 0.11, ipywidgets 8.1, kagglehub 1.0, xgboost 3.4
(Python 3.12); every cell also compiles under Python 3.11.

## 7. Suggested use

* **Milestones.** A natural split is Milestone A = Parts 0–4 (entropy to metrics, Q00–Q10, ≈ 8 h) and Milestone B = Parts 5–8
  (array trees to the capstone, Q11–Q19, ≈ 9 h). `build_submission()` requires all 20 recordings; for a two-milestone run, tell students
  to submit the notebook plus the `recordings/` folder as a zip for Milestone A (or temporarily trim `VOICE_QUESTIONS`).
* **In-class hooks.** Part 4's 86 % table and Part 7's base-rate cell make good 10-minute discussions. The capstone (Q19) can be
  turned into a 3-minute in-class pitch for a few volunteers.
* **Grading load.** ≈ 30 TA-minutes per submission (autograder unattended, 5 min code review, 20 min listening at 1.5×). The rubric
  suggests grading one question across many students for consistency. Optional: transcribe recordings with Whisper to skim before listening;
  grade from the audio, not the transcript.
* **Integrity.** The design relies on (a) the mic-check voice reference, (b) questions that require the student's own numbers, (c) manifest
  hashes and timestamps, and (d) the fact that an explanation of *why your run did X* is hard to outsource. It does not prevent a student
  from reading a prepared script; the rubric caps such answers and tells TAs what to listen for.
* **Varying the assignment between semesters.** Change the dev-sample seed and the holdout seed (two constants in Part 4); switch the
  target to the three-class `Diabetes_012` file; swap in the BRFSS heart-disease dataset (`kamilpytlak/personal-key-indicators-of-heart-disease`,
  same structure); change the capstone scenario (e.g., a payer deciding whom to invite for screening). The reference values in the rubric
  then need to be regenerated from the solution run.

## 8. Publishing and licensing

The material is MIT-licensed so that other courses can reproduce and adapt it; the copyright line names Kaleb Aklilu (change it to the professor or the course if preferred). Authorship is
recorded as Python comments at the top of the notebook's first code cell and of both scripts (professor, both TAs, previous course staff,
and Claude Code as the drafting tool), in the staff line under the notebook title, in the notebook footer and in the README. The names
live in one place for the build (`staff.py` next to the notebook sources) and as plain text in the files listed here. The GitHub repository `kalk-ak/artificial_intelligence_decision_tree_hw` is the
destination for pull requests; `CONTRIBUTING.md` has the workflow and the one-time commands for the first push (`git branch -M main`,
commit, `git push -u origin main`). Nothing in the repository identifies students: recordings, submissions and data are ignored by git.

## 9. Known limitations

* The from-scratch trees are pure numpy and deliberately simple; the bagging cell is the slowest part of the notebook. If student laptops
  struggle, reduce `fit_bagging(..., 25, ...)` to 15 trees in Part 6 (the lessons do not change; update the rubric's root-count numbers).
* `lint_notebook_functions()` lists every function defined in the notebook, including provided ones, so TAs should look at the flagged
  names rather than the row count.
* Gain ratio is implemented and tested on the toy data, and `train_tree(criterion="gain_ratio")` works, but no experiment in the notebook
  uses it at scale; it is an easy extension if you want a Part 5 exercise on it.
* The widget's recording length is capped at each question's `max_s`; the recorder stops itself, which students are told.
