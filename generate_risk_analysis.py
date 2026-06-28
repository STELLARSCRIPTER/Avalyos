"""
Exploratory analysis for data_company_risk_500.csv
Generates:
 - printed summary statistics
 - correlation matrix (printed)
 - saves plots to ./analysis/
 - writes top 20 risk companies to ./analysis/top_risk_companies.csv
"""
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

INFILE = 'data_company_risk_500.csv'
OUTDIR = 'analysis'
os.makedirs(OUTDIR, exist_ok=True)

df = pd.read_csv(INFILE)

# Basic summary
summary = df.describe(include='all')
print('\n=== DATAFRAME SUMMARY (describe) ===\n')
print(summary)

# Risk distribution
print('\n=== RISK_SCORE DISTRIBUTION ===\n')
print(df['risk_score'].describe())

# Correlations (numeric columns)
numeric = df.select_dtypes(include=[np.number])
corr = numeric.corr()
print('\n=== CORRELATION MATRIX (top-right snippet) ===\n')
print(corr.round(3))

# Save correlation heatmap
plt.figure(figsize=(12,10))
sns.heatmap(corr, annot=True, fmt='.2f', cmap='vlag', center=0)
plt.title('Correlation matrix')
plt.tight_layout()
heatmap_path = os.path.join(OUTDIR, 'correlation_heatmap.png')
plt.savefig(heatmap_path, dpi=150)
plt.close()

# Histogram of risk_score
plt.figure(figsize=(8,4))
sns.histplot(df['risk_score'], bins=30, kde=True, color='crimson')
plt.title('Risk Score Distribution')
plt.xlabel('risk_score')
plt.tight_layout()
hist_path = os.path.join(OUTDIR, 'risk_score_histogram.png')
plt.savefig(hist_path, dpi=150)
plt.close()

# Scatter: risk_score vs debt/assets
if 'debt' in df.columns and 'assets' in df.columns:
    df['debt_to_assets'] = df['debt'] / df['assets'].replace({0: np.nan})
    plt.figure(figsize=(7,5))
    sns.scatterplot(x='debt_to_assets', y='risk_score', data=df, alpha=0.7)
    plt.title('Risk Score vs Debt-to-Assets')
    plt.xlabel('debt_to_assets')
    plt.ylabel('risk_score')
    plt.tight_layout()
    scatter_path = os.path.join(OUTDIR, 'risk_vs_debt_to_assets.png')
    plt.savefig(scatter_path, dpi=150)
    plt.close()

# Top risk companies
top_n = 20
top = df.sort_values('risk_score', ascending=False).head(top_n)
top_csv = os.path.join(OUTDIR, 'top_risk_companies.csv')
top.to_csv(top_csv, index=False)

print(f"\nSaved plots: {heatmap_path}, {hist_path}, {scatter_path if 'scatter_path' in locals() else 'N/A'}")
print(f"Top {top_n} risk companies written to: {top_csv}\n")

# Print a concise top table to stdout
print('\n=== TOP 20 RISK COMPANIES (preview) ===\n')
print(top[['company_id','company_name','revenue','debt','assets','risk_score','default_probability']].to_string(index=False))
