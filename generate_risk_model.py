"""
Quick model training to predict `default_history` (binary) using a logistic regression.
Saves metrics to analysis/model_metrics.txt and a confusion matrix plot.
"""
import os
import pandas as pd
import numpy as np

OUTDIR = 'analysis'
os.makedirs(OUTDIR, exist_ok=True)

try:
    from sklearn.model_selection import train_test_split
    from sklearn.linear_model import LogisticRegression
    from sklearn.metrics import accuracy_score, precision_score, recall_score, roc_auc_score, confusion_matrix
    import matplotlib.pyplot as plt
    import seaborn as sns
except Exception as e:
    print('Required ML packages not installed:', e)
    raise

# Load data
df = pd.read_csv('data_company_risk_500.csv')

# Prepare features: select numeric columns except target
numeric = df.select_dtypes(include=[np.number]).copy()
if 'default_history' not in numeric.columns:
    raise RuntimeError('default_history column missing')

# Drop default_probability and risk_score to avoid leakage for this quick demo
features = numeric.drop(columns=['default_probability', 'risk_score'], errors='ignore')
# Ensure target
y = features.pop('default_history')

# Fill or drop NaNs
features = features.fillna(features.median())

# Train-test split
X_train, X_test, y_train, y_test = train_test_split(features, y, test_size=0.25, random_state=42, stratify=y)

# Train logistic regression (with balanced class weight because default is rare)
model = LogisticRegression(max_iter=1000, class_weight='balanced')
model.fit(X_train, y_train)

# Predict
y_pred = model.predict(X_test)
y_proba = model.predict_proba(X_test)[:,1]

# Metrics
acc = accuracy_score(y_test, y_pred)
prec = precision_score(y_test, y_pred, zero_division=0)
rec = recall_score(y_test, y_pred, zero_division=0)
auc = roc_auc_score(y_test, y_proba)

metrics_path = os.path.join(OUTDIR, 'model_metrics.txt')
with open(metrics_path, 'w') as fh:
    fh.write(f"accuracy: {acc:.4f}\n")
    fh.write(f"precision: {prec:.4f}\n")
    fh.write(f"recall: {rec:.4f}\n")
    fh.write(f"roc_auc: {auc:.4f}\n")

print('\nModel metrics:')
print(open(metrics_path).read())

# Confusion matrix
cm = confusion_matrix(y_test, y_pred)
plt.figure(figsize=(5,4))
ax = sns.heatmap(cm, annot=True, fmt='d', cbar=False)
ax.set_xlabel('Predicted')
ax.set_ylabel('Actual')
plt.title('Confusion Matrix')
conf_path = os.path.join(OUTDIR, 'confusion_matrix.png')
plt.tight_layout()
plt.savefig(conf_path, dpi=150)
plt.close()

print('Saved confusion matrix to', conf_path)

# Save model coefficients snapshot
coef_path = os.path.join(OUTDIR, 'model_coefficients.csv')
coefs = pd.Series(model.coef_[0], index=features.columns).sort_values(key=abs, ascending=False)
coefs.to_csv(coef_path, header=['coefficient'])
print('Saved coefficients to', coef_path)
