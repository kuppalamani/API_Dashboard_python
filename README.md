# 📡 API Usage Analytics Dashboard

A production-grade Streamlit dashboard for monitoring API call data across tenants and connectors.

---

## 🗂 Project Structure

```
api_dashboard/
├── dashboard.py              # Main Streamlit app
├── generate_sample_data.py   # Creates a demo Excel workbook
├── requirements.txt          # Python dependencies
├── README.md                 # This file
└── data/
    └── sample_api_usage.xlsx # (generated) Demo data
```

---

## 🚀 Quick Start

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. (Optional) Generate sample data

```bash
python generate_sample_data.py
```

This creates `data/sample_api_usage.xlsx` with 10 tenants, 9 connectors,
and 90 days of realistic API call data.

### 3. Run the dashboard

```bash
streamlit run dashboard.py
```

Open your browser at **http://localhost:8501**

---

## 📊 Excel File Format

### Sheet 1 — API Usage Data

| Tenant Name | Connector Name | OID     | 2024-01-01 | 2024-01-02 | … |
|-------------|----------------|---------|-----------|-----------|---|
| Acme Corp   | Salesforce CRM | OID1001 | 120       | 135       | … |
| Acme Corp   | HubSpot        | OID1001 | 80        | 90        | … |

- First three columns are fixed identifiers
- Remaining columns are date headers (any parseable date format)
- Values are integer API call counts

### Sheet 2 — Tenant Mapping

| Tenant Name | Customer Email        | OID     |
|-------------|-----------------------|---------|
| Acme Corp   | admin@acme.com        | OID1001 |

---

## 🎛 Dashboard Features

### KPI Cards
- Total API Calls
- Daily Average
- Active Tenants
- Total Connectors
- This Month Total

### Visualizations
| Chart | Description |
|---|---|
| Daily Trend | Line chart with 7-day rolling average |
| Monthly Usage | Bar + trend overlay |
| Top Tenants | Horizontal bar ranking |
| Top Connectors | Horizontal bar ranking |
| Connector Mix | Stacked bar per tenant |
| Usage Heatmap | Tenant × Date matrix |
| Growth Trend | Weekly WoW growth |
| Connector Comparison | Multi-line 7d smoothed |
| Peak Detection | Avg calls by day of week |
| API Distribution | Donut chart by connector |

### Advanced Analytics
- **Spike Detection** — Z-score based anomaly alerts (configurable threshold)
- **Tenant Segmentation** — Low / Medium / High usage classification
- **Active Tenants Table** — Sortable summary with last-seen dates

### Filters (Sidebar)
- Tenant multi-select
- Connector multi-select
- Date range picker
- Customer email search
- Spike threshold slider (σ)
- Top N items slider

---

## ⚙️ Technical Details

- **Data pipeline**: Wide → Long format melt, datetime normalization, OID join
- **Caching**: `@st.cache_data` on data loading and transformation
- **Charts**: Plotly with dark theme, responsive layout
- **Styling**: Custom CSS with CSS variables, DM Sans + IBM Plex Mono fonts
- **Zero external API calls**: All data processed locally

---

## 📦 Requirements

```
streamlit>=1.35.0
pandas>=2.0.0
numpy>=1.24.0
plotly>=5.18.0
openpyxl>=3.1.0
xlrd>=2.0.1
```
