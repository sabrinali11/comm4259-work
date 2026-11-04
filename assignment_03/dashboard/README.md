# Assignment 3: Model Evaluation Dashboard

A Streamlit app for exploring how a decision tree's depth and the choice of
validation method affect accuracy on the Titanic survival dataset, and for
seeing a confusion matrix, precision/recall/F1, and a cost total for a
holdout split. The app makes no decisions on its own and uses no AI model —
every number shown is the output of a labeled scikit-learn function call.

## How to run it

From inside this folder (`assignment_03/dashboard/`):

```
streamlit run app.py
```

## What it does

In the single "Model Evaluation" tab, you can:

1. Set the decision tree's `max_depth` with a slider.
2. Choose a validation method (holdout, k-fold cross-validation, or
   bootstrap) and see its accuracy.
3. See the confusion matrix, precision, recall, and F1 score for a holdout
   split (Survived = 1 is the positive class).
4. Enter the cost of a false positive and a false negative and see the
   total cost of the holdout predictions.
