# Project 4 — Decision Trees: from Entropy to Ensembles

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
![Python 3.11 | 3.12](https://img.shields.io/badge/python-3.11%20%7C%203.12-blue)
![Jupyter](https://img.shields.io/badge/notebook-JupyterLab%204-orange)

Who worked on this
Musab Hadque <mhaque5@jhu.edu>, instructor of record for EN.601.464: course content, the lecture material
(the lecture dataset and tree that the self-checks reproduce) and approval of the design.

Matthew Brownrigg <mbrown1@jh.edu>, teaching assistant: assignment design, review, testing and grading.

Kaleb Aklilu <kaklilu1@jh.edu>, teaching assistant: assignment design, requirements, grading policy, review.

Claude Code: drafted the refactored notebook, the
voice-recorder widget, the autograder and the TA rubric under the TAs' direction,
October 2026.

> **Why spoken answers?** Every explanation in this project is a **voice recording** made inside the notebook instead of a written
> paragraph. The format was introduced to mitigate the use of AI tools to generate the entire homework in one shot: each spoken
> prompt asks the student to explain, in their own words, what they built and _why their own code_ broke, which is hard to outsource
> and easy for a TA to check against the notebook.
>
> **Using AI to learn is encouraged.** The notebook says so on its first page: students may use any AI tool to understand a concept,
> an error message or a question. What must be their own is the code they can explain and the recorded explanation itself.
> Students who use an AI chat save those conversations as PDFs in `ai_logs/`, and `build_submission()` packs them into the zip.
> Details in [Voice answers](#voice-answers).

## What students learn

- Build **entropy, information gain, gain ratio and ID3** from scratch, test them against a hand-computable toy dataset and the
  exact tree from lecture, and run the same code on real patients.
- Evaluate **honestly**: stratified holdouts and folds, confusion matrices, sensitivity, specificity, precision, F1, balanced accuracy,
  AUC, operating thresholds and base rates, framed for clinical screening.
- Discover the **failure modes of a single tree** by running into them: the accuracy paradox at 14% prevalence, many-valued attribute
  bias and fragmentation, unseen values, overfitting, instability and axis-aligned boundaries.
- Fix them with **thresholds, pre-pruning, bagging, random forests and AdaBoost**, implemented in numpy on top of their own tree, and
  then with **scikit-learn, histogram gradient boosting and (optionally) XGBoost** on the full data.
- Reason about **deployment**: balanced training versus real prevalence, feature importances versus causation, the use of income and
  education in a clinical tool, and what to monitor after release.

## How the project is organised

| Part | Topic                                    | Student builds                                                                                    | Deliberate problem to explain                                             | Time  |
| ---- | ---------------------------------------- | ------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------- | ----- |
| 0    | Setup, recorder, Kaggle download         | —                                                                                                 | —                                                                         | 0.5 h |
| 1    | Entropy                                  | `entropy_from_probabilities`, `class_probabilities`, `entropy`                                    | `math domain error` on a pure group (0 log 0)                             | 1.5 h |
| 2    | Information gain and its bias            | `partition`, `information_gain`, `split_info`, `gain_ratio`                                       | `patient_id` wins information gain                                        | 1.5 h |
| 3    | ID3 and prediction                       | `majority_class`, `best_attribute`, `id3`, `predict_one_naive`, `predict_one`, `classify`         | prediction returns `None` for an unseen value                             | 2.5 h |
| 4    | Real patients and clinical metrics       | `confusion_counts`, `sensitivity`, `specificity`, `precision`, `f1_score`, `stratified_folds`     | every tree scores exactly 86.07%                                          | 2.5 h |
| 5    | The limits of a single tree              | `entropy_np`, `information_gain_np`, `best_threshold`, `should_stop`, `best_split`, `grow_tree`   | BMI fragmented into one branch per value; two halves give different trees | 3 h   |
| 6    | Ensembles                                | `bootstrap_indices`, `fit_bagging`, `predict_proba_bagging`, `predict_bagging`, `fit_adaboost`    | 17 of 25 bagged trees share the same root                                 | 3 h   |
| 7    | Industry tools and the clinical decision | scikit-learn tree, forest, gradient boosting, `undersample_balanced`, `threshold_for_sensitivity` | precision collapses at real prevalence after balanced training            | 2.5 h |
| 8    | Extra credit (optional)                  | `best_threshold_fast`, out-of-bag error, `prune_tree`, `threshold_for_cost`                       | —                                                                         | 2–3 h |
| 9    | Submit                                   | `lint_notebook_functions()`, `recording_status()`, `build_submission()`                           | —                                                                         | 0.3 h |

Each part reuses the functions of the previous one: the `entropy` of Part 1 sits inside the `information_gain` of Part 2, inside the
`id3` of Part 3, which is ported to arrays in Part 5 and wrapped in ensembles in Part 6. Every student-written function has visible
self-check `assert` cells; 20 of them are autograded.

## Voice answers

Eighteen required questions (Q00–Q17, 20 to 180 seconds each) and one optional extra-credit question (Q18) are answered out loud.
The prompts ask for general understanding in the student's own words; a few ask for a rough number from the student's own output. A recorder built into the notebook (an
[anywidget](https://anywidget.dev) around the browser's `MediaRecorder`) saves each take to `recordings/<QID>.webm` together with its
length, a UTC timestamp and a SHA-256 fingerprint in `recordings/manifest.json`. `build_submission()` verifies the set and writes
`submission.zip` (notebook + recordings + a `review.html` page with inline players for TAs). Q00 is a mic check in which the student
states their name, which also gives graders a voice reference. The rubric caps answers that recite generic text without the student's
own numbers; grading guidance is in [`TA_GRADING_RUBRIC.md`](TA_GRADING_RUBRIC.md).

Students who cannot use the browser recorder can attach a file recorded elsewhere with `register_external_recording(...)`; it is flagged
for TAs but graded normally. Recordings never leave the student's machine until they upload the zip.

## Getting started (students)

```bash
conda create -n ai_hw4 python=3.11 -y
conda activate ai_hw4
pip install -r requirements.txt
jupyter lab project_4_decision_trees.ipynb
```

- Open the notebook in a **browser** (Chrome, Edge, Firefox or Safari) at the default `http://localhost` address, or in **VS Code** with the
  Jupyter extension. In VS Code the notebook records through Python (`sounddevice` + `soundfile`), because VS Code blocks the browser
  microphone inside notebooks. On Linux, also install PortAudio (`conda install -c conda-forge portaudio`).
- Part 0 downloads the data from Kaggle through `kagglehub` (6 MB, public, no Kaggle account needed) and keeps it in memory.
- Work through the parts in order; expect about 17 hours in total, plus 2 to 3 hours if you attempt the extra credit. _Restart Kernel and
  Run All_ should finish in roughly 5 to 10 minutes depending on your laptop; the slowest cell grows 25 bagged trees.
- Finish with Part 9: `lint_notebook_functions()`, `recording_status()`, `build_submission()`, then upload `submission.zip` to Gradescope.

## For instructors and TAs

| File                                                 | Purpose                                                                                                                      |
| ---------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------- |
| `project_4_decision_trees.ipynb`                     | the assignment (239 cells, Parts 0–9, 18 voice questions + 1 optional, 7 deliberate problems, 50 points of extra credit)     |
| `TA_GRADING_RUBRIC.md` / `.pdf`                      | 200-point rubric: checklists and model answers for all 19 voice questions, code tests, penalties, workflow, reference values |
| `instructor/project_4_decision_trees_SOLUTION.ipynb` | executed solution; the master copy (`### BEGIN SOLUTION` / `### END SOLUTION` markers, cell tags)                            |
| `instructor/make_student_version.py`                 | regenerates the student notebook from the solution (strips solutions and outputs)                                            |
| `instructor/autograde.py`                            | executes a `submission.zip` and scores the 10 coding questions (10 points each, 100 points)                                   |
| `instructor/INSTRUCTOR_NOTES.md`                     | design rationale, recorder internals, data notes, expected results, grading load, variations                                 |
| `archive/`                                           | the previous Project 4 notebook and rubric, kept for reference                                                               |

Grading: **250 points available, graded out of 200.** The 200 base points are 100 for code (10 autograded coding questions,
10 points each), 90 for voice answers (18 questions, 5 points each) and 10 for process; the 50 extra-credit points (four autograded coding tasks and one voice question in Part 8)
are a buffer that can make up for lost points or lift a score above 100%. The solution notebook scores 100/100 base and 40/40
extra credit on the autograder and runs end to end in about five minutes. Before the first release, open the student notebook in a browser
and in VS Code, run the Q00 cell and record a few seconds in each to confirm both recorders work on your setup.

Edit the solution notebook, not the student one, and regenerate:

```bash
python instructor/make_student_version.py instructor/project_4_decision_trees_SOLUTION.ipynb project_4_decision_trees.ipynb
python instructor/autograde.py path/to/submission.zip
```

## Dataset

[CDC Diabetes Health Indicators (BRFSS 2015)](https://www.kaggle.com/datasets/alexteboul/diabetes-health-indicators-dataset), cleaned by
Alex Teboul and published on Kaggle under CC0: 253,680 survey respondents, 21 health indicators, 13.93% with (pre)diabetes. The notebook
uses only the binary-label file and builds its own balanced samples from the training split to avoid leakage into the holdout. The data
is self-reported survey data; the notebook presents the task as screening and risk stratification, not diagnosis.

## Repository layout

```
.
├── project_4_decision_trees.ipynb      student notebook (239 cells, Parts 0-9, 18 voice questions + 1 optional)
├── requirements.txt
├── TA_GRADING_RUBRIC.md                rubric (Markdown) and TA_GRADING_RUBRIC.pdf
├── README.md · CONTRIBUTING.md · LICENSE · .gitignore
└── archive/                            previous version of the assignment
```

## Contributing

Bug reports, typo fixes, better self-checks, new deliberate problems and ports to other datasets are welcome through pull requests to
<https://github.com/kalk-ak/artificial_intelligence_decision_tree_hw>. The step-by-step guide, including how to keep the solution and
student notebooks in sync and what never to commit, is in [`CONTRIBUTING.md`](CONTRIBUTING.md). Homework submissions do **not** go
through pull requests; students submit `submission.zip` on Gradescope.

## License and credits

Released under the [MIT License](LICENSE), Copyright (c) 2026 Kaleb Aklilu. You may reuse and adapt the notebook, rubric and tooling in
your own course; a link back to this repository is appreciated. The dataset is CC0 (see above).

Who worked on this (also recorded as comments at the top of the notebook's first code cell and of each script):

- **[Professor's name]**, instructor of record for EN.601.464: course content, the lecture material the self-checks reproduce, and approval of the design.
- **Kaleb Aklilu**, teaching assistant: assignment design, requirements, pedagogy (deliberate problems, voice answers, medical framing), grading policy and review.
- **[Second TA's name]**, teaching assistant: review, testing and grading.
- **EN.601.464 course staff** of previous semesters: the original Project 4 (ID3 on the mushroom data), whose lecture dataset and tree the self-checks still reproduce.
- **Claude Code** (Anthropic, model Claude Fable 5.1): drafted the refactored notebook, the voice-recorder widget, the autograder and the TA rubric under the TAs' direction, October 2026.
