"""Evaluate a decision tree classifier on the WineQuality dataset."""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split, StratifiedKFold, cross_val_score
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    ConfusionMatrixDisplay,
)

# Class order used everywhere below: Good, then Poor
CLASS_ORDER = ["Good", "Poor"]

# Load the data and split it into features (X) and target (y)
data = pd.read_csv("../WineQuality.csv")
X = data.drop(columns=["quality"])
y = data["quality"]

# Stratified 70/30 holdout split, random_state=1
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.3, stratify=y, random_state=1
)

# Train the decision tree on the training split
model = DecisionTreeClassifier(max_depth=5, random_state=1)
model.fit(X_train, y_train)
y_pred = model.predict(X_test)

# Holdout metrics: accuracy overall, precision/recall/F1 for the "Good" class
accuracy = accuracy_score(y_test, y_pred)
precision_good = precision_score(y_test, y_pred, pos_label="Good")
recall_good = recall_score(y_test, y_pred, pos_label="Good")
f1_good = f1_score(y_test, y_pred, pos_label="Good")

# Confusion matrix with rows/columns ordered Good, Poor
cm = confusion_matrix(y_test, y_pred, labels=CLASS_ORDER)
print("Confusion matrix (rows = actual, columns = predicted; order: Good, Poor)")
print(pd.DataFrame(cm, index=CLASS_ORDER, columns=CLASS_ORDER))

# Save the confusion matrix as a PNG in this folder
disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=CLASS_ORDER)
disp.plot(cmap="Blues", values_format="d")
plt.title("Confusion Matrix")
plt.tight_layout()
plt.savefig("confusion_matrix.png")
plt.close()

# Total cost using the given cost matrix (rows actual, columns predicted; order: Good, Poor)
cost_matrix = np.array([[0, 2], [10, 0]])
total_cost = int(np.sum(cm * cost_matrix))

# 5-fold stratified cross validation on the full dataset
cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=1)
cv_scores = cross_val_score(model, X, y, cv=cv, scoring="accuracy")
cv_mean = cv_scores.mean()
cv_std = cv_scores.std()

# Print a short results table, with every rate as a percentage to two decimals
print("\nResults")
print(f"{'Metric':<25}{'Value':>15}")
print(f"{'Holdout accuracy':<25}{accuracy * 100:>14.2f}%")
print(f"{'Precision (Good)':<25}{precision_good * 100:>14.2f}%")
print(f"{'Recall (Good)':<25}{recall_good * 100:>14.2f}%")
print(f"{'F1 score (Good)':<25}{f1_good * 100:>14.2f}%")
print(f"{'Total cost':<25}{total_cost:>15}")
print(f"{'CV accuracy (mean)':<25}{cv_mean * 100:>14.2f}%")
print(f"{'CV accuracy (+/- std)':<25}{cv_std * 100:>14.2f}%")
