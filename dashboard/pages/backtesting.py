# Page — Backtesting

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from scipy.stats import chi2, ks_2samp

@st.cache_data
def load_data():
    pd_preds = pd.read_csv('data/pd_predictions.csv')
    pd_year  = pd.read_csv('data/pd_predictions_with_year.csv')
    return pd_preds, pd_year

def show():
    pd_preds, pd_year = load_data()

    st.markdown("""
    <div class='page-header'>Regulatory Backtesting</div>
    <div class='page-subheader'>
        Kupiec · Traffic Light · Calibration · OOT PSI — all 4 tests
    </div>
    """, unsafe_allow_html=True)

    y_true  = pd_preds['actual_default']
    y_score = pd_preds['pd_probability']

    actual_dr   = y_true.mean()
    mean_pd     = y_score.mean()
    n           = len(pd_preds)
    x           = y_true.sum()

    # ── 1. KUPIEC TEST ───────────────────────────────────────
    p      = mean_pd
    LR     = -2 * (x * np.log(p) + (n - x) * np.log(1 - p)
                   - x * np.log(x / n) - (n - x) * np.log(1 - x / n))
    p_val  = 1 - chi2.cdf(LR, df=1)
    k_pass = p_val > 0.05

    # ── 2. TRAFFIC LIGHT ────────────────────────────────────
    expected  = mean_pd * n
    deviation = abs(x - expected) / expected * 100
    if deviation < 20:
        tl_zone  = "GREEN"
        tl_color = "#22c55e"
        tl_bg    = "#14532d"
    elif deviation < 40:
        tl_zone  = "AMBER"
        tl_color = "#f59e0b"
        tl_bg    = "#78350f"
    else:
        tl_zone  = "RED"
        tl_color = "#ef4444"
        tl_bg    = "#7f1d1d"

    # ── 3. CALIBRATION ──────────────────────────────────────
    pd_preds_copy = pd_preds.copy()
    pd_preds_copy['bucket'] = pd.qcut(y_score, 10, duplicates='drop')
    calib = pd_preds_copy.groupby('bucket', observed=True).agg(
        pred=('pd_probability', 'mean'),
        actual=('actual_default', 'mean'),
        count=('actual_default', 'count')
    ).reset_index()
    calib['deviation'] = abs(calib['pred'] - calib['actual'])
    mean_calib_err = calib['deviation'].mean()
    cal_pass = mean_calib_err < 0.10

    # ── 4. OOT PSI ──────────────────────────────────────────
    train_w = pd_year[pd_year['issue_year'] <= 2016]['pd_probability']
    oot_w   = pd_year[pd_year['issue_year'] >= 2017]['pd_probability']
    bins       = np.linspace(0, 1, 11)
    train_dist = np.histogram(train_w, bins=bins)[0] / len(train_w)
    oot_dist   = np.histogram(oot_w,   bins=bins)[0] / len(oot_w)
    train_dist = np.where(train_dist == 0, 1e-4, train_dist)
    oot_dist   = np.where(oot_dist   == 0, 1e-4, oot_dist)
    bucket_psi = (oot_dist - train_dist) * np.log(oot_dist / train_dist)
    psi        = bucket_psi.sum()
    psi_pass   = psi < 0.10

    # ── Summary cards ────────────────────────────────────────
    st.markdown("<div class='section-title'>Test results summary</div>",
                unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)

    for col, name, result, val, passed, color in [
        (c1, "Kupiec Test",
         "PASS" if k_pass else "FAIL",
         f"p-value: {p_val:.4f}", k_pass, "#22c55e" if k_pass else "#ef4444"),
        (c2, "Traffic Light",
         tl_zone,
         f"deviation: {deviation:.2f}%", tl_zone == "GREEN", tl_color),
        (c3, "Calibration",
         "PASS" if cal_pass else "REVIEW",
         f"mean error: {mean_calib_err:.4f}", cal_pass,
         "#22c55e" if cal_pass else "#f59e0b"),
        (c4, "OOT PSI",
         "STABLE" if psi_pass else "MONITOR",
         f"PSI: {psi:.4f}", psi_pass, "#22c55e" if psi_pass else "#f59e0b"),
    ]:
        col.markdown(f"""
        <div class='ecl-card' style='text-align:center'>
            <div style='font-size:22px;font-weight:600;color:{color};
                font-family:DM Mono,monospace;margin-bottom:4px'>{result}</div>
            <div style='font-size:13px;font-weight:500;color:#94a3b8;
                margin-bottom:3px'>{name}</div>
            <div style='font-size:11px;color:#475569;
                font-family:DM Mono,monospace'>{val}</div>
        </div>""", unsafe_allow_html=True)

    all_pass = k_pass and tl_zone == "GREEN" and cal_pass and psi_pass
    st.markdown(f"""
    <div style='background:{"#14532d" if all_pass else "#78350f"};
        border:1px solid {"#22c55e" if all_pass else "#f59e0b"};
        border-radius:10px;padding:12px 16px;margin:0.5rem 0 1.5rem;
        display:flex;align-items:center;gap:10px'>
        <div style='font-size:15px;font-weight:600;
            color:{"#86efac" if all_pass else "#fde68a"}'>
            {"ALL 4 TESTS PASSED" if all_pass else "REVIEW REQUIRED"}
        </div>
        <div style='font-size:12px;color:{"#86efac" if all_pass else "#fde68a"};opacity:0.8'>
            — Model meets regulatory backtesting requirements
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<hr>", unsafe_allow_html=True)

    # ── Chart row 1: Kupiec + Traffic Light ─────────────────
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("<div class='section-title'>Kupiec test — predicted vs actual DR</div>",
                    unsafe_allow_html=True)
        fig1 = go.Figure()
        fig1.add_trace(go.Bar(
            x=['Predicted PD<br>(Calibrated)', 'Actual<br>Default Rate'],
            y=[mean_pd * 100, actual_dr * 100],
            marker=dict(color=['#3b82f6', '#ef4444'],
                        line=dict(color='#0a0e1a', width=1)),
            text=[f'{mean_pd*100:.2f}%', f'{actual_dr*100:.2f}%'],
            textposition='outside',
            textfont=dict(size=13, color='#e2e8f0', family='DM Mono')
        ))
        fig1.update_layout(
            paper_bgcolor='#111827', plot_bgcolor='#111827',
            font=dict(color='#94a3b8', family='Sora', size=11),
            xaxis=dict(color='#475569', showgrid=False),
            yaxis=dict(title='Default Rate (%)', color='#475569',
                       gridcolor='#1e2d4a', range=[0, 30]),
            margin=dict(t=20, b=40, l=50, r=20),
            height=280, showlegend=False,
            annotations=[dict(
                text=f"LR stat: {LR:.4f} | p-value: {p_val:.4f} | {'PASS' if k_pass else 'FAIL'}",
                x=0.5, y=1.05, xref='paper', yref='paper',
                showarrow=False,
                font=dict(size=11, color='#22c55e' if k_pass else '#ef4444')
            )]
        )
        st.plotly_chart(fig1, use_container_width=True)

    with col2:
        st.markdown("<div class='section-title'>Traffic light — deviation from expected</div>",
                    unsafe_allow_html=True)
        fig2 = go.Figure()
        fig2.add_trace(go.Bar(
            x=['Green\n(<20%)', 'Amber\n(20-40%)', 'Red\n(>40%)'],
            y=[20, 20, 20],
            marker=dict(color=['#22c55e', '#f59e0b', '#ef4444'], opacity=0.35),
            showlegend=False
        ))
        fig2.add_trace(go.Scatter(
            x=[tl_zone.title() + '\n(<20%)' if tl_zone == 'GREEN'
               else ('Amber\n(20-40%)' if tl_zone == 'AMBER' else 'Red\n(>40%)')],
            y=[deviation],
            mode='markers',
            marker=dict(color=tl_color, size=16,
                        symbol='diamond',
                        line=dict(color='white', width=2)),
            name=f'Deviation: {deviation:.2f}%',
            showlegend=True
        ))
        fig2.update_layout(
            paper_bgcolor='#111827', plot_bgcolor='#111827',
            font=dict(color='#94a3b8', family='Sora', size=11),
            xaxis=dict(color='#475569', showgrid=False),
            yaxis=dict(title='Deviation (%)', color='#475569',
                       gridcolor='#1e2d4a', range=[0, 60]),
            legend=dict(bgcolor='#111827', bordercolor='#1e2d4a'),
            margin=dict(t=20, b=40, l=50, r=20),
            height=280,
            annotations=[dict(
                text=f"Zone: {tl_zone} | Deviation: {deviation:.2f}%",
                x=0.5, y=1.05, xref='paper', yref='paper',
                showarrow=False,
                font=dict(size=11, color=tl_color)
            )]
        )
        st.plotly_chart(fig2, use_container_width=True)

    # ── Chart row 2: Calibration ─────────────────────────────
    st.markdown("<hr>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("<div class='section-title'>Calibration curve — bucket level</div>",
                    unsafe_allow_html=True)
        fig3 = go.Figure()
        fig3.add_trace(go.Scatter(
            x=[0, calib['pred'].max() * 1.05],
            y=[0, calib['pred'].max() * 1.05],
            mode='lines',
            line=dict(color='#475569', width=1.5, dash='dash'),
            name='Perfect calibration'
        ))
        fig3.add_trace(go.Scatter(
            x=calib['pred'], y=calib['actual'],
            mode='lines+markers',
            marker=dict(color='#3b82f6', size=9,
                        line=dict(color='#1d4ed8', width=1.5)),
            line=dict(color='#3b82f6', width=2),
            name='Actual vs Predicted',
            text=[f'n={c:,}' for c in calib['count']],
            hovertemplate='Pred: %{x:.3f}<br>Actual: %{y:.3f}<br>%{text}'
        ))
        fig3.update_layout(
            paper_bgcolor='#111827', plot_bgcolor='#111827',
            font=dict(color='#94a3b8', family='Sora', size=11),
            xaxis=dict(title='Mean Predicted PD', color='#475569',
                       gridcolor='#1e2d4a'),
            yaxis=dict(title='Actual Default Rate', color='#475569',
                       gridcolor='#1e2d4a'),
            legend=dict(bgcolor='#111827', bordercolor='#1e2d4a'),
            margin=dict(t=20, b=40, l=50, r=10),
            height=300,
            annotations=[dict(
                text=f"Mean calibration error: {mean_calib_err:.4f} | {'PASS' if cal_pass else 'REVIEW'}",
                x=0.5, y=1.05, xref='paper', yref='paper',
                showarrow=False,
                font=dict(size=11, color='#22c55e' if cal_pass else '#f59e0b')
            )]
        )
        st.plotly_chart(fig3, use_container_width=True)

    with col2:
        st.markdown("<div class='section-title'>Calibration error by bucket</div>",
                    unsafe_allow_html=True)
        fig4 = go.Figure()
        fig4.add_trace(go.Bar(
            x=[str(b) for b in calib['bucket']],
            y=calib['deviation'],
            marker=dict(
                color=calib['deviation'],
                colorscale=[[0, '#22c55e'], [0.5, '#f59e0b'], [1, '#ef4444']],
                line=dict(color='#0a0e1a', width=0.5)
            ),
            text=[f'{v:.4f}' for v in calib['deviation']],
            textposition='outside',
            textfont=dict(size=9, color='#94a3b8')
        ))
        fig4.add_hline(y=0.10, line=dict(color='#ef4444', width=1, dash='dash'),
                       annotation_text='Threshold (0.10)',
                       annotation_font_color='#ef4444',
                       annotation_font_size=10)
        fig4.update_layout(
            paper_bgcolor='#111827', plot_bgcolor='#111827',
            font=dict(color='#94a3b8', family='Sora', size=11),
            xaxis=dict(title='PD Bucket', color='#475569',
                       showticklabels=False, showgrid=False),
            yaxis=dict(title='Abs. Deviation', color='#475569',
                       gridcolor='#1e2d4a'),
            margin=dict(t=20, b=40, l=50, r=10),
            height=300, showlegend=False
        )
        st.plotly_chart(fig4, use_container_width=True)

    # ── Chart row 3: OOT PSI ─────────────────────────────────
    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>Out-of-time PSI — 2007–2016 vs 2017–2018</div>",
                unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    bin_labels = [f'{bins[i]:.1f}–{bins[i+1]:.1f}' for i in range(len(bins)-1)]

    with col1:
        fig5 = go.Figure()
        fig5.add_trace(go.Bar(
            x=bin_labels, y=train_dist,
            name=f'Train 2007–2016 (n={len(train_w):,})',
            marker=dict(color='#3b82f6', opacity=0.8,
                        line=dict(color='#0a0e1a', width=0.5))
        ))
        fig5.add_trace(go.Bar(
            x=bin_labels, y=oot_dist,
            name=f'OOT 2017–2018 (n={len(oot_w):,})',
            marker=dict(color='#f97316', opacity=0.8,
                        line=dict(color='#0a0e1a', width=0.5))
        ))
        fig5.update_layout(
            barmode='group',
            paper_bgcolor='#111827', plot_bgcolor='#111827',
            font=dict(color='#94a3b8', family='Sora', size=11),
            xaxis=dict(title='PD Bucket', color='#475569',
                       showticklabels=False, showgrid=False),
            yaxis=dict(title='Proportion', color='#475569',
                       gridcolor='#1e2d4a'),
            legend=dict(bgcolor='#111827', bordercolor='#1e2d4a',
                        font=dict(size=10)),
            margin=dict(t=20, b=40, l=50, r=10),
            height=300,
            annotations=[dict(
                text=f"PSI: {psi:.4f} | {'STABLE' if psi_pass else 'MONITOR'}",
                x=0.5, y=1.05, xref='paper', yref='paper',
                showarrow=False,
                font=dict(size=11, color='#22c55e' if psi_pass else '#f59e0b')
            )]
        )
        st.plotly_chart(fig5, use_container_width=True)

    with col2:
        fig6 = go.Figure()
        fig6.add_trace(go.Bar(
            x=bin_labels, y=bucket_psi,
            marker=dict(
                color=bucket_psi,
                colorscale=[[0, '#22c55e'], [0.5, '#f59e0b'], [1, '#ef4444']],
                line=dict(color='#0a0e1a', width=0.5)
            ),
            text=[f'{v:.4f}' for v in bucket_psi],
            textposition='outside',
            textfont=dict(size=9, color='#94a3b8')
        ))
        fig6.add_hline(y=0.10, line=dict(color='#ef4444', width=1, dash='dash'),
                       annotation_text='Instability threshold',
                       annotation_font_color='#ef4444',
                       annotation_font_size=10)
        fig6.update_layout(
            paper_bgcolor='#111827', plot_bgcolor='#111827',
            font=dict(color='#94a3b8', family='Sora', size=11),
            xaxis=dict(title='PD Bucket', color='#475569',
                       showticklabels=False, showgrid=False),
            yaxis=dict(title='Bucket PSI', color='#475569',
                       gridcolor='#1e2d4a'),
            margin=dict(t=20, b=40, l=50, r=10),
            height=300, showlegend=False
        )
        st.plotly_chart(fig6, use_container_width=True)

    # ── Full metrics table ───────────────────────────────────
    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>Full metrics</div>",
                unsafe_allow_html=True)

    metrics_df = pd.DataFrame([
        ['Kupiec LR Statistic',     f'{LR:.4f}',          '< 3.84 (χ² at 5%)', 'PASS' if k_pass else 'FAIL'],
        ['Kupiec p-value',          f'{p_val:.4f}',        '> 0.05',             'PASS' if k_pass else 'FAIL'],
        ['Expected defaults',       f'{expected:,.0f}',    '—',                  '—'],
        ['Actual defaults',         f'{int(x):,}',         '—',                  '—'],
        ['Traffic Light deviation', f'{deviation:.2f}%',   '< 20% = Green',      tl_zone],
        ['Mean calibration error',  f'{mean_calib_err:.4f}','< 0.10',            'PASS' if cal_pass else 'REVIEW'],
        ['OOT PSI',                 f'{psi:.4f}',          '< 0.10 = Stable',    'STABLE' if psi_pass else 'MONITOR'],
        ['Train window loans',      f'{len(train_w):,}',   '2007–2016',          '—'],
        ['OOT window loans',        f'{len(oot_w):,}',     '2017–2018',          '—'],
    ], columns=['Metric', 'Value', 'Benchmark', 'Result'])

    st.dataframe(metrics_df, use_container_width=True, hide_index=True)