"""Data Preparation Workbench.

A simple Streamlit app for exploring and cleaning a CSV file step by step.
The app does not decide anything on its own — the user picks every step
from a fixed menu, and the app shows the pandas code each step is equal to.
"""

from pathlib import Path

import pandas as pd
import streamlit as st

DATA_DIR = Path(__file__).parent / "data"
DEFAULT_DATA_PATH = DATA_DIR / "titanic_features.csv"


# Build a small summary table: one row per column, with its type and
# how many (and what share) of its values are missing.
def compute_profile(df: pd.DataFrame) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "column": df.columns,
            "dtype": df.dtypes.astype(str).values,
            "missing_count": df.isna().sum().values,
            "missing_share": (df.isna().sum() / len(df)).round(3).values,
        }
    )


st.header("Data Preparation Workbench")

# Let the user upload their own CSV, or fall back to the course dataset.
uploaded_file = st.file_uploader("Upload a CSV file", type="csv")
source_id = f"{uploaded_file.name}-{uploaded_file.size}" if uploaded_file else "default"

# Load fresh data whenever the file source changes, and reset the step history.
# raw_df is kept untouched so the EDA tab can always look at the original data,
# even after the workbench has applied steps to df.
if "df" not in st.session_state or st.session_state.get("loaded_source") != source_id:
    if uploaded_file is not None:
        loaded_df = pd.read_csv(uploaded_file)
    else:
        loaded_df = pd.read_csv(DEFAULT_DATA_PATH)
    st.session_state.df = loaded_df
    st.session_state.raw_df = loaded_df.copy()
    st.session_state.history = []
    st.session_state.loaded_source = source_id

tab_workbench, tab_eda = st.tabs(["Workbench", "EDA"])

with tab_workbench:
    # Show the current dataset's size and a per-column missing-value profile.
    st.subheader("Dataset profile")
    current_df = st.session_state.df
    st.write(f"**Rows:** {current_df.shape[0]}  |  **Columns:** {current_df.shape[1]}")
    st.dataframe(compute_profile(current_df), width="stretch")

    # Build the fixed menu of steps. The two Section 2A presets only appear
    # once the columns they need are actually present in the data.
    st.subheader("Add a preparation step")
    columns_now = list(current_df.columns)
    step_options = [
        "Drop a column",
        "Fill missing values",
        "Dummy-code a column",
        "Drop rows missing a value",
    ]
    if {"Age", "Pclass", "Sex"}.issubset(columns_now):
        step_options.append("Fill Age by Pclass/Sex median (Section 2A preset)")
    if "Cabin" in columns_now:
        step_options.append("Create HasCabin flag, then drop Cabin (Section 2A preset)")

    step = st.selectbox("Choose a step", step_options)

    # Show the extra inputs each step type needs.
    col = None
    method = None
    custom_value = None
    if step == "Drop a column":
        col = st.selectbox("Column to drop", columns_now)
    elif step == "Fill missing values":
        col = st.selectbox("Column to fill", columns_now)
        method = st.selectbox("Fill method", ["mean", "median", "most frequent", "custom value"])
        if method == "custom value":
            custom_value = st.text_input("Value to fill with")
    elif step == "Dummy-code a column":
        col = st.selectbox("Column to dummy-code", columns_now)
    elif step == "Drop rows missing a value":
        col = st.selectbox("Column to check", columns_now)

    # Apply the chosen step to a copy of the data, and record before/after info.
    if st.button("Apply step"):
        df_before = current_df.copy()
        try:
            if step == "Drop a column":
                new_df = df_before.drop(columns=[col])
                code = f'df = df.drop(columns=["{col}"])'
                description = f"Drop column '{col}'"
            elif step == "Fill missing values":
                new_df = df_before.copy()
                if method == "mean":
                    new_df[col] = new_df[col].fillna(new_df[col].mean())
                    code = f'df["{col}"] = df["{col}"].fillna(df["{col}"].mean())'
                elif method == "median":
                    new_df[col] = new_df[col].fillna(new_df[col].median())
                    code = f'df["{col}"] = df["{col}"].fillna(df["{col}"].median())'
                elif method == "most frequent":
                    new_df[col] = new_df[col].fillna(new_df[col].mode()[0])
                    code = f'df["{col}"] = df["{col}"].fillna(df["{col}"].mode()[0])'
                else:
                    value = custom_value
                    if pd.api.types.is_numeric_dtype(new_df[col]):
                        value = float(value)
                    new_df[col] = new_df[col].fillna(value)
                    code = f'df["{col}"] = df["{col}"].fillna({value!r})'
                description = f"Fill missing values in '{col}' ({method})"
            elif step == "Dummy-code a column":
                new_df = pd.get_dummies(df_before, columns=[col], drop_first=True)
                code = f'df = pd.get_dummies(df, columns=["{col}"], drop_first=True)'
                description = f"Dummy-code column '{col}'"
            elif step == "Drop rows missing a value":
                new_df = df_before.dropna(subset=[col])
                code = f'df = df.dropna(subset=["{col}"])'
                description = f"Drop rows missing '{col}'"
            elif step.startswith("Fill Age by Pclass/Sex median"):
                new_df = df_before.copy()
                new_df["Age"] = new_df.groupby(["Pclass", "Sex"])["Age"].transform(
                    lambda s: s.fillna(s.median())
                )
                code = (
                    'df["Age"] = df.groupby(["Pclass", "Sex"])["Age"]'
                    '.transform(lambda s: s.fillna(s.median()))'
                )
                description = "Fill missing Age with the median Age for each Pclass/Sex group"
            else:  # Create HasCabin flag, then drop Cabin
                new_df = df_before.copy()
                if "HasCabin" not in new_df.columns:
                    new_df["HasCabin"] = new_df["Cabin"].notna().astype(int)
                    code = (
                        'df["HasCabin"] = df["Cabin"].notna().astype(int)\n'
                        'df = df.drop(columns=["Cabin"])'
                    )
                else:
                    code = (
                        "# HasCabin already exists, so it is not created again\n"
                        'df = df.drop(columns=["Cabin"])'
                    )
                new_df = new_df.drop(columns=["Cabin"])
                description = "Create HasCabin flag (if missing), then drop Cabin"

            st.session_state.history.append(
                {
                    "description": description,
                    "code": code,
                    "shape_before": df_before.shape,
                    "shape_after": new_df.shape,
                    "profile_before": compute_profile(df_before),
                    "profile_after": compute_profile(new_df),
                    "df_before": df_before,
                }
            )
            st.session_state.df = new_df
            st.rerun()
        except Exception as e:
            st.error(f"Could not apply this step: {e}")

    # Let the user undo the most recently applied step.
    if st.session_state.history:
        if st.button("Undo last step"):
            last_step = st.session_state.history.pop()
            st.session_state.df = last_step["df_before"]
            st.rerun()

    # Show every step applied so far, with the pandas line and before/after profiles.
    st.subheader("Steps applied")
    if not st.session_state.history:
        st.write("No steps applied yet.")
    else:
        for i, step_record in enumerate(st.session_state.history, start=1):
            with st.expander(f"Step {i}: {step_record['description']}"):
                st.code(step_record["code"], language="python")
                before_col, after_col = st.columns(2)
                with before_col:
                    rows, cols = step_record["shape_before"]
                    st.write(f"Before: {rows} rows, {cols} columns")
                    st.dataframe(step_record["profile_before"], width="stretch")
                with after_col:
                    rows, cols = step_record["shape_after"]
                    st.write(f"After: {rows} rows, {cols} columns")
                    st.dataframe(step_record["profile_after"], width="stretch")

    # Let the user download the current, prepared data as a CSV file.
    st.subheader("Download prepared data")
    csv_bytes = st.session_state.df.to_csv(index=False)
    st.download_button(
        "Download prepared data as CSV",
        data=csv_bytes,
        file_name="titanic_prepared.csv",
        mime="text/csv",
    )

with tab_eda:
    st.subheader("Exploratory data analysis")

    # Let the user pick whether to explore the original, untouched data or
    # the current prepared data (after whatever steps were applied above).
    data_choice = st.radio(
        "Data to explore", ["Raw data", "Prepared data (current)"], horizontal=True
    )
    eda_df = st.session_state.raw_df if data_choice == "Raw data" else st.session_state.df
    eda_columns = list(eda_df.columns)
    numeric_columns = list(eda_df.select_dtypes(include="number").columns)

    # 1. Summary statistics (numeric column) and a frequency table (any column).
    st.markdown("#### Summary statistics and frequency table")
    stats_col = st.selectbox("Numeric column for summary statistics", numeric_columns, key="stats_col")
    st.code(f'df["{stats_col}"].describe()', language="python")
    st.dataframe(eda_df[stats_col].describe(), width="stretch")

    freq_col = st.selectbox("Column for frequency table", eda_columns, key="freq_col")
    st.code(f'df["{freq_col}"].value_counts()', language="python")
    st.dataframe(eda_df[freq_col].value_counts(), width="stretch")

    # 2. Histogram of a chosen numeric column, binned with value_counts().
    st.markdown("#### Histogram")
    hist_col = st.selectbox("Numeric column to plot", numeric_columns, key="hist_col")
    st.code(f'df["{hist_col}"].value_counts(bins=10).sort_index()', language="python")
    hist_counts = eda_df[hist_col].value_counts(bins=10).sort_index()
    hist_counts.index = hist_counts.index.astype(str)
    st.bar_chart(hist_counts)

    # 3. Rate of Survived for each group of a chosen column (needs Survived).
    if "Survived" in eda_columns:
        st.markdown("#### Survival rate by group")
        group_options = [c for c in eda_columns if c != "Survived"]
        group_col = st.selectbox("Column to group by", group_options, key="group_col")
        st.code(f'df.groupby("{group_col}")["Survived"].mean()', language="python")
        survival_rate = eda_df.groupby(group_col)["Survived"].mean()
        st.bar_chart(survival_rate)
        st.dataframe(survival_rate, width="stretch")
    else:
        st.caption("No 'Survived' column in this data, so survival rate by group is skipped.")

    # 4. Correlation table across numeric columns.
    st.markdown("#### Correlation table")
    st.code("df.corr(numeric_only=True)", language="python")
    st.dataframe(eda_df.corr(numeric_only=True), width="stretch")
