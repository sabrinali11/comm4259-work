# Customer Dashboard (lab_07/agent_demo)

A Streamlit dashboard for exploring the `Customer.csv` dataset, starting with
a Data Preparation tab.

## Data preparation decisions

- **Reviews / Feedback_Call** (83.2% / 83.8% missing): added `HasReview`
  (1 if the customer left a review, else 0), then dropped both columns.
- **ZipCode** (mix of 5-digit and 9-digit ZIP+4 values): kept only the
  first five digits.
- **BirthYear** (21.5% missing): filled missing values with the median
  BirthYear.
- **AgeAtJoin** (new feature): year of `JoinDate` minus `BirthYear`.

Note: the "Churned vs. Returning" chart assumes `Churn == 1` means the
customer churned and `Churn == 0` means they are still a returning
customer. Let me know if that mapping is backwards.

## How to run it

1. From this folder (`lab_07/agent_demo/`), install dependencies if needed:

   ```
   pip install -r requirements.txt
   ```

2. Launch the app:

   ```
   streamlit run app.py
   ```

3. Streamlit will open the dashboard in your browser (usually at
   `http://localhost:8501`).

## Folder contents

- `app.py` — the Streamlit app
- `data/Customer.csv` — the raw dataset
- `requirements.txt` — Python packages needed to run the app
- `ai_sessions/` — placeholder folder for saved AI session logs
- `AI_USE_LOG.md` — log of AI use (filled in by the student)
