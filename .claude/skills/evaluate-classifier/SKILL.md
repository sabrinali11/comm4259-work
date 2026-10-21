---
name: evaluate-classifier
description: Use when the student wants to train and evaluate a binary classifier (e.g. a decision tree) on a CSV for a COMM 4259 assignment or lab, with holdout metrics for a chosen positive class, a confusion matrix image, a cost-based total cost, and cross-validation accuracy.
---

# Evaluate a classifier on a CSV

This skill writes a Python script that trains a binary classifier on a CSV file
and reports a standard set of evaluation metrics. It was built from the
lab_08 WineQuality evaluation and keeps the same conventions.

## 1. Ask the student for the following, if not already given

- **File**: path to the CSV file to use.
- **Target column**: the column to predict.
- **Positive class**: the value in the target column to treat as "positive"
  (e.g. `Good`). Metrics are reported for this class.
- **Columns to drop**: any columns to exclude from the features besides the
  target (e.g. IDs). Do not guess at or add any other feature engineering —
  use exactly the columns the student specifies.
- **Model and settings**: the scikit-learn classifier class and its
  hyperparameters (e.g. `DecisionTreeClassifier(max_depth=5, random_state=1)`).
  Use exactly what the student specifies; do not substitute defaults.
- **Cost matrix**: a 2x2 matrix, rows = actual, columns = predicted, in the
  order (positive class, other class). Confirm the order back to the student
  before using it.
- **Output folder**: where to write the script and save the confusion matrix
  PNG. Only create or edit files inside this folder (per the project's
  CLAUDE.md rule of working only in the current task's folder) unless the
  student explicitly says otherwise.

If the target has more than two classes, ask the student how they want to
define "positive" vs. "the rest" (or whether this skill even fits), rather
than assuming.

## 2. Build the script with these exact conventions

- **Split**: stratified 70/30 train/test split using `train_test_split` with
  `stratify=y` and the same `random_state` as the model (ask if the student
  wants a different one for the split).
- **Holdout metrics**: accuracy overall, plus precision, recall, and F1 for
  the positive class only (`pos_label=<positive class>`), not averaged across
  classes.
- **Confusion matrix**: compute with `labels=[positive_class, other_class]`
  so both rows and columns are ordered positive class first, then the other
  class — this must match the cost matrix order. Print it as a small table
  and also save it as a PNG in the output folder (e.g. via
  `ConfusionMatrixDisplay`).
- **Total cost**: elementwise multiply the confusion matrix by the cost
  matrix (same row/column order) and sum, using the costs the student gave —
  do not invent a different cost convention.
- **Cross-validation**: `StratifiedKFold` with `n_splits=5`, `shuffle=True`,
  and the same `random_state`. Report mean accuracy and the standard
  deviation (as mean ± std), not just the mean.
- **Formatting**: print every rate (accuracy, precision, recall, F1, CV mean,
  CV std) as a percentage with two decimal places (e.g. `85.80%`), in one
  short results table. Total cost is printed as a plain number, not a
  percentage.
- **Comments**: put a short comment above each block of code describing what
  it does, per the project's CLAUDE.md style.
- **No new packages**: use only pandas, numpy, matplotlib, and scikit-learn.
  If something seems to need a package that isn't already installed, ask the
  student first instead of installing it.

## 3. Run and report

Run the script to confirm it works, then tell the student the exact command
to run it themselves (including the working directory), and point out where
the confusion matrix PNG was saved.
