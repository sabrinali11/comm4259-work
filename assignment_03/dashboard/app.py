"""
Assignment 3 dashboard: Model Evaluation.
This app only trains a DecisionTreeClassifier and reports evaluation metrics
that scikit-learn computes. It does not use any AI model and makes no
decisions on its own -- every number comes from a labeled scikit-learn call.
"""
from pathlib import Path

import numpy as np
import pandas as pd
import streamlit as st
from sklearn.metrics import confusion_matrix, f1_score, precision_score, recall_score
from sklearn.model_selection import StratifiedKFold, cross_val_score, train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn.utils import resample

st.set_page_config(page_title="Assignment 3: Model Evaluation", layout="wide")


# Turn a 0-1 rate into a "NN.NN%" string, used for every rate shown in the app.
def pct(value: float) -> str:
    return f"{value * 100:.2f}%"


# Load the cleaned Titanic data once and split it into features (X) and target (y).
@st.cache_data
def load_data() -> pd.DataFrame:
    data_path = Path(__file__).parent / "data" / "titanic_train_clean.csv"
    return pd.read_csv(data_path)


df = load_data()
y = df["Survived"]
X = df.drop(columns=["PassengerId", "Survived"])

(tab_eval,) = st.tabs(["Model Evaluation"])

with tab_eval:
    st.header("Model Evaluation")

    # 1. Let the user choose how deep the decision tree is allowed to grow.
    st.subheader("1. Model settings")
    max_depth = st.slider("max_depth", min_value=1, max_value=15, value=5)
    st.caption(
        'Model: DecisionTreeClassifier(max_depth=max_depth, criterion="entropy", random_state=42)'
    )

    # A fresh, untrained tree with the chosen max_depth. Copies of this are
    # fit wherever a model is needed below (holdout, each CV fold, each
    # bootstrap round) so every fit starts from a clean model.
    def make_tree() -> DecisionTreeClassifier:
        return DecisionTreeClassifier(
            max_depth=max_depth, criterion="entropy", random_state=42
        )

    # This holdout split is always computed, no matter which validation
    # method is chosen below. It is the split the confusion matrix,
    # precision/recall/F1, and cost total are always based on.
    st.subheader("2. Validation method")
    test_size = st.slider(
        "Test size (fraction held out for testing)",
        min_value=0.10,
        max_value=0.50,
        value=0.30,
        step=0.01,
    )
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, stratify=y, random_state=1
    )
    holdout_tree = make_tree()
    holdout_tree.fit(X_train, y_train)
    y_pred = holdout_tree.predict(X_test)
    holdout_accuracy = (y_pred == y_test).mean()
    st.caption(
        "Split: train_test_split(X, y, test_size=test_size, stratify=y, random_state=1)"
    )

    # The validation method choice only changes which accuracy number is
    # displayed here. The holdout split above is always used for items 3 and 4.
    method = st.radio(
        "Choose how to measure accuracy",
        ["Holdout", "K-fold cross-validation", "Bootstrap"],
    )

    if method == "Holdout":
        st.metric("Holdout accuracy", pct(holdout_accuracy))
        st.caption("accuracy_score(y_test, y_pred)  (equivalent to (y_pred == y_test).mean())")

    elif method == "K-fold cross-validation":
        k = st.slider("k (number of folds)", min_value=3, max_value=10, value=5)
        skf = StratifiedKFold(n_splits=k, shuffle=True, random_state=1)
        cv_scores = cross_val_score(make_tree(), X, y, cv=skf)
        col1, col2 = st.columns(2)
        col1.metric("Mean accuracy", pct(cv_scores.mean()))
        col2.metric("Standard deviation", pct(cv_scores.std()))
        st.caption(
            "StratifiedKFold(n_splits=k, shuffle=True, random_state=1); "
            "cross_val_score(DecisionTreeClassifier(...), X, y, cv=skf)"
        )

    else:  # Bootstrap
        rounds = st.slider("Number of bootstrap rounds", min_value=10, max_value=200, value=100)
        boot_accuracies = []
        for b in range(rounds):
            # Resample the full data with replacement; rows left out are "out-of-bag".
            X_boot, y_boot = resample(X, y, replace=True, n_samples=len(X), random_state=b)
            oob_idx = np.setdiff1d(X.index, X_boot.index)
            if len(oob_idx) == 0:
                continue
            boot_tree = make_tree()
            boot_tree.fit(X_boot, y_boot)
            oob_pred = boot_tree.predict(X.loc[oob_idx])
            boot_accuracies.append((oob_pred == y.loc[oob_idx]).mean())
        boot_accuracies = np.array(boot_accuracies)
        lower, upper = np.percentile(boot_accuracies, [2.5, 97.5])
        col1, col2 = st.columns(2)
        col1.metric("Mean out-of-bag accuracy", pct(boot_accuracies.mean()))
        col2.metric("Middle 95% range", f"{pct(lower)} - {pct(upper)}")
        st.caption(
            "resample(X, y, replace=True, n_samples=len(X), random_state=b); "
            "accuracy on the rows left out of the resample (out-of-bag)"
        )

    # 3. Confusion matrix and precision/recall/F1, always from the holdout split above.
    st.subheader("3. Confusion matrix (holdout split)")
    cm = confusion_matrix(y_test, y_pred, labels=[1, 0])
    cm_table = pd.DataFrame(
        cm,
        index=["Actual: Survived (1)", "Actual: Did not survive (0)"],
        columns=["Predicted: Survived (1)", "Predicted: Did not survive (0)"],
    )
    st.dataframe(cm_table)
    st.caption("confusion_matrix(y_test, y_pred, labels=[1, 0])")

    precision = precision_score(y_test, y_pred, pos_label=1)
    recall = recall_score(y_test, y_pred, pos_label=1)
    f1 = f1_score(y_test, y_pred, pos_label=1)
    col1, col2, col3 = st.columns(3)
    col1.metric("Precision (positive = 1)", pct(precision))
    col2.metric("Recall (positive = 1)", pct(recall))
    col3.metric("F1 score (positive = 1)", pct(f1))
    st.caption(
        "precision_score(y_test, y_pred, pos_label=1), "
        "recall_score(y_test, y_pred, pos_label=1), "
        "f1_score(y_test, y_pred, pos_label=1)"
    )

    # 4. Let the user price false positives and false negatives, then total the cost.
    st.subheader("4. Cost of the holdout predictions")
    cost_fp = st.number_input("Cost of a false positive", min_value=0.0, value=1.0, step=1.0)
    cost_fn = st.number_input("Cost of a false negative", min_value=0.0, value=1.0, step=1.0)

    # With labels=[1, 0], row 0 = actual 1, row 1 = actual 0.
    false_negatives = cm[0, 1]  # actual Survived, predicted not survived
    false_positives = cm[1, 0]  # actual not survived, predicted Survived
    total_cost = false_positives * cost_fp + false_negatives * cost_fn

    st.metric("Total cost", f"{total_cost:,.2f}")
    st.caption(
        "Total cost = (false positives x cost of a false positive) "
        "+ (false negatives x cost of a false negative), "
        "using the counts from the confusion matrix above."
    )
