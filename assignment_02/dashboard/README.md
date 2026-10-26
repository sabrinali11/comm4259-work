# Data Preparation Workbench

A Streamlit app for cleaning a CSV file step by step. You pick each step from a
fixed menu — the app never decides anything on its own, and it doesn't use any
AI model. For every step it shows the rows/columns/missing values before and
after, plus the exact line of pandas code the step is equal to.

## How to run it

From inside this folder (`assignment_02/dashboard/`), run:

```
streamlit run app.py
```

This opens the app in your browser.

## What it does

1. **Load data** — upload any CSV, or leave it blank to use the course's
   `data/titanic_features.csv`. Shows rows, columns, each column's type, and
   how many (and what share of) values are missing in each column.
2. **Add a step** from the fixed menu:
   - Drop a column
   - Fill missing values (mean, median, most frequent, or a value you type)
   - Dummy-code a column (`pd.get_dummies(..., drop_first=True)`)
   - Drop rows missing a value
   - Fill Age by the median Age within each Pclass/Sex group (only shown when
     Age, Pclass, and Sex are present) — used for the Section 2A Age decision
   - Create a `HasCabin` flag, then drop `Cabin` (only shown when Cabin is
     present; won't recreate `HasCabin` if it's already there) — used for the
     Section 2A Cabin decision
3. Each applied step is listed with its pandas code line and a before/after
   comparison. You can undo the most recent step.
4. **Download** the prepared data as `titanic_prepared.csv`.
