"""
API Usage Analytics Dashboard
==============================
A production-grade Streamlit dashboard for monitoring API call data
across tenants and connectors from an Excel workbook.

Run with:
    streamlit run dashboard.py
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os
from datetime import datetime, timedelta

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="API Usage Analytics",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# CUSTOM CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
    /* Import fonts */
    @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=DM+Sans:wght@300;400;500;700&display=swap');

    /* Root theme */
    :root {
        --bg-primary: #0f1117;
        --bg-card: #1a1d2e;
        --bg-card-hover: #1f2340;
        --accent-cyan: #00d4ff;
        --accent-purple: #8b5cf6;
        --accent-green: #10b981;
        --accent-amber: #f59e0b;
        --accent-rose: #f43f5e;
        --text-primary: #e2e8f0;
        --text-muted: #64748b;
        --border: #2d3161;
    }

    /* Global */
    .stApp { background-color: var(--bg-primary); }
    html, body, [class*="css"] {
        font-family: 'DM Sans', sans-serif;
        color: var(--text-primary);
    }

    /* Hide Streamlit chrome */
    #MainMenu, footer, header { visibility: hidden; }
    .block-container { padding: 1.5rem 2rem 2rem 2rem; }

    /* KPI Cards */
    .kpi-grid {
        display: grid;
        grid-template-columns: repeat(5, 1fr);
        gap: 16px;
        margin-bottom: 24px;
    }
    .kpi-card {
        background: var(--bg-card);
        border: 1px solid var(--border);
        border-radius: 12px;
        padding: 20px;
        position: relative;
        overflow: hidden;
        transition: transform 0.2s, border-color 0.2s;
    }
    .kpi-card:hover { transform: translateY(-2px); border-color: var(--accent-cyan); }
    .kpi-card::before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 3px;
        background: var(--accent-color, var(--accent-cyan));
    }
    .kpi-label {
        font-size: 11px;
        font-weight: 600;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        color: var(--text-muted);
        margin-bottom: 8px;
    }
    .kpi-value {
        font-family: 'IBM Plex Mono', monospace;
        font-size: 28px;
        font-weight: 600;
        color: var(--text-primary);
        line-height: 1;
    }
    .kpi-sub {
        font-size: 12px;
        color: var(--text-muted);
        margin-top: 6px;
    }
    .kpi-icon {
        position: absolute;
        top: 20px; right: 20px;
        font-size: 22px;
        opacity: 0.25;
    }

    /* Section headers */
    .section-header {
        font-size: 13px;
        font-weight: 700;
        letter-spacing: 0.1em;
        text-transform: uppercase;
        color: var(--text-muted);
        border-bottom: 1px solid var(--border);
        padding-bottom: 8px;
        margin: 24px 0 16px 0;
    }

    /* Chart containers */
    .chart-card {
        background: var(--bg-card);
        border: 1px solid var(--border);
        border-radius: 12px;
        padding: 20px;
    }
    .chart-title {
        font-size: 14px;
        font-weight: 600;
        color: var(--text-primary);
        margin-bottom: 4px;
    }
    .chart-subtitle {
        font-size: 12px;
        color: var(--text-muted);
        margin-bottom: 16px;
    }

    /* Sidebar */
    .css-1d391kg, [data-testid="stSidebar"] {
        background-color: #12152a !important;
        border-right: 1px solid var(--border);
    }
    .sidebar-title {
        font-family: 'IBM Plex Mono', monospace;
        font-size: 14px;
        font-weight: 600;
        color: var(--accent-cyan);
        letter-spacing: 0.05em;
        margin-bottom: 4px;
    }

    /* Selectbox/multiselect tweaks */
    .stMultiSelect [data-baseweb="tag"] {
        background-color: #1e3a5f !important;
        border: 1px solid #3b82f6 !important;
    }

    /* Alert badges */
    .spike-badge {
        display: inline-block;
        background: rgba(244,63,94,0.15);
        border: 1px solid var(--accent-rose);
        color: var(--accent-rose);
        border-radius: 6px;
        padding: 4px 10px;
        font-size: 12px;
        font-family: 'IBM Plex Mono', monospace;
        margin: 3px;
    }
    .low-badge {
        background: rgba(16,185,129,0.15);
        border-color: var(--accent-green);
        color: var(--accent-green);
    }
    .med-badge {
        background: rgba(245,158,11,0.15);
        border-color: var(--accent-amber);
        color: var(--accent-amber);
    }
    .high-badge {
        background: rgba(244,63,94,0.15);
        border-color: var(--accent-rose);
        color: var(--accent-rose);
    }
    .segment-row {
        display: flex;
        align-items: center;
        padding: 8px 0;
        border-bottom: 1px solid var(--border);
    }
    .segment-name { flex: 1; font-size: 13px; }
    .segment-calls { font-family: 'IBM Plex Mono', monospace; font-size: 12px; color: var(--text-muted); }

    /* Dataframe tweaks */
    .stDataFrame { border-radius: 8px; overflow: hidden; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# DATA GENERATION (for demo if no file uploaded)
# ─────────────────────────────────────────────
@st.cache_data
def generate_demo_data():
    """Generate realistic demo API usage data."""
    np.random.seed(42)

    tenants = ["Acme Corp", "Globex Inc", "Initech", "Umbrella Ltd", "Massive Dyn",
               "Soylent Co", "Buy N Large", "Vault-Tec", "Cyberdyne", "Weyland-Yutani"]
    connectors = ["Salesforce CRM", "HubSpot", "Stripe Payments", "SendGrid Email",
                  "Twilio SMS", "Slack Notify", "Jira Tickets", "AWS S3", "Google Analytics"]
    emails = [f"admin@{t.lower().replace(' ', '').replace('.', '')}.com" for t in tenants]
    oids = [f"OID{10000+i}" for i in range(len(tenants))]

    # Date range: last 90 days
    end_date = datetime.today()
    start_date = end_date - timedelta(days=89)
    dates = pd.date_range(start_date, end_date, freq='D')
    date_cols = [d.strftime('%Y-%m-%d') for d in dates]

    rows = []
    for i, tenant in enumerate(tenants):
        # Each tenant uses 2-4 connectors
        n_connectors = np.random.randint(2, 5)
        chosen = np.random.choice(connectors, n_connectors, replace=False)
        for connector in chosen:
            base = np.random.randint(50, 500)
            trend = np.random.uniform(-0.5, 1.5)
            # Weekly seasonality + random spikes
            calls = []
            for j, d in enumerate(dates):
                weekday_factor = 0.3 if d.weekday() >= 5 else 1.0
                seasonal = base * (1 + trend * j / 100)
                noise = np.random.normal(0, base * 0.15)
                spike = base * 3 if np.random.random() < 0.02 else 0
                v = max(0, int(seasonal * weekday_factor + noise + spike))
                calls.append(v)
            row = {
                'Tenant Name': tenant,
                'Connector Name': connector,
                'OID': oids[i],
            }
            for k, dc in enumerate(date_cols):
                row[dc] = calls[k]
            rows.append(row)

    df_usage = pd.DataFrame(rows)

    df_mapping = pd.DataFrame({
        'Tenant Name': tenants,
        'Customer Email': emails,
        'OID': oids,
    })

    return df_usage, df_mapping


# ─────────────────────────────────────────────
# DATA LOADING
# ─────────────────────────────────────────────
@st.cache_data
def load_excel(file_bytes):
    xl = pd.ExcelFile(file_bytes)
    sheet_names = xl.sheet_names

    df_usage = xl.parse(sheet_names[0])
    df_mapping = xl.parse(sheet_names[1]) if len(sheet_names) > 1 else pd.DataFrame()

    return df_usage, df_mapping


# ─────────────────────────────────────────────
# DATA TRANSFORMATION
# ─────────────────────────────────────────────
@st.cache_data
def transform_data(df_usage: pd.DataFrame, df_mapping: pd.DataFrame):
    """
    Normalise wide-format usage data into a long time-series,
    join with tenant mapping, and compute derived metrics.
    """
    # ── Normalize column names: strip whitespace ──────────────────
    df_usage.columns = df_usage.columns.astype(str).str.strip()
    if not df_mapping.empty:
        df_mapping.columns = df_mapping.columns.astype(str).str.strip()

    # ── Auto-detect fixed (non-date) columns ──────────────────────
    # First 3 non-date columns are treated as fixed identifiers
    # A column is a "date column" if it can be parsed as a date
    def is_date_col(col_name):
        try:
            pd.to_datetime(col_name)
            return True
        except Exception:
            return False

    all_cols = list(df_usage.columns)
    date_cols = [c for c in all_cols if is_date_col(str(c))]
    fixed_cols = [c for c in all_cols if c not in date_cols]

    # Standardise fixed column names for downstream use
    col_rename = {}
    for col in fixed_cols:
        lower = col.lower().replace('_', ' ').strip()
        if 'tenant' in lower:
            col_rename[col] = 'Tenant Name'
        elif 'connector' in lower:
            col_rename[col] = 'Connector Name'
        elif 'oid' in lower:
            col_rename[col] = 'OID'

    df_usage = df_usage.rename(columns=col_rename)
    fixed_cols = [col_rename.get(c, c) for c in fixed_cols]

    # Ensure all expected fixed cols exist
    for req in ['Tenant Name', 'Connector Name', 'OID']:
        if req not in df_usage.columns:
            df_usage[req] = 'Unknown'
    fixed_cols = ['Tenant Name', 'Connector Name', 'OID']

    # ── Melt to long format ───────────────────────────────────────
    df_long = df_usage.melt(
        id_vars=fixed_cols,
        value_vars=date_cols,
        var_name='Date',
        value_name='API Calls',
    )

    # Parse dates robustly
    df_long['Date'] = pd.to_datetime(df_long['Date'], errors='coerce')
    df_long = df_long.dropna(subset=['Date'])
    df_long['API Calls'] = pd.to_numeric(df_long['API Calls'], errors='coerce').fillna(0).astype(int)

    # Derived date features
    df_long['Year'] = df_long['Date'].dt.year
    df_long['Month'] = df_long['Date'].dt.to_period('M').astype(str)
    df_long['Week'] = df_long['Date'].dt.isocalendar().week
    df_long['DayOfWeek'] = df_long['Date'].dt.day_name()

    # ── Join with mapping ─────────────────────────────────────────
    if not df_mapping.empty:
        # Normalize mapping column names
        map_rename = {}
        for col in df_mapping.columns:
            lower = str(col).lower().replace('_', ' ').strip()
            if 'tenant' in lower:
                map_rename[col] = 'Tenant Name'
            elif 'email' in lower:
                map_rename[col] = 'Customer Email'
            elif 'oid' in lower:
                map_rename[col] = 'OID'
        df_mapping = df_mapping.rename(columns=map_rename)

        if 'OID' in df_mapping.columns:
            extra_cols = [c for c in df_mapping.columns if c not in ['OID', 'Tenant Name', 'Connector Name']]
            df_long = df_long.merge(
                df_mapping[['OID'] + extra_cols],
                on='OID',
                how='left',
                suffixes=('', '_mapped'),
            )

    if 'Customer Email' not in df_long.columns:
        df_long['Customer Email'] = 'N/A'

    df_long = df_long.sort_values('Date').reset_index(drop=True)
    return df_long


# ─────────────────────────────────────────────
# ANALYTICS HELPERS
# ─────────────────────────────────────────────
def kpi_metrics(df: pd.DataFrame):
    total_calls = int(df['API Calls'].sum())
    daily_avg = round(df.groupby('Date')['API Calls'].sum().mean(), 1)
    active_tenants = df[df['API Calls'] > 0]['Tenant Name'].nunique()
    total_connectors = df['Connector Name'].nunique()

    # This-month calls
    latest = df['Date'].max()
    this_month = df[df['Month'] == str(latest.to_period('M'))]['API Calls'].sum()

    return {
        'total_calls': total_calls,
        'daily_avg': daily_avg,
        'active_tenants': active_tenants,
        'total_connectors': total_connectors,
        'this_month': int(this_month),
    }


def detect_spikes(df: pd.DataFrame, z_threshold: float = 2.5):
    """Return rows where daily tenant-connector calls exceed mean + z * std."""
    grp = df.groupby(['Tenant Name', 'Connector Name', 'Date'])['API Calls'].sum().reset_index()
    stats = grp.groupby(['Tenant Name', 'Connector Name'])['API Calls'].agg(['mean', 'std']).reset_index()
    merged = grp.merge(stats, on=['Tenant Name', 'Connector Name'])
    merged['z_score'] = (merged['API Calls'] - merged['mean']) / merged['std'].replace(0, 1)
    spikes = merged[merged['z_score'] > z_threshold].copy()
    spikes['spike_pct'] = ((spikes['API Calls'] - spikes['mean']) / spikes['mean'].replace(0, 1) * 100).round(1)
    return spikes.sort_values('z_score', ascending=False).head(20)


def segment_tenants(df: pd.DataFrame):
    """Segment tenants into Low / Medium / High usage buckets."""
    tenant_totals = df.groupby('Tenant Name')['API Calls'].sum().reset_index()
    q33 = tenant_totals['API Calls'].quantile(0.33)
    q66 = tenant_totals['API Calls'].quantile(0.66)

    def seg(v):
        if v <= q33:
            return 'Low'
        elif v <= q66:
            return 'Medium'
        return 'High'

    tenant_totals['Segment'] = tenant_totals['API Calls'].apply(seg)
    return tenant_totals


# ─────────────────────────────────────────────
# PLOTLY THEME
# ─────────────────────────────────────────────
PLOTLY_LAYOUT = dict(
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    font=dict(family='DM Sans', color='#94a3b8', size=12),
    margin=dict(l=10, r=10, t=30, b=10),
    legend=dict(
        bgcolor='rgba(26,29,46,0.8)',
        bordercolor='#2d3161',
        borderwidth=1,
        font=dict(size=11),
    ),
    xaxis=dict(
        gridcolor='#1e2240',
        linecolor='#2d3161',
        tickfont=dict(size=11),
    ),
    yaxis=dict(
        gridcolor='#1e2240',
        linecolor='#2d3161',
        tickfont=dict(size=11),
    ),
)

COLOR_SEQ = [
    '#00d4ff', '#8b5cf6', '#10b981', '#f59e0b', '#f43f5e',
    '#3b82f6', '#ec4899', '#14b8a6', '#a78bfa', '#34d399',
]


# ─────────────────────────────────────────────
# CHART BUILDERS
# ─────────────────────────────────────────────
def chart_daily_trend(df):
    daily = df.groupby('Date')['API Calls'].sum().reset_index()
    # 7-day rolling avg
    daily['Rolling 7d Avg'] = daily['API Calls'].rolling(7, min_periods=1).mean().round(1)

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=daily['Date'], y=daily['API Calls'],
        mode='lines', name='Daily Calls',
        line=dict(color='#00d4ff', width=1.5),
        fill='tozeroy',
        fillcolor='rgba(0,212,255,0.06)',
    ))
    fig.add_trace(go.Scatter(
        x=daily['Date'], y=daily['Rolling 7d Avg'],
        mode='lines', name='7-Day Avg',
        line=dict(color='#8b5cf6', width=2, dash='dot'),
    ))
    fig.update_layout(**PLOTLY_LAYOUT, height=280,
                      title=dict(text='Daily API Calls', font=dict(size=14, color='#e2e8f0')))
    fig.update_xaxes(showgrid=True)
    fig.update_yaxes(showgrid=True)
    return fig


def chart_monthly(df):
    monthly = df.groupby('Month')['API Calls'].sum().reset_index().sort_values('Month')
    monthly['MoM_pct'] = monthly['API Calls'].pct_change() * 100

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=monthly['Month'], y=monthly['API Calls'],
        marker_color='#8b5cf6',
        marker_line_width=0,
        name='Monthly Total',
    ))
    fig.add_trace(go.Scatter(
        x=monthly['Month'], y=monthly['API Calls'],
        mode='lines+markers',
        line=dict(color='#00d4ff', width=1.5),
        marker=dict(size=6),
        name='Trend',
        yaxis='y',
    ))
    fig.update_layout(**PLOTLY_LAYOUT, height=280,
                      title=dict(text='Monthly API Usage', font=dict(size=14, color='#e2e8f0')),
                      bargap=0.3)
    return fig


def chart_top_tenants(df, n=10):
    top = df.groupby('Tenant Name')['API Calls'].sum().nlargest(n).reset_index()
    top = top.sort_values('API Calls')
    fig = go.Figure(go.Bar(
        x=top['API Calls'], y=top['Tenant Name'],
        orientation='h',
        marker=dict(
            color=top['API Calls'],
            colorscale=[[0, '#1e3a5f'], [1, '#00d4ff']],
            showscale=False,
        ),
        text=top['API Calls'].apply(lambda v: f'{v:,}'),
        textposition='outside',
        textfont=dict(size=11, color='#94a3b8'),
    ))
    fig.update_layout(**PLOTLY_LAYOUT, height=360,
                      title=dict(text=f'Top {n} Tenants by API Calls', font=dict(size=14, color='#e2e8f0')),
                      xaxis_title='Total API Calls')
    return fig


def chart_top_connectors(df, n=10):
    top = df.groupby('Connector Name')['API Calls'].sum().nlargest(n).reset_index()
    top = top.sort_values('API Calls')
    fig = go.Figure(go.Bar(
        x=top['API Calls'], y=top['Connector Name'],
        orientation='h',
        marker=dict(
            color=top['API Calls'],
            colorscale=[[0, '#2d1b69'], [1, '#8b5cf6']],
            showscale=False,
        ),
        text=top['API Calls'].apply(lambda v: f'{v:,}'),
        textposition='outside',
        textfont=dict(size=11, color='#94a3b8'),
    ))
    fig.update_layout(**PLOTLY_LAYOUT, height=360,
                      title=dict(text=f'Top {n} Connectors by API Calls', font=dict(size=14, color='#e2e8f0')),
                      xaxis_title='Total API Calls')
    return fig


def chart_connector_by_tenant(df):
    pivot = df.groupby(['Tenant Name', 'Connector Name'])['API Calls'].sum().reset_index()
    fig = px.bar(
        pivot, x='Tenant Name', y='API Calls', color='Connector Name',
        color_discrete_sequence=COLOR_SEQ,
        barmode='stack',
    )
    fig.update_layout(**PLOTLY_LAYOUT, height=360,
                      title=dict(text='Connector Mix per Tenant', font=dict(size=14, color='#e2e8f0')),
                      xaxis_tickangle=-30, bargap=0.2)
    return fig


def chart_distribution(df):
    by_conn = df.groupby('Connector Name')['API Calls'].sum().reset_index()
    by_conn = by_conn.nlargest(8, 'API Calls')
    fig = go.Figure(go.Pie(
        labels=by_conn['Connector Name'],
        values=by_conn['API Calls'],
        hole=0.62,
        marker=dict(colors=COLOR_SEQ, line=dict(color='#0f1117', width=2)),
        textfont=dict(size=11, color='#e2e8f0'),
        hovertemplate='<b>%{label}</b><br>Calls: %{value:,}<br>Share: %{percent}<extra></extra>',
    ))
    fig.add_annotation(
        text=f"<b>{by_conn['API Calls'].sum():,}</b><br><span style='font-size:11px;color:#64748b'>Total</span>",
        x=0.5, y=0.5, showarrow=False,
        font=dict(size=16, color='#e2e8f0'),
        align='center',
    )
    fig.update_layout(**PLOTLY_LAYOUT, height=340,
                      title=dict(text='API Usage Distribution', font=dict(size=14, color='#e2e8f0')),
                      showlegend=True)
    return fig


def chart_heatmap(df):
    # Aggregate to tenant × date
    pivot = df.groupby(['Tenant Name', 'Date'])['API Calls'].sum().reset_index()
    pivot_wide = pivot.pivot(index='Tenant Name', columns='Date', values='API Calls').fillna(0)

    # Sample at most 30 dates for readability
    if pivot_wide.shape[1] > 30:
        step = pivot_wide.shape[1] // 30
        pivot_wide = pivot_wide.iloc[:, ::step]

    fig = go.Figure(go.Heatmap(
        z=pivot_wide.values,
        x=[str(d)[:10] for d in pivot_wide.columns],
        y=pivot_wide.index.tolist(),
        colorscale=[
            [0.0, '#0f1117'],
            [0.2, '#1e3a5f'],
            [0.5, '#1d4ed8'],
            [0.8, '#00d4ff'],
            [1.0, '#f43f5e'],
        ],
        hovertemplate='Tenant: %{y}<br>Date: %{x}<br>Calls: %{z:,}<extra></extra>',
        showscale=True,
        colorbar=dict(
            title='API Calls',
            titlefont=dict(color='#94a3b8', size=11),
            tickfont=dict(color='#94a3b8', size=10),
            bgcolor='rgba(26,29,46,0.8)',
            bordercolor='#2d3161',
        ),
    ))
    fig.update_layout(**PLOTLY_LAYOUT, height=400,
                      title=dict(text='API Usage Heatmap (Tenant × Date)', font=dict(size=14, color='#e2e8f0')),
                      xaxis=dict(tickangle=-45, tickfont=dict(size=9), gridcolor='#1e2240'),
                      yaxis=dict(tickfont=dict(size=11), gridcolor='#1e2240'))
    return fig


def chart_growth_trend(df):
    weekly = df.groupby(df['Date'].dt.to_period('W').astype(str))['API Calls'].sum().reset_index()
    weekly.columns = ['Week', 'API Calls']
    weekly['Growth %'] = weekly['API Calls'].pct_change() * 100

    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(go.Bar(
        x=weekly['Week'], y=weekly['API Calls'],
        name='Weekly Calls', marker_color='rgba(0,212,255,0.4)',
        marker_line_width=0,
    ), secondary_y=False)
    fig.add_trace(go.Scatter(
        x=weekly['Week'], y=weekly['Growth %'],
        name='WoW Growth %', mode='lines+markers',
        line=dict(color='#f59e0b', width=2),
        marker=dict(size=5),
    ), secondary_y=True)
    fig.update_layout(**PLOTLY_LAYOUT, height=300,
                      title=dict(text='Weekly Growth Trend', font=dict(size=14, color='#e2e8f0')))
    fig.update_yaxes(title_text='API Calls', secondary_y=False,
                     gridcolor='#1e2240', tickfont=dict(size=11))
    fig.update_yaxes(title_text='WoW Growth %', secondary_y=True,
                     gridcolor='rgba(0,0,0,0)', tickfont=dict(size=11))
    fig.update_xaxes(tickangle=-45, tickfont=dict(size=9))
    return fig


def chart_connector_comparison(df):
    conn_daily = df.groupby(['Connector Name', 'Date'])['API Calls'].sum().reset_index()
    top_conns = df.groupby('Connector Name')['API Calls'].sum().nlargest(5).index.tolist()
    conn_daily = conn_daily[conn_daily['Connector Name'].isin(top_conns)]

    fig = go.Figure()
    for i, conn in enumerate(top_conns):
        sub = conn_daily[conn_daily['Connector Name'] == conn]
        smoothed = sub['API Calls'].rolling(7, min_periods=1).mean()
        fig.add_trace(go.Scatter(
            x=sub['Date'], y=smoothed,
            mode='lines', name=conn,
            line=dict(color=COLOR_SEQ[i % len(COLOR_SEQ)], width=2),
        ))
    fig.update_layout(**PLOTLY_LAYOUT, height=300,
                      title=dict(text='Connector Performance (7d Rolling Avg)', font=dict(size=14, color='#e2e8f0')))
    return fig


def chart_peak_detection(df):
    daily_hour = df.groupby(['DayOfWeek'])['API Calls'].mean().reset_index()
    order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    daily_hour['DayOfWeek'] = pd.Categorical(daily_hour['DayOfWeek'], categories=order, ordered=True)
    daily_hour = daily_hour.sort_values('DayOfWeek')

    fig = go.Figure(go.Bar(
        x=daily_hour['DayOfWeek'], y=daily_hour['API Calls'],
        marker=dict(
            color=daily_hour['API Calls'],
            colorscale=[[0, '#1e3a5f'], [0.5, '#8b5cf6'], [1, '#f43f5e']],
            showscale=False,
        ),
        text=daily_hour['API Calls'].round(0).astype(int).apply(lambda v: f'{v:,}'),
        textposition='outside',
        textfont=dict(size=11, color='#94a3b8'),
    ))
    fig.update_layout(**PLOTLY_LAYOUT, height=280,
                      title=dict(text='Average API Calls by Day of Week', font=dict(size=14, color='#e2e8f0')),
                      bargap=0.25)
    return fig


# ─────────────────────────────────────────────
# SIDEBAR & FILTERS
# ─────────────────────────────────────────────
def sidebar_filters(df: pd.DataFrame):
    with st.sidebar:
        st.markdown("""
        <div style="padding: 16px 0 8px 0;">
            <div class="sidebar-title">📡 API ANALYTICS</div>
            <div style="font-size:11px; color:#475569; margin-bottom:16px;">Usage Intelligence Dashboard</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("**📂 Data Source**")
        uploaded = st.file_uploader(
            "Upload Excel File",
            type=['xlsx', 'xls'],
            help="Sheet 1: API Usage Data | Sheet 2: Tenant Mapping",
        )

        st.markdown("---")
        st.markdown("**🔍 Filters**")

        all_tenants = sorted(df['Tenant Name'].dropna().unique().tolist())
        tenants_sel = st.multiselect(
            "Tenants",
            options=all_tenants,
            default=[],
            placeholder="All tenants",
        )

        all_connectors = sorted(df['Connector Name'].dropna().unique().tolist())
        connectors_sel = st.multiselect(
            "Connectors",
            options=all_connectors,
            default=[],
            placeholder="All connectors",
        )

        date_min = df['Date'].min().date()
        date_max = df['Date'].max().date()
        date_range = st.date_input(
            "Date Range",
            value=(date_min, date_max),
            min_value=date_min,
            max_value=date_max,
        )

        email_search = st.text_input("🔎 Customer Email Search", placeholder="@company.com")

        st.markdown("---")
        st.markdown("**⚙️ Settings**")
        spike_z = st.slider("Spike Detection Threshold (σ)", 1.5, 4.0, 2.5, 0.1)
        top_n = st.slider("Top N Items in Charts", 5, 20, 10)

    return uploaded, tenants_sel, connectors_sel, date_range, email_search, spike_z, top_n


def apply_filters(df, tenants_sel, connectors_sel, date_range, email_search):
    filtered = df.copy()
    if tenants_sel:
        filtered = filtered[filtered['Tenant Name'].isin(tenants_sel)]
    if connectors_sel:
        filtered = filtered[filtered['Connector Name'].isin(connectors_sel)]
    if len(date_range) == 2:
        filtered = filtered[
            (filtered['Date'].dt.date >= date_range[0]) &
            (filtered['Date'].dt.date <= date_range[1])
        ]
    if email_search and 'Customer Email' in filtered.columns:
        filtered = filtered[
            filtered['Customer Email'].str.contains(email_search, case=False, na=False)
        ]
    return filtered


# ─────────────────────────────────────────────
# KPI CARDS RENDERER
# ─────────────────────────────────────────────
def render_kpi_cards(metrics):
    cards = [
        ('Total API Calls', f"{metrics['total_calls']:,}", 'All time total', '📊', '#00d4ff'),
        ('Daily Average', f"{metrics['daily_avg']:,}", 'Avg calls/day', '📈', '#8b5cf6'),
        ('Active Tenants', str(metrics['active_tenants']), 'With API activity', '🏢', '#10b981'),
        ('Connectors', str(metrics['total_connectors']), 'Unique connectors', '🔌', '#f59e0b'),
        ('This Month', f"{metrics['this_month']:,}", 'Current month total', '📅', '#f43f5e'),
    ]
    html = '<div class="kpi-grid">'
    for label, value, sub, icon, color in cards:
        html += f"""
        <div class="kpi-card" style="--accent-color:{color}">
            <div class="kpi-icon">{icon}</div>
            <div class="kpi-label">{label}</div>
            <div class="kpi-value">{value}</div>
            <div class="kpi-sub">{sub}</div>
        </div>"""
    html += '</div>'
    st.markdown(html, unsafe_allow_html=True)


# ─────────────────────────────────────────────
# ACTIVE TENANTS TABLE
# ─────────────────────────────────────────────
def render_active_tenants_table(df):
    table = df.groupby('Tenant Name').agg(
        Total_Calls=('API Calls', 'sum'),
        Connectors=('Connector Name', 'nunique'),
        Active_Days=('Date', 'nunique'),
        Last_Seen=('Date', 'max'),
    ).reset_index()
    table['Avg Daily Calls'] = (table['Total_Calls'] / table['Active_Days']).round(0).astype(int)
    table = table.sort_values('Total_Calls', ascending=False).reset_index(drop=True)
    table.columns = ['Tenant', 'Total Calls', 'Connectors', 'Active Days', 'Last Seen', 'Avg/Day']
    table['Total Calls'] = table['Total Calls'].apply(lambda v: f'{v:,}')
    table['Avg/Day'] = table['Avg/Day'].apply(lambda v: f'{v:,}')
    table['Last Seen'] = table['Last Seen'].dt.strftime('%Y-%m-%d')
    st.dataframe(table, use_container_width=True, hide_index=True)


# ─────────────────────────────────────────────
# SPIKE ALERT PANEL
# ─────────────────────────────────────────────
def render_spike_panel(df, z_threshold):
    spikes = detect_spikes(df, z_threshold)
    if spikes.empty:
        st.info("✅ No significant spikes detected with current threshold.")
        return

    st.markdown(f"**{len(spikes)} spike(s) detected** above {z_threshold}σ threshold")
    for _, row in spikes.iterrows():
        st.markdown(
            f'<span class="spike-badge">⚡ {row["Tenant Name"]} · {row["Connector Name"]} · '
            f'{str(row["Date"])[:10]} · {int(row["API Calls"]):,} calls (+{row["spike_pct"]:.0f}%)</span>',
            unsafe_allow_html=True,
        )


# ─────────────────────────────────────────────
# SEGMENTATION PANEL
# ─────────────────────────────────────────────
def render_segmentation(df):
    segs = segment_tenants(df)
    badge_map = {'Low': 'low-badge', 'Medium': 'med-badge', 'High': 'high-badge'}
    for _, row in segs.iterrows():
        badge_class = badge_map.get(row['Segment'], '')
        st.markdown(
            f'<div class="segment-row">'
            f'<span class="segment-name">{row["Tenant Name"]}</span>'
            f'<span class="segment-calls">{int(row["API Calls"]):,} calls&nbsp;&nbsp;</span>'
            f'<span class="spike-badge {badge_class}">{row["Segment"]}</span>'
            f'</div>',
            unsafe_allow_html=True,
        )


# ─────────────────────────────────────────────
# MAIN APP
# ─────────────────────────────────────────────
def main():

    # ── Load data ──────────────────────────────
    # Sidebar (must be called before we can show data)
    # We create a placeholder sidebar call to get the upload widget up first
    with st.sidebar:
        st.markdown("""
        <div style="padding: 16px 0 8px 0;">
            <div class="sidebar-title">📡 API ANALYTICS</div>
            <div style="font-size:11px; color:#475569; margin-bottom:16px;">Usage Intelligence Dashboard</div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("**📂 Data Source**")
        uploaded = st.file_uploader(
            "Upload Excel File",
            type=['xlsx', 'xls'],
            help="Sheet 1: API Usage Data | Sheet 2: Tenant Mapping",
        )

    if uploaded:
        df_usage_raw, df_mapping_raw = load_excel(uploaded)
    else:
        df_usage_raw, df_mapping_raw = generate_demo_data()
        st.sidebar.info("🎲 Using demo data. Upload an Excel file to use your own data.")

    df_full = transform_data(df_usage_raw, df_mapping_raw)

    # ── Sidebar filters ─────────────────────────
    with st.sidebar:
        st.markdown("---")
        st.markdown("**🔍 Filters**")

        all_tenants = sorted(df_full['Tenant Name'].dropna().unique().tolist())
        tenants_sel = st.multiselect("Tenants", all_tenants, default=[], placeholder="All tenants")

        all_connectors = sorted(df_full['Connector Name'].dropna().unique().tolist())
        connectors_sel = st.multiselect("Connectors", all_connectors, default=[], placeholder="All connectors")

        date_min = df_full['Date'].min().date()
        date_max = df_full['Date'].max().date()
        date_range = st.date_input("Date Range", value=(date_min, date_max),
                                   min_value=date_min, max_value=date_max)

        email_search = st.text_input("🔎 Customer Email Search", placeholder="@company.com")

        st.markdown("---")
        st.markdown("**⚙️ Settings**")
        spike_z = st.slider("Spike Detection Threshold (σ)", 1.5, 4.0, 2.5, 0.1)
        top_n = st.slider("Top N in Charts", 5, 20, 10)

    df = apply_filters(df_full, tenants_sel, connectors_sel, date_range, email_search)

    if df.empty:
        st.warning("⚠️ No data matches your current filters. Please adjust the filter criteria.")
        return

    metrics = kpi_metrics(df)

    # ── Header ──────────────────────────────────
    col_title, col_meta = st.columns([3, 1])
    with col_title:
        st.markdown("""
        <div style="margin-bottom:4px;">
            <span style="font-family:'IBM Plex Mono',monospace; font-size:24px; font-weight:700;
                         color:#e2e8f0; letter-spacing:-0.02em;">API Usage Analytics</span>
            <span style="font-size:12px; color:#475569; margin-left:12px;">Production Dashboard</span>
        </div>
        """, unsafe_allow_html=True)
    with col_meta:
        st.markdown(
            f'<div style="text-align:right; font-family:IBM Plex Mono,monospace; '
            f'font-size:11px; color:#475569; padding-top:8px;">'
            f'Data: {df["Date"].min().strftime("%b %d")} → {df["Date"].max().strftime("%b %d, %Y")}<br>'
            f'{len(df):,} data points loaded</div>',
            unsafe_allow_html=True,
        )

    # ── KPI Cards ───────────────────────────────
    render_kpi_cards(metrics)

    # ── Trend Charts ────────────────────────────
    st.markdown('<div class="section-header">📈 USAGE TRENDS</div>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        st.plotly_chart(chart_daily_trend(df), use_container_width=True, config={'displayModeBar': False})
    with c2:
        st.plotly_chart(chart_monthly(df), use_container_width=True, config={'displayModeBar': False})

    # ── Rankings ────────────────────────────────
    st.markdown('<div class="section-header">🏆 RANKINGS</div>', unsafe_allow_html=True)
    c3, c4 = st.columns(2)
    with c3:
        st.plotly_chart(chart_top_tenants(df, top_n), use_container_width=True, config={'displayModeBar': False})
    with c4:
        st.plotly_chart(chart_top_connectors(df, top_n), use_container_width=True, config={'displayModeBar': False})

    # ── Connector Breakdown ─────────────────────
    st.markdown('<div class="section-header">🔌 CONNECTOR ANALYSIS</div>', unsafe_allow_html=True)
    c5, c6 = st.columns([2, 1])
    with c5:
        st.plotly_chart(chart_connector_by_tenant(df), use_container_width=True, config={'displayModeBar': False})
    with c6:
        st.plotly_chart(chart_distribution(df), use_container_width=True, config={'displayModeBar': False})

    # ── Heatmap ─────────────────────────────────
    st.markdown('<div class="section-header">🗺 USAGE HEATMAP</div>', unsafe_allow_html=True)
    st.plotly_chart(chart_heatmap(df), use_container_width=True, config={'displayModeBar': False})

    # ── Advanced Analytics ──────────────────────
    st.markdown('<div class="section-header">🔬 ADVANCED ANALYTICS</div>', unsafe_allow_html=True)
    c7, c8 = st.columns(2)
    with c7:
        st.plotly_chart(chart_growth_trend(df), use_container_width=True, config={'displayModeBar': False})
    with c8:
        st.plotly_chart(chart_connector_comparison(df), use_container_width=True, config={'displayModeBar': False})

    # Peak detection
    st.plotly_chart(chart_peak_detection(df), use_container_width=True, config={'displayModeBar': False})

    # ── Spike Alerts & Segmentation ─────────────
    st.markdown('<div class="section-header">⚡ ANOMALY DETECTION & SEGMENTATION</div>', unsafe_allow_html=True)
    c9, c10 = st.columns([3, 2])
    with c9:
        st.markdown("**🚨 API Call Spikes**")
        render_spike_panel(df, spike_z)
    with c10:
        st.markdown("**📦 Tenant Segmentation**")
        render_segmentation(df)

    # ── Active Tenants Table ─────────────────────
    st.markdown('<div class="section-header">📋 ACTIVE TENANTS</div>', unsafe_allow_html=True)
    render_active_tenants_table(df)

    # ── Footer ───────────────────────────────────
    st.markdown("""
    <div style="text-align:center; color:#2d3161; font-size:11px;
                border-top:1px solid #1e2240; padding:24px 0 8px 0; margin-top:32px;
                font-family:'IBM Plex Mono',monospace;">
        API Usage Analytics Dashboard · Built with Streamlit + Plotly
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
