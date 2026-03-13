"""
generate_sample_data.py
=======================
Generates a realistic sample Excel workbook for testing the API Usage Dashboard.

Run:
    python generate_sample_data.py

Output:
    data/sample_api_usage.xlsx
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os

os.makedirs("data", exist_ok=True)

np.random.seed(42)

# ── Config ─────────────────────────────────────────────────────
TENANTS = [
    "Acme Corp", "Globex Inc", "Initech", "Umbrella Ltd",
    "Massive Dynamics", "Soylent Co", "Buy N Large",
    "Vault-Tec Corp", "Cyberdyne Systems", "Weyland-Yutani",
]
CONNECTORS = [
    "Salesforce CRM", "HubSpot Marketing", "Stripe Payments",
    "SendGrid Email", "Twilio SMS", "Slack Notifications",
    "Jira Ticketing", "AWS S3 Storage", "Google Analytics",
]
EMAILS = [
    "admin@acme.com", "ops@globexinc.com", "it@initech.com",
    "platform@umbrellaltd.com", "dev@massivedyn.com",
    "api@soylentco.com", "tech@buynlarge.com",
    "it@vault-tec.com", "devops@cyberdyne.io", "api@weyland-yutani.com",
]
OIDS = [f"OID{10000 + i}" for i in range(len(TENANTS))]

# Date range: last 90 days
end_date = datetime.today()
start_date = end_date - timedelta(days=89)
dates = pd.date_range(start_date, end_date, freq='D')
date_cols = [d.strftime('%Y-%m-%d') for d in dates]

# ── Sheet 1: API Usage Data ─────────────────────────────────────
rows = []
for i, tenant in enumerate(TENANTS):
    n_connectors = np.random.randint(2, 5)
    chosen_connectors = np.random.choice(CONNECTORS, n_connectors, replace=False)

    for connector in chosen_connectors:
        base = np.random.randint(50, 600)
        trend = np.random.uniform(-0.3, 1.8)

        daily_calls = []
        for j, d in enumerate(dates):
            weekday_factor = 0.25 if d.weekday() >= 5 else 1.0
            seasonal = base * (1 + trend * j / 100)
            noise = np.random.normal(0, base * 0.12)
            # Random spike: ~2% chance
            spike = base * np.random.uniform(2.5, 5.0) if np.random.random() < 0.02 else 0
            value = max(0, int(seasonal * weekday_factor + noise + spike))
            daily_calls.append(value)

        row = {
            'Tenant Name': tenant,
            'Connector Name': connector,
            'OID': OIDS[i],
        }
        for k, dc in enumerate(date_cols):
            row[dc] = daily_calls[k]

        rows.append(row)

df_usage = pd.DataFrame(rows)

# ── Sheet 2: Tenant Mapping ─────────────────────────────────────
df_mapping = pd.DataFrame({
    'Tenant Name': TENANTS,
    'Customer Email': EMAILS,
    'OID': OIDS,
})

# ── Write Excel ─────────────────────────────────────────────────
output_path = "data/sample_api_usage.xlsx"
with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
    df_usage.to_excel(writer, sheet_name='API Usage Data', index=False)
    df_mapping.to_excel(writer, sheet_name='Tenant Mapping', index=False)

print(f"✅  Sample data written to: {output_path}")
print(f"    Sheet 1 - API Usage Data:  {len(df_usage)} rows × {len(df_usage.columns)} columns")
print(f"    Sheet 2 - Tenant Mapping:  {len(df_mapping)} rows")
print(f"    Date range: {date_cols[0]} → {date_cols[-1]}")
print(f"    Tenants: {len(TENANTS)}, Connectors: {len(CONNECTORS)}")
