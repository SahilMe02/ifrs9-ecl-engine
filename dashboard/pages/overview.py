# Page 1 - Executive Overview
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

@st.cache_data
def load_data():
    ecl_df = pd.read_csv('data/ecl_final_results.csv')
    return ecl_df

def show():
    df = load_data()

    st.markdown("""
    <div class='page-header'>Portfolio Overview</div>
    <div class='page-subheader'>
        IFRS 9 Expected Credit Loss — Executive Summary · 122,216 loans · LendingClub 2007–2018
    </div>
    """, unsafe_allow_html=True)

    total_loans  = len(df)
    total_ead    = df['ead'].sum()
    total_ecl    = df['ecl_base'].sum()
    ecl_coverage = (total_ecl / total_ead) * 100 if total_ead > 0 else 0
    mean_pd      = df['pd_probability'].mean()
    mean_lgd     = df['lgd_predicted'].mean()

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Loans", f"{total_loans:,}")
    with col2:
        st.metric("Portfolio EAD", f"${total_ead/1e6:.1f}M")
    with col3:
        st.metric("Base ECL Provision", f"${total_ecl/1e6:.1f}M",
                  delta=f"{ecl_coverage:.2f}% of EAD")
    with col4:
        st.metric("Mean PD / LGD",
                  f"{mean_pd*100:.1f}% / {mean_lgd*100:.1f}%")

    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>Macro scenario overlay (IFRS 9 forward-looking)</div>",
                unsafe_allow_html=True)

    ecl_opt  = df['ecl_optimistic'].sum() if 'ecl_optimistic' in df.columns else total_ecl * 0.80
    ecl_base = df['ecl_base'].sum()
    ecl_adv  = df['ecl_adverse'].sum() if 'ecl_adverse' in df.columns else total_ecl * 1.30

    sc1, sc2, sc3, sc4 = st.columns(4)
    with sc1:
        st.markdown(f"""
        <div class='ecl-card'>
            <div class='ecl-label'>Optimistic (PD × 0.80)</div>
            <div class='ecl-value-green'>${ecl_opt/1e6:.1f}M</div>
            <div style='font-size:11px;color:#475569;margin-top:4px'>{ecl_opt/total_ead*100:.2f}% of EAD</div>
        </div>""", unsafe_allow_html=True)
    with sc2:
        st.markdown(f"""
        <div class='ecl-card'>
            <div class='ecl-label'>Base case (no adjustment)</div>
            <div class='ecl-value-blue'>${ecl_base/1e6:.1f}M</div>
            <div style='font-size:11px;color:#475569;margin-top:4px'>{ecl_base/total_ead*100:.2f}% of EAD</div>
        </div>""", unsafe_allow_html=True)
    with sc3:
        st.markdown(f"""
        <div class='ecl-card'>
            <div class='ecl-label'>Adverse (PD × 1.30)</div>
            <div class='ecl-value-red'>${ecl_adv/1e6:.1f}M</div>
            <div style='font-size:11px;color:#475569;margin-top:4px'>{ecl_adv/total_ead*100:.2f}% of EAD</div>
        </div>""", unsafe_allow_html=True)
    with sc4:
        st.markdown(f"""
        <div class='ecl-card'>
            <div class='ecl-label'>Adverse uplift</div>
            <div class='ecl-value-amber'>+${(ecl_adv-ecl_base)/1e6:.1f}M</div>
            <div style='font-size:11px;color:#475569;margin-top:4px'>additional provision required</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<hr>", unsafe_allow_html=True)
    col1, col2 = st.columns([1, 1.4])

    with col1:
        st.markdown("<div class='section-title'>IFRS 9 stage distribution</div>",
                    unsafe_allow_html=True)

        stage_counts = df['ifrs9_stage'].value_counts()
        stage_colors_map = {
            'Stage 1': '#22c55e',
            'Stage 2': '#f59e0b',
            'Stage 3': '#ef4444'
        }
        colors = [stage_colors_map.get(s, '#64748b') for s in stage_counts.index]

        fig_pie = go.Figure(go.Pie(
            labels=list(stage_counts.index),
            values=stage_counts.values,
            hole=0.65,
            marker=dict(colors=colors, line=dict(color='#0a0e1a', width=2)),
            textinfo='percent',
            textfont=dict(size=12, color='white', family='DM Mono'),
            showlegend=True
        ))
        fig_pie.update_layout(
            paper_bgcolor='#111827',
            plot_bgcolor='#111827',
            font=dict(color='#94a3b8', family='Sora'),
            legend=dict(font=dict(size=11, color='#94a3b8'),
                        bgcolor='#111827', bordercolor='#1e2d4a',
                        x=0.75, y=0.5),
            margin=dict(t=10, b=10, l=10, r=10),
            height=280,
            annotations=[dict(
                text=f"<b>{total_loans:,}</b><br>loans",
                x=0.37, y=0.5,
                font=dict(size=14, color='#e2e8f0', family='DM Mono'),
                showarrow=False
            )]
        )
        st.plotly_chart(fig_pie, use_container_width=True)

        stage_ecl_map = df.groupby('ifrs9_stage')['ecl_base'].sum()
        cols = st.columns(3)
        for i, (stage, color) in enumerate([
            ('Stage 1','#22c55e'), ('Stage 2','#f59e0b'), ('Stage 3','#ef4444')
        ]):
            val = stage_ecl_map.get(stage, 0)
            cols[i].markdown(f"""
            <div style='background:#111827;border:1px solid #1e2d4a;border-radius:10px;
                        padding:10px;text-align:center;margin-top:4px'>
                <div style='font-size:15px;font-family:DM Mono,monospace;
                            font-weight:500;color:{color}'>${val/1e6:.1f}M</div>
                <div style='font-size:10px;color:#475569;margin-top:2px'>{stage}</div>
            </div>""", unsafe_allow_html=True)

    with col2:
        st.markdown("<div class='section-title'>Mean ECL by loan grade</div>",
                    unsafe_allow_html=True)

        grade_ecl    = df.groupby('grade')['ecl_base'].mean().sort_index()
        grade_colors = ['#22c55e','#84cc16','#eab308',
                        '#f97316','#ef4444','#dc2626','#991b1b']

        fig_bar = go.Figure(go.Bar(
            x=list(grade_ecl.index),
            y=list(grade_ecl.values),
            marker=dict(color=grade_colors[:len(grade_ecl)],
                        line=dict(color='#0a0e1a', width=1)),
            text=[f'${v:,.0f}' for v in grade_ecl.values],
            textposition='outside',
            textfont=dict(size=11, color='#94a3b8', family='DM Mono')
        ))
        fig_bar.update_layout(
            paper_bgcolor='#111827', plot_bgcolor='#111827',
            font=dict(color='#94a3b8', family='Sora'),
            xaxis=dict(title='Loan Grade', color='#475569',
                       gridcolor='#1e2d4a', showgrid=False),
            yaxis=dict(title='Mean ECL ($)', color='#475569',
                       gridcolor='#1e2d4a', tickprefix='$', tickformat=','),
            margin=dict(t=30, b=40, l=60, r=20),
            height=280, showlegend=False
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    col1, col2 = st.columns([1.4, 1])

    with col1:
        st.markdown("<div class='section-title'>Mean ECL by loan purpose</div>",
                    unsafe_allow_html=True)

        purpose_ecl = df.groupby('purpose')['ecl_base'].mean().sort_values()

        fig_h = go.Figure(go.Bar(
            y=list(purpose_ecl.index),
            x=list(purpose_ecl.values),
            orientation='h',
            marker=dict(
                color=list(purpose_ecl.values),
                colorscale=[[0,'#1d4ed8'],[0.5,'#7c3aed'],[1,'#ef4444']],
                line=dict(color='#0a0e1a', width=0.5)
            ),
            text=[f'${v:,.0f}' for v in purpose_ecl.values],
            textposition='outside',
            textfont=dict(size=10, color='#64748b', family='DM Mono')
        ))
        fig_h.update_layout(
            paper_bgcolor='#111827', plot_bgcolor='#111827',
            font=dict(color='#94a3b8', family='Sora'),
            xaxis=dict(color='#475569', gridcolor='#1e2d4a',
                       tickprefix='$', tickformat=','),
            yaxis=dict(color='#475569', gridcolor='#1e2d4a'),
            margin=dict(t=10, b=40, l=130, r=80),
            height=350, showlegend=False
        )
        st.plotly_chart(fig_h, use_container_width=True)

    with col2:
        st.markdown("<div class='section-title'>Total ECL provision by stage</div>",
                    unsafe_allow_html=True)

        stage_ecl = df.groupby('ifrs9_stage')['ecl_base'].sum()
        s_labels  = ['Stage 1', 'Stage 2', 'Stage 3']
        s_values  = [stage_ecl.get(k, 0) for k in s_labels]
        s_colors  = ['#22c55e', '#f59e0b', '#ef4444']

        fig_stage = go.Figure(go.Bar(
            x=s_labels, y=s_values,
            marker=dict(color=s_colors, line=dict(color='#0a0e1a', width=1)),
            text=[f'${v/1e6:.1f}M' for v in s_values],
            textposition='outside',
            textfont=dict(size=12, color='#94a3b8', family='DM Mono')
        ))
        fig_stage.update_layout(
            paper_bgcolor='#111827', plot_bgcolor='#111827',
            font=dict(color='#94a3b8', family='Sora'),
            xaxis=dict(color='#475569', showgrid=False),
            yaxis=dict(color='#475569', gridcolor='#1e2d4a',
                       tickprefix='$', tickformat=','),
            margin=dict(t=30, b=40, l=60, r=20),
            height=350, showlegend=False
        )
        st.plotly_chart(fig_stage, use_container_width=True)

    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>Regulatory backtesting — all 4 tests passed</div>",
                unsafe_allow_html=True)

    bt1, bt2, bt3, bt4 = st.columns(4)
    for col, name, val, result, color in [
        (bt1, "Kupiec Test",         "p-value: 0.7935",  "PASS",   "#22c55e"),
        (bt2, "Traffic Light",       "deviation: 0.32%", "GREEN",  "#22c55e"),
        (bt3, "Calibration",         "error: 0.0080",    "PASS",   "#22c55e"),
        (bt4, "OOT PSI (2007–2018)", "PSI: 0.0466",      "STABLE", "#3b82f6"),
    ]:
        col.markdown(f"""
        <div class='ecl-card' style='text-align:center'>
            <div style='font-size:18px;font-weight:600;color:{color};
                        font-family:DM Mono,monospace'>{result}</div>
            <div style='font-size:12px;font-weight:500;color:#94a3b8;
                        margin:4px 0 2px'>{name}</div>
            <div style='font-size:11px;color:#475569;font-family:DM Mono,monospace'>{val}</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>Top 10 highest risk loans</div>",
                unsafe_allow_html=True)

    top10 = df.nlargest(10, 'ecl_base')[
        ['id', 'loan_amnt', 'grade', 'purpose',
         'pd_probability', 'lgd_predicted', 'ead', 'ecl_base', 'ifrs9_stage']
    ].copy()

    top10.columns = ['Loan ID', 'Loan Amount', 'Grade', 'Purpose',
                     'PD', 'LGD', 'EAD', 'ECL (Base)', 'IFRS 9 Stage']

    top10['Loan Amount'] = top10['Loan Amount'].apply(lambda x: f'${x:,.0f}')
    top10['PD']          = top10['PD'].apply(lambda x: f'{x*100:.1f}%')
    top10['LGD']         = top10['LGD'].apply(lambda x: f'{x*100:.1f}%')
    top10['EAD']         = top10['EAD'].apply(lambda x: f'${x:,.0f}')
    top10['ECL (Base)']  = top10['ECL (Base)'].apply(lambda x: f'${x:,.0f}')

    st.dataframe(top10, use_container_width=True, hide_index=True)