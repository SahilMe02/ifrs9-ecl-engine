# IFRS 9 ECL Engine — Main App Entry Point

import streamlit as st

st.set_page_config(
    page_title="IFRS 9 ECL Engine",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Global CSS — Dark Fintech Theme ─────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Sora:wght@300;400;500;600&family=DM+Mono:wght@300;400;500&display=swap');

html, body, [class*="css"] {
    font-family: 'Sora', sans-serif;
    background-color: #0a0e1a;
    color: #e2e8f0;
}

#MainMenu, footer, header {visibility: hidden;}
.block-container {
    padding-top: 1.5rem;
    padding-bottom: 2rem;
    padding-left: 2rem;
    padding-right: 2rem;
    max-width: 1400px;
}

[data-testid="stSidebar"] {
    background-color: #0d1220;
    border-right: 1px solid #1e2d4a;
}
[data-testid="stSidebar"] * {
    font-family: 'Sora', sans-serif !important;
}

[data-testid="metric-container"] {
    background: #111827;
    border: 1px solid #1e2d4a;
    border-radius: 12px;
    padding: 1rem 1.25rem;
}
[data-testid="metric-container"] label {
    color: #64748b !important;
    font-size: 12px !important;
    letter-spacing: 0.05em;
    text-transform: uppercase;
}
[data-testid="metric-container"] [data-testid="stMetricValue"] {
    font-family: 'DM Mono', monospace !important;
    font-size: 24px !important;
    color: #e2e8f0 !important;
}

[data-testid="stTabs"] button {
    font-family: 'Sora', sans-serif;
    font-size: 13px;
    color: #64748b;
    border-bottom: 2px solid transparent;
}
[data-testid="stTabs"] button[aria-selected="true"] {
    color: #3b82f6;
    border-bottom: 2px solid #3b82f6;
}

[data-testid="stSelectbox"] > div,
[data-testid="stNumberInput"] input,
[data-testid="stSlider"] {
    background: #111827 !important;
    border: 1px solid #1e2d4a !important;
    border-radius: 8px !important;
    color: #e2e8f0 !important;
    font-family: 'Sora', sans-serif !important;
}

[data-testid="stButton"] button {
    background: linear-gradient(135deg, #1d4ed8, #3b82f6);
    color: white;
    border: none;
    border-radius: 8px;
    font-family: 'Sora', sans-serif;
    font-size: 14px;
    font-weight: 500;
    padding: 0.6rem 1.5rem;
    transition: all 0.2s ease;
    width: 100%;
}
[data-testid="stButton"] button:hover {
    background: linear-gradient(135deg, #1e40af, #2563eb);
    transform: translateY(-1px);
    box-shadow: 0 4px 20px rgba(59, 130, 246, 0.3);
}

[data-testid="stDataFrame"] {
    border: 1px solid #1e2d4a;
    border-radius: 10px;
    overflow: hidden;
}

hr {
    border-color: #1e2d4a;
    margin: 1.5rem 0;
}

.ecl-card {
    background: #111827;
    border: 1px solid #1e2d4a;
    border-radius: 14px;
    padding: 1.5rem;
    margin-bottom: 1rem;
}
.ecl-card-accent {
    background: #0f1f3d;
    border: 1px solid #1d4ed8;
    border-radius: 14px;
    padding: 1.5rem;
    margin-bottom: 1rem;
}
.ecl-label {
    font-size: 11px;
    color: #64748b;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    margin-bottom: 4px;
}
.ecl-value        { font-family: 'DM Mono', monospace; font-size: 28px; font-weight: 500; color: #e2e8f0; }
.ecl-value-blue   { font-family: 'DM Mono', monospace; font-size: 28px; font-weight: 500; color: #3b82f6; }
.ecl-value-red    { font-family: 'DM Mono', monospace; font-size: 28px; font-weight: 500; color: #ef4444; }
.ecl-value-green  { font-family: 'DM Mono', monospace; font-size: 28px; font-weight: 500; color: #22c55e; }
.ecl-value-amber  { font-family: 'DM Mono', monospace; font-size: 28px; font-weight: 500; color: #f59e0b; }

.stage-badge-1 {
    display: inline-block; background: #14532d; color: #86efac;
    font-size: 12px; font-weight: 500; padding: 4px 12px;
    border-radius: 20px; letter-spacing: 0.04em;
}
.stage-badge-2 {
    display: inline-block; background: #78350f; color: #fde68a;
    font-size: 12px; font-weight: 500; padding: 4px 12px;
    border-radius: 20px; letter-spacing: 0.04em;
}
.stage-badge-3 {
    display: inline-block; background: #7f1d1d; color: #fca5a5;
    font-size: 12px; font-weight: 500; padding: 4px 12px;
    border-radius: 20px; letter-spacing: 0.04em;
}
.page-header {
    font-family: 'Sora', sans-serif;
    font-size: 22px; font-weight: 600;
    color: #f1f5f9; margin-bottom: 4px;
}
.page-subheader { font-size: 13px; color: #64748b; margin-bottom: 1.5rem; }
.section-title {
    font-size: 13px; font-weight: 500; color: #94a3b8;
    letter-spacing: 0.06em; text-transform: uppercase;
    margin-bottom: 12px; margin-top: 8px;
}
.glow-blue { box-shadow: 0 0 20px rgba(59, 130, 246, 0.15); }
</style>
""", unsafe_allow_html=True)

# ── Sidebar ─────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='padding: 1rem 0 1.5rem 0;'>
        <div style='font-family: DM Mono, monospace; font-size: 11px;
                    color: #3b82f6; letter-spacing: 0.12em;
                    text-transform: uppercase; margin-bottom: 6px;'>
            IFRS 9 Engine
        </div>
        <div style='font-size: 18px; font-weight: 600; color: #f1f5f9;
                    line-height: 1.3;'>
            ECL Risk<br>Platform
        </div>
        <div style='font-size: 11px; color: #475569; margin-top: 6px;'>
            Morgan Stanley CV Project
        </div>
    </div>
    <hr style='border-color: #1e2d4a; margin: 0 0 1rem 0;'>
    """, unsafe_allow_html=True)

    page = st.radio(
        "Navigation",
        options=[
            "📊  Overview",
            "🎯  Loan Sandbox",
            "📈  Portfolio Analysis",
            "🧠  Model Performance",
            "✅  Backtesting",
            "📋  Export Report"
        ],
        label_visibility="collapsed"
    )

    st.markdown("""
    <hr style='border-color: #1e2d4a; margin: 1rem 0;'>
    <div style='font-size: 11px; color: #334155; line-height: 1.9;'>
        <div>Dataset: LendingClub 2007–2018</div>
        <div>Loans: 122,216</div>
        <div>PD model: Gradient Boosting</div>
        <div>AUC: 0.7115 · Gini: 0.4230</div>
        <div>LGD model: Gradient Boosting</div>
        <div>R²: 0.1914 · RMSE: 0.2007</div>
        <div>EAD: Hybrid amortisation</div>
        <div>Calibration: Platt Scaling</div>
        <div>Backtesting: 4/4 PASS</div>
    </div>
    """, unsafe_allow_html=True)

# ── Page Router ─────────────────────────────────────────────
if "Overview" in page:
    from pages.overview import show
    show()

elif "Sandbox" in page:
    from pages.loan_sandbox import show
    show()

elif "Portfolio" in page:
    from pages.portfolio import show
    show()

elif "Model Performance" in page:
    from pages.model_performance import show
    show()

elif "Backtesting" in page:
    from pages.backtesting import show
    show()

elif "Export" in page:
    from pages.export_report import show
    show()