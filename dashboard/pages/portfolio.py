# Page — Portfolio Analysis

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

@st.cache_data
def load_data():
    df = pd.read_csv('data/ecl_final_results.csv')
    return df

def show():
    df = load_data()

    st.markdown("""
    <div class='page-header'>Portfolio Analysis</div>
    <div class='page-subheader'>
        Loan distribution, risk concentration, and vintage analysis
    </div>
    """, unsafe_allow_html=True)

    total_loans   = len(df)
    total_ead     = df['ead'].sum()
    total_ecl     = df['ecl_base'].sum()
    mean_pd       = df['pd_probability'].mean()
    mean_lgd      = df['lgd_predicted'].mean()
    mean_int_rate = df['int_rate'].mean() if 'int_rate' in df.columns else 0

    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        st.metric("Total Loans", f"{total_loans:,}")
    with c2:
        st.metric("Total EAD", f"${total_ead/1e6:.1f}M")
    with c3:
        st.metric("Base ECL", f"${total_ecl/1e6:.1f}M")
    with c4:
        st.metric("Mean PD", f"{mean_pd*100:.2f}%")
    with c5:
        st.metric("Mean Int Rate", f"{mean_int_rate:.2f}%" if mean_int_rate else "N/A")

    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>Loan composition</div>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1.4, 1, 1])
    grade_colors = ['#22c55e','#84cc16','#eab308','#f97316','#ef4444','#dc2626','#991b1b']

    with col1:
        grade_counts = df['grade'].value_counts().sort_index()
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=list(grade_counts.index), y=list(grade_counts.values),
            marker=dict(color=grade_colors[:len(grade_counts)], line=dict(color='#0a0e1a', width=1)),
            text=[f'{v:,}' for v in grade_counts.values],
            textposition='outside', textfont=dict(size=10, color='#94a3b8')
        ))
        fig.update_layout(
            title=dict(text='Loans by Grade', font=dict(size=13, color='#94a3b8'), x=0),
            paper_bgcolor='#111827', plot_bgcolor='#111827',
            font=dict(color='#94a3b8', family='Sora', size=11),
            xaxis=dict(title='Grade', color='#475569', showgrid=False),
            yaxis=dict(title='Number of Loans', color='#475569', gridcolor='#1e2d4a'),
            margin=dict(t=40, b=40, l=50, r=10), height=280, showlegend=False
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        term_counts = df['term'].value_counts().sort_index()
        term_labels = [f'{t}-month' for t in term_counts.index]
        fig2 = go.Figure(go.Pie(
            labels=term_labels, values=term_counts.values, hole=0.6,
            marker=dict(colors=['#3b82f6', '#a78bfa'], line=dict(color='#0a0e1a', width=2)),
            textinfo='percent', textfont=dict(size=12, color='white', family='DM Mono')
        ))
        fig2.update_layout(
            title=dict(text='Loans by Term', font=dict(size=13, color='#94a3b8'), x=0),
            paper_bgcolor='#111827', plot_bgcolor='#111827',
            font=dict(color='#94a3b8', family='Sora'),
            legend=dict(bgcolor='#111827', bordercolor='#1e2d4a', font=dict(size=11)),
            margin=dict(t=40, b=10, l=10, r=10), height=280,
            annotations=[dict(text=f"{total_loans:,}<br>loans", x=0.5, y=0.5,
                font=dict(size=12, color='#e2e8f0', family='DM Mono'), showarrow=False)]
        )
        st.plotly_chart(fig2, use_container_width=True)

    with col3:
        stage_counts = df['ifrs9_stage'].value_counts().sort_index()
        stage_colors_map = {'Stage 1': '#22c55e', 'Stage 2': '#f59e0b', 'Stage 3': '#ef4444'}
        s_colors = [stage_colors_map.get(s, '#64748b') for s in stage_counts.index]
        fig3 = go.Figure(go.Pie(
            labels=list(stage_counts.index), values=stage_counts.values, hole=0.6,
            marker=dict(colors=s_colors, line=dict(color='#0a0e1a', width=2)),
            textinfo='percent', textfont=dict(size=12, color='white', family='DM Mono')
        ))
        fig3.update_layout(
            title=dict(text='IFRS 9 Stages', font=dict(size=13, color='#94a3b8'), x=0),
            paper_bgcolor='#111827', plot_bgcolor='#111827',
            font=dict(color='#94a3b8', family='Sora'),
            legend=dict(bgcolor='#111827', bordercolor='#1e2d4a', font=dict(size=11)),
            margin=dict(t=40, b=10, l=10, r=10), height=280
        )
        st.plotly_chart(fig3, use_container_width=True)

    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>Risk by grade</div>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)

    with col1:
        grade_pd = df.groupby('grade')['pd_probability'].mean().sort_index()
        fig4 = go.Figure()
        fig4.add_trace(go.Bar(
            x=list(grade_pd.index), y=list(grade_pd.values * 100),
            marker=dict(color='#3b82f6', line=dict(color='#0a0e1a', width=1)),
            text=[f'{v*100:.1f}%' for v in grade_pd.values],
            textposition='outside', textfont=dict(size=10, color='#94a3b8')
        ))
        fig4.update_layout(
            title=dict(text='Mean PD by Grade (%)', font=dict(size=13, color='#94a3b8'), x=0),
            paper_bgcolor='#111827', plot_bgcolor='#111827',
            font=dict(color='#94a3b8', family='Sora', size=11),
            xaxis=dict(title='Grade', color='#475569', showgrid=False),
            yaxis=dict(title='Mean PD (%)', color='#475569', gridcolor='#1e2d4a'),
            margin=dict(t=40, b=40, l=50, r=10), height=280, showlegend=False
        )
        st.plotly_chart(fig4, use_container_width=True)

    with col2:
        grade_lgd = df.groupby('grade')['lgd_predicted'].mean().sort_index()
        fig5 = go.Figure()
        fig5.add_trace(go.Bar(
            x=list(grade_lgd.index), y=list(grade_lgd.values * 100),
            marker=dict(color=grade_colors[:len(grade_lgd)], line=dict(color='#0a0e1a', width=1)),
            text=[f'{v*100:.1f}%' for v in grade_lgd.values],
            textposition='outside', textfont=dict(size=10, color='#94a3b8')
        ))
        fig5.update_layout(
            title=dict(text='Mean LGD by Grade (%)', font=dict(size=13, color='#94a3b8'), x=0),
            paper_bgcolor='#111827', plot_bgcolor='#111827',
            font=dict(color='#94a3b8', family='Sora', size=11),
            xaxis=dict(title='Grade', color='#475569', showgrid=False),
            yaxis=dict(title='Mean LGD (%)', color='#475569', gridcolor='#1e2d4a'),
            margin=dict(t=40, b=40, l=50, r=10), height=280, showlegend=False
        )
        st.plotly_chart(fig5, use_container_width=True)

    if 'issue_year' in df.columns:
        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown("<div class='section-title'>Vintage analysis</div>", unsafe_allow_html=True)
        col1, col2 = st.columns(2)

        with col1:
            vintage = df.groupby('issue_year').agg(
                loans=('id', 'count'),
                mean_pd=('pd_probability', 'mean'),
                total_ecl=('ecl_base', 'sum')
            ).reset_index()
            fig6 = go.Figure()
            fig6.add_trace(go.Bar(
                x=vintage['issue_year'], y=vintage['loans'], name='Loan count',
                marker=dict(color='#3b82f6', opacity=0.8, line=dict(color='#0a0e1a', width=1))
            ))
            fig6.add_trace(go.Scatter(
                x=vintage['issue_year'], y=vintage['mean_pd'] * 100,
                name='Mean PD (%)', yaxis='y2', mode='lines+markers',
                line=dict(color='#ef4444', width=2), marker=dict(size=6, color='#ef4444')
            ))
            fig6.update_layout(
                title=dict(text='Loans & Mean PD by Vintage Year', font=dict(size=13, color='#94a3b8'), x=0),
                paper_bgcolor='#111827', plot_bgcolor='#111827',
                font=dict(color='#94a3b8', family='Sora', size=11),
                xaxis=dict(title='Issue Year', color='#475569', showgrid=False, tickmode='linear'),
                yaxis=dict(title='Loan Count', color='#3b82f6', gridcolor='#1e2d4a'),
                yaxis2=dict(title='Mean PD (%)', color='#ef4444', overlaying='y', side='right', showgrid=False),
                legend=dict(bgcolor='#111827', bordercolor='#1e2d4a', font=dict(size=10)),
                margin=dict(t=40, b=40, l=50, r=60), height=300
            )
            st.plotly_chart(fig6, use_container_width=True)

        with col2:
            fig7 = go.Figure()
            fig7.add_trace(go.Bar(
                x=vintage['issue_year'], y=vintage['total_ecl'] / 1e6,
                marker=dict(
                    color=vintage['total_ecl'],
                    colorscale=[[0, '#1d4ed8'], [0.5, '#7c3aed'], [1, '#ef4444']],
                    line=dict(color='#0a0e1a', width=1)
                ),
                text=[f'${v:.1f}M' for v in vintage['total_ecl'] / 1e6],
                textposition='outside', textfont=dict(size=9, color='#94a3b8')
            ))
            fig7.update_layout(
                title=dict(text='Total ECL by Vintage Year ($M)', font=dict(size=13, color='#94a3b8'), x=0),
                paper_bgcolor='#111827', plot_bgcolor='#111827',
                font=dict(color='#94a3b8', family='Sora', size=11),
                xaxis=dict(title='Issue Year', color='#475569', showgrid=False, tickmode='linear'),
                yaxis=dict(title='Total ECL ($M)', color='#475569', gridcolor='#1e2d4a'),
                margin=dict(t=40, b=40, l=50, r=10), height=300, showlegend=False
            )
            st.plotly_chart(fig7, use_container_width=True)

    if 'purpose' in df.columns:
        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown("<div class='section-title'>Loan purpose breakdown</div>", unsafe_allow_html=True)
        col1, col2 = st.columns(2)

        with col1:
            purpose_counts = df['purpose'].value_counts().head(10)
            fig8 = go.Figure(go.Bar(
                y=list(purpose_counts.index), x=list(purpose_counts.values), orientation='h',
                marker=dict(color=list(purpose_counts.values),
                    colorscale=[[0, '#1d4ed8'], [1, '#7c3aed']], line=dict(color='#0a0e1a', width=0.5)),
                text=[f'{v:,}' for v in purpose_counts.values],
                textposition='outside', textfont=dict(size=10, color='#64748b')
            ))
            fig8.update_layout(
                title=dict(text='Loan Count by Purpose (Top 10)', font=dict(size=13, color='#94a3b8'), x=0),
                paper_bgcolor='#111827', plot_bgcolor='#111827',
                font=dict(color='#94a3b8', family='Sora', size=11),
                xaxis=dict(color='#475569', gridcolor='#1e2d4a'),
                yaxis=dict(color='#475569'),
                margin=dict(t=40, b=40, l=130, r=60), height=320, showlegend=False
            )
            st.plotly_chart(fig8, use_container_width=True)

        with col2:
            purpose_pd = df.groupby('purpose').agg(
                mean_pd=('pd_probability', 'mean')
            ).sort_values('mean_pd', ascending=True).head(10)
            fig9 = go.Figure(go.Bar(
                y=list(purpose_pd.index), x=list(purpose_pd['mean_pd'] * 100), orientation='h',
                marker=dict(color=list(purpose_pd['mean_pd']),
                    colorscale=[[0, '#22c55e'], [0.5, '#f59e0b'], [1, '#ef4444']],
                    line=dict(color='#0a0e1a', width=0.5)),
                text=[f'{v*100:.1f}%' for v in purpose_pd['mean_pd']],
                textposition='outside', textfont=dict(size=10, color='#64748b')
            ))
            fig9.update_layout(
                title=dict(text='Mean PD by Purpose (%)', font=dict(size=13, color='#94a3b8'), x=0),
                paper_bgcolor='#111827', plot_bgcolor='#111827',
                font=dict(color='#94a3b8', family='Sora', size=11),
                xaxis=dict(title='Mean PD (%)', color='#475569', gridcolor='#1e2d4a'),
                yaxis=dict(color='#475569'),
                margin=dict(t=40, b=40, l=130, r=60), height=320, showlegend=False
            )
            st.plotly_chart(fig9, use_container_width=True)

    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>ECL concentration</div>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)

    with col1:
        grade_ecl_total = df.groupby('grade')['ecl_base'].sum().sort_index()
        fig10 = go.Figure(go.Bar(
            x=list(grade_ecl_total.index), y=list(grade_ecl_total.values / 1e6),
            marker=dict(color=grade_colors[:len(grade_ecl_total)], line=dict(color='#0a0e1a', width=1)),
            text=[f'${v/1e6:.1f}M' for v in grade_ecl_total.values],
            textposition='outside', textfont=dict(size=10, color='#94a3b8')
        ))
        fig10.update_layout(
            title=dict(text='Total ECL by Grade ($M)', font=dict(size=13, color='#94a3b8'), x=0),
            paper_bgcolor='#111827', plot_bgcolor='#111827',
            font=dict(color='#94a3b8', family='Sora', size=11),
            xaxis=dict(title='Grade', color='#475569', showgrid=False),
            yaxis=dict(title='Total ECL ($M)', color='#475569', gridcolor='#1e2d4a'),
            margin=dict(t=40, b=40, l=50, r=10), height=280, showlegend=False
        )
        st.plotly_chart(fig10, use_container_width=True)

    with col2:
        ecl_sorted = df['ecl_base'].sort_values(ascending=False).reset_index(drop=True)
        cumulative = ecl_sorted.cumsum() / ecl_sorted.sum() * 100
        loan_pct   = (ecl_sorted.index + 1) / len(ecl_sorted) * 100
        fig11 = go.Figure()
        fig11.add_trace(go.Scatter(
            x=loan_pct, y=cumulative, mode='lines',
            line=dict(color='#3b82f6', width=2.5),
            fill='tozeroy', fillcolor='rgba(59,130,246,0.08)'
        ))
        fig11.add_hline(y=80, line=dict(color='#f59e0b', width=1, dash='dash'),
                        annotation_text='80% of ECL', annotation_font_color='#f59e0b',
                        annotation_font_size=10)
        fig11.update_layout(
            title=dict(text='ECL Concentration Curve', font=dict(size=13, color='#94a3b8'), x=0),
            paper_bgcolor='#111827', plot_bgcolor='#111827',
            font=dict(color='#94a3b8', family='Sora', size=11),
            xaxis=dict(title='% of Loans (sorted by ECL)', color='#475569', gridcolor='#1e2d4a'),
            yaxis=dict(title='Cumulative % of ECL', color='#475569', gridcolor='#1e2d4a'),
            margin=dict(t=40, b=40, l=50, r=10), height=280, showlegend=False
        )
        st.plotly_chart(fig11, use_container_width=True)

    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>Loan explorer</div>", unsafe_allow_html=True)

    col_f1, col_f2, col_f3 = st.columns(3)
    with col_f1:
        grades    = ['All'] + sorted(df['grade'].dropna().unique().tolist())
        sel_grade = st.selectbox('Filter by Grade', grades)
    with col_f2:
        stages    = ['All'] + sorted(df['ifrs9_stage'].dropna().unique().tolist())
        sel_stage = st.selectbox('Filter by Stage', stages)
    with col_f3:
        top_n = st.selectbox('Show top N by ECL', [10, 25, 50, 100])

    filtered = df.copy()
    if sel_grade != 'All':
        filtered = filtered[filtered['grade'] == sel_grade]
    if sel_stage != 'All':
        filtered = filtered[filtered['ifrs9_stage'] == sel_stage]

    display_cols = ['id', 'loan_amnt', 'grade', 'purpose',
                    'pd_probability', 'lgd_predicted', 'ead', 'ecl_base', 'ifrs9_stage']
    available = [c for c in display_cols if c in filtered.columns]
    top_df    = filtered.nlargest(top_n, 'ecl_base')[available].copy()
    top_df    = top_df.rename(columns={
        'id': 'Loan ID', 'loan_amnt': 'Loan Amount', 'grade': 'Grade',
        'purpose': 'Purpose', 'pd_probability': 'PD', 'lgd_predicted': 'LGD',
        'ead': 'EAD', 'ecl_base': 'ECL (Base)', 'ifrs9_stage': 'Stage'
    })
    if 'Loan Amount' in top_df.columns:
        top_df['Loan Amount'] = top_df['Loan Amount'].apply(lambda x: f'${x:,.0f}')
    if 'PD' in top_df.columns:
        top_df['PD'] = top_df['PD'].apply(lambda x: f'{x*100:.1f}%')
    if 'LGD' in top_df.columns:
        top_df['LGD'] = top_df['LGD'].apply(lambda x: f'{x*100:.1f}%')
    if 'EAD' in top_df.columns:
        top_df['EAD'] = top_df['EAD'].apply(lambda x: f'${x:,.0f}')
    if 'ECL (Base)' in top_df.columns:
        top_df['ECL (Base)'] = top_df['ECL (Base)'].apply(lambda x: f'${x:,.0f}')

    st.markdown(f"""
    <div style='font-size:12px;color:#64748b;margin-bottom:8px'>
        Showing top {top_n} loans by ECL
        {f"· Grade {sel_grade}" if sel_grade != "All" else ""}
        {f"· {sel_stage}" if sel_stage != "All" else ""}
        · {len(filtered):,} loans match filter
    </div>
    """, unsafe_allow_html=True)

    st.dataframe(top_df, use_container_width=True, hide_index=True)