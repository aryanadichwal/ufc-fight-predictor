from data_processing import matchups
from  data_processing import diff_cols

from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
from sklearn.metrics import (
    confusion_matrix,
    classification_report,
    roc_auc_score,
    accuracy_score
)

matchups = matchups.sort_values("date").reset_index(drop=True)

train , test = train_test_split(matchups, shuffle=False, test_size=0.2)

x_train , y_train = train[diff_cols], train["won"]

x_test , y_test = test[diff_cols], test["won"]

# print(f"Train: {len(train)} fights, {train['date'].min().date()} to {train['date'].max().date()}")
# print(f"Test:  {len(test)} fights, {test['date'].min().date()} to {test['date'].max().date()}")
# print(f"Train win rate: {y_train.mean():.3f} | Test win rate: {y_test.mean():.3f}")

log_reg_pipe = make_pipeline(StandardScaler(), LogisticRegression())
log_reg_pipe.fit(x_train, y_train)
preds = log_reg_pipe.predict(x_test)
# print(preds)


final_preds = log_reg_pipe.predict(x_test)
final_probs = log_reg_pipe.predict_proba(x_test)[:, 1]

# print(confusion_matrix(y_test, final_preds))
# print(classification_report(y_test, final_preds, target_names=['Lost','Won']))
# print("ROC-AUC:", round(roc_auc_score(y_test, final_probs), 3))

