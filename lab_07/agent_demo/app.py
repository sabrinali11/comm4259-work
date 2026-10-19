import os

import pandas as pd
import streamlit as st

st.set_page_config(page_title="Customer Dashboard", layout="wide")

# Load the raw CSV using a path relative to this file, so the app
# works no matter where it is launched from.
APP_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(APP_DIR, "data", "Customer.csv")
raw_df = pd.read_csv(DATA_PATH)


def summarize_missing(df: pd.DataFrame) -> pd.DataFrame:
    # Build a small table of missing-value counts and percentages per column.
    missing_count = df.isna().sum()
    missing_pct = (missing_count / len(df) * 100).round(1)
    return pd.DataFrame(
        {"Missing Values": missing_count, "Missing %": missing_pct}
    )


def prepare_data(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    # Reviews/Feedback_Call are both missing >80% of the time. Before
    # dropping them, keep a record of who left a review at all.
    df["HasReview"] = df["Reviews"].notna().astype(int)
    df = df.drop(columns=["Reviews", "Feedback_Call"])

    # ZipCode has both 5-digit and 9-digit (ZIP+4) values; keep just the
    # first five digits for everyone.
    df["ZipCode"] = df["ZipCode"].astype(str).str[:5]

    # BirthYear is missing for 21.5% of customers. Fill those gaps with
    # the median BirthYear so every row can still get an AgeAtJoin value.
    df["BirthYear"] = df["BirthYear"].fillna(df["BirthYear"].median())

    # New feature: how old each customer was when they joined.
    df["JoinDate"] = pd.to_datetime(df["JoinDate"])
    df["AgeAtJoin"] = df["JoinDate"].dt.year - df["BirthYear"]

    return df


clean_df = prepare_data(raw_df)

st.title("Customer Dashboard")

tab_prep, = st.tabs(["Data Preparation"])

with tab_prep:
    st.header("Data Preparation")

    st.subheader("Missing Values: Before vs. After")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Before**")
        st.dataframe(summarize_missing(raw_df))
    with col2:
        st.markdown("**After**")
        st.dataframe(summarize_missing(clean_df))

    st.subheader("Dataset Shape: Before vs. After")
    shape_df = pd.DataFrame(
        {
            "Rows": [raw_df.shape[0], clean_df.shape[0]],
            "Columns": [raw_df.shape[1], clean_df.shape[1]],
        },
        index=["Before", "After"],
    )
    st.dataframe(shape_df)

    st.subheader("Average Age at Join: Churned vs. Returning Customers")
    age_by_churn = (
        clean_df.groupby("Churn")["AgeAtJoin"]
        .mean()
        .rename(index={0: "Returning", 1: "Churned"})
    )
    st.bar_chart(age_by_churn)
