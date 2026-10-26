# AI session: Data Preparation Workbench (Assignment 02)

**Tool:** Claude Code
**Scope of work:** `assignment_02/dashboard/`

## Request

Build a Streamlit "Data Preparation Workbench" app that carries out the
Section 2A data-preparation decisions for `titanic_features.csv`:

- Age: fill missing values with the median Age within each Pclass/Sex group.
- Cabin: create a `HasCabin` flag (if not already present), then drop `Cabin`.
- Embarked: fill missing values with the mode ("S").
- Sex and Embarked: dummy-code with `pd.get_dummies()`; Pclass stays numeric.
- Name and Ticket: drop both columns.

The app itself makes no data-preparation decisions on its own — every step
comes from a fixed menu the user chooses from, and each step displays the
exact pandas line it is equal to, plus a before/after profile (rows,
columns, missing values).

## Clarifications resolved before building

- `titanic_features.csv` was copied from `assignment_02/` into
  `assignment_02/dashboard/data/` so the app can load it with
  `Path(__file__).parent / "data"`.
- Dummy-coding uses `pd.get_dummies(..., drop_first=True)`.
- The download button's default filename is `titanic_prepared.csv`, matching
  what the assignment notebook's Section 2C check expects.

## What was built

- `app.py` — the workbench: file upload (or default dataset), a profile
  table, a fixed step menu (drop column, fill missing, dummy-code, drop rows
  missing a value, plus the two Section 2A presets for Age and
  Cabin/HasCabin), a step history with before/after comparisons and pandas
  code per step, an undo button, and a CSV download button.
- `requirements.txt` — pinned to the installed versions (`streamlit==1.58.0`,
  `pandas==3.0.3`); no packages were installed or upgraded.
- `README.md` — plain-language instructions for running the app.
- `data/titanic_features.csv` — copied in as the default dataset.
- `ai_sessions/`, `AI_USE_LOG.md` — left for the student's own record-keeping.

## Verification performed

- Confirmed `app.py` parses with no syntax errors.
- Started the app locally (`streamlit run app.py`) and confirmed it serves
  successfully (HTTP 200) with no startup errors.
- Confirmed the default dataset loads with the expected profile: 891 rows,
  14 columns; missing values in Age (177), Cabin (687), Embarked (2); and
  that `HasCabin` is already present alongside `Cabin` (so the duplicate
  guard in the Cabin preset is exercised correctly).
- Replicated the app's "Fill Age by Pclass/Sex median" preset
  (`df["Age"] = df.groupby(["Pclass", "Sex"])["Age"].transform(lambda s: s.fillna(s.median()))`)
  against the default dataset outside the UI (browser automation wasn't
  available in this environment): Age missing values went from 177 to 0,
  row/column shape unchanged (891 x 14), and the group medians used were
  reasonable (e.g. Pclass 1 female: 35.0, Pclass 3 male: 25.0).
