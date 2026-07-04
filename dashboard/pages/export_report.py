# Page — Export Report

import streamlit as st
import pandas as pd
import io

@st.cache_data
def load_data():
    ecl  = pd.read_csv('data/ecl_final_results.csv')
    pd_p = pd.read_csv('data/pd_predictions.csv')
    lgd  = pd.read_csv('data/lgd_predictions.csv')
    return ecl, pd_p, lgd

def show():
    ecl_df, pd_df, lgd_df = load_data()

    st.markdown("""
    <div class='page-header'>Export Report</div>
    <div class='page-subheader'>
        Download model outputs and ECL results
    </div>
    """, unsafe_allow_html=True)

    # ── Portfolio summary card ───────────────────────────────
    total_ead  = ecl_df['ead'].sum()
    total_ecl  = ecl_df['ecl_base'].sum()
    mean_pd    = ecl_df['pd_probability'].mean()
    mean_lgd   = ecl_df['lgd_predicted'].mean()

    st.markdown(f"""
    <div class='ecl-card-accent' style='margin-bottom:1.5rem'>
        <div class='section-title' style='margin-top:0'>Portfolio snapshot</div>
        <div style='display:grid;grid-template-columns:repeat(4,1fr);gap:1rem;margin-top:0.75rem'>
            <div>
                <div class='ecl-label'>Total Loans</div>
                <div class='ecl-value-blue'>{len(ecl_df):,}</div>
            </div>
            <div>
                <div class='ecl-label'>Total EAD</div>
                <div class='ecl-value-blue'>${total_ead/1e6:.1f}M</div>
            </div>
            <div>
                <div class='ecl-label'>Base ECL Provision</div>
                <div class='ecl-value-blue'>${total_ecl/1e6:.1f}M</div>
            </div>
            <div>
                <div class='ecl-label'>ECL / EAD</div>
                <div class='ecl-value-blue'>{total_ecl/total_ead*100:.2f}%</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<hr>", unsafe_allow_html=True)

    # ── Download buttons ─────────────────────────────────────
    st.markdown("<div class='section-title'>Download files</div>",
                unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        <div class='ecl-card' style='margin-bottom:0.75rem'>
            <div class='ecl-label'>ECL Final Results</div>
            <div style='font-size:13px;color:#94a3b8;margin:6px 0 12px;line-height:1.6'>
                Full loan-level ECL with PD, LGD, EAD,
                IFRS 9 stage, and macro scenarios.
                <br>122,216 rows.
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.download_button(
            label="Download ECL Results (CSV)",
            data=ecl_df.to_csv(index=False).encode('utf-8'),
            file_name='ecl_final_results.csv',
            mime='text/csv'
        )

    with col2:
        st.markdown("""
        <div class='ecl-card' style='margin-bottom:0.75rem'>
            <div class='ecl-label'>PD Predictions</div>
            <div style='font-size:13px;color:#94a3b8;margin:6px 0 12px;line-height:1.6'>
                Calibrated PD probabilities, raw scores,
                and actual defaults for the test set.
                <br>24,444 rows.
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.download_button(
            label="Download PD Predictions (CSV)",
            data=pd_df.to_csv(index=False).encode('utf-8'),
            file_name='pd_predictions.csv',
            mime='text/csv'
        )

    with col3:
        st.markdown("""
        <div class='ecl-card' style='margin-bottom:0.75rem'>
            <div class='ecl-label'>LGD Predictions</div>
            <div style='font-size:13px;color:#94a3b8;margin:6px 0 12px;line-height:1.6'>
                Predicted LGD for the full portfolio
                of 122,216 loans using loan
                characteristics only.
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.download_button(
            label="Download LGD Predictions (CSV)",
            data=lgd_df.to_csv(index=False).encode('utf-8'),
            file_name='lgd_predictions.csv',
            mime='text/csv'
        )

    # ── Summary report ───────────────────────────────────────
    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>Portfolio summary report</div>",
                unsafe_allow_html=True)

    stage_ecl = ecl_df.groupby('ifrs9_stage')['ecl_base'].sum()

    summary = pd.DataFrame([
        ['Total loans',                f"{len(ecl_df):,}"],
        ['Total EAD',                  f"${total_ead:,.0f}"],
        ['Base ECL provision',         f"${total_ecl:,.0f}"],
        ['ECL as % of EAD',            f"{total_ecl/total_ead*100:.2f}%"],
        ['Adverse ECL',                f"${ecl_df['ecl_adverse'].sum():,.0f}" if 'ecl_adverse' in ecl_df.columns else 'N/A'],
        ['Optimistic ECL',             f"${ecl_df['ecl_optimistic'].sum():,.0f}" if 'ecl_optimistic' in ecl_df.columns else 'N/A'],
        ['Mean PD (calibrated)',       f"{mean_pd*100:.2f}%"],
        ['Mean LGD',                   f"{mean_lgd*100:.2f}%"],
        ['Stage 1 loans',              f"{(ecl_df['ifrs9_stage']=='Stage 1').sum():,}"],
        ['Stage 2 loans',              f"{(ecl_df['ifrs9_stage']=='Stage 2').sum():,}"],
        ['Stage 3 loans',              f"{(ecl_df['ifrs9_stage']=='Stage 3').sum():,}"],
        ['Stage 1 ECL',                f"${stage_ecl.get('Stage 1', 0):,.0f}"],
        ['Stage 2 ECL',                f"${stage_ecl.get('Stage 2', 0):,.0f}"],
        ['Stage 3 ECL',                f"${stage_ecl.get('Stage 3', 0):,.0f}"],
        ['PD model',                   'Gradient Boosting'],
        ['AUC-ROC',                    '0.7115'],
        ['Gini coefficient',           '0.4230'],
        ['KS statistic',               '0.3046'],
        ['LGD model',                  'Gradient Boosting'],
        ['LGD R²',                     '0.1914'],
        ['LGD RMSE',                   '0.2007'],
        ['EAD method',                 'Hybrid amortisation'],
        ['Calibration',                'Platt Scaling'],
        ['Calibration gap',            '0.07%'],
        ['Kupiec test',                'PASS (p=0.7935)'],
        ['Traffic Light',              'GREEN (0.32% deviation)'],
        ['Calibration test',           'PASS (error=0.0080)'],
        ['OOT PSI',                    'STABLE (PSI=0.0466)'],
    ], columns=['Metric', 'Value'])

    st.dataframe(summary, use_container_width=True, hide_index=True)

    st.download_button(
        label="Download Summary Report (CSV)",
        data=summary.to_csv(index=False).encode('utf-8'),
        file_name='ecl_summary_report.csv',
        mime='text/csv'
    )