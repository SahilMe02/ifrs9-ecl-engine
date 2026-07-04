# Page — Model Performance
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from sklearn.metrics import roc_curve, roc_auc_score, average_precision_score
from sklearn.metrics import precision_recall_curve, mean_squared_error, r2_score
from scipy.stats import ks_2samp

@st.cache_data
def load_data():
    pd_preds      = pd.read_csv('data/pd_predictions.csv')
    pd_year       = pd.read_csv('data/pd_predictions_with_year.csv')
    lgd_test      = pd.read_csv('data/lgd_predictions_test.csv')
    return pd_preds, pd_year, lgd_test

def show():
    pd_preds, pd_year, lgd_test = load_data()

    st.markdown("""
    <div class='page-header'>Model Performance</div>
    <div class='page-subheader'>
        PD · LGD · Calibration — full diagnostic report
    </div>
    """, unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs([
        "  PD Model  ",
        "  LGD Model  ",
        "  Calibration  "
    ])

    with tab1:

        y_true  = pd_preds['actual_default']
        y_score = pd_preds['pd_probability']
        y_raw   = pd_preds['pd_raw']

        auc     = roc_auc_score(y_true, y_score)
        auc_pr  = average_precision_score(y_true, y_score)
        gini    = 2 * auc - 1
        ks_stat, _ = ks_2samp(
            y_score[y_true == 0],
            y_score[y_true == 1]
        )

        c1, c2, c3, c4, c5 = st.columns(5)
        with c1:
            st.metric("AUC-ROC", f"{auc:.4f}")
        with c2:
            st.metric("AUC-PR", f"{auc_pr:.4f}")
        with c3:
            st.metric("Gini", f"{gini:.4f}")
        with c4:
            st.metric("KS Statistic", f"{ks_stat:.4f}")
        with c5:
            st.metric("Test samples", f"{len(pd_preds):,}")

        st.markdown("""
        <div style='display:flex;gap:8px;margin:0.5rem 0 1.25rem;flex-wrap:wrap'>
            <span style='background:#14532d;color:#86efac;font-size:11px;
                padding:3px 10px;border-radius:20px;font-weight:500'>
                AUC &gt; 0.70 — Good
            </span>
            <span style='background:#14532d;color:#86efac;font-size:11px;
                padding:3px 10px;border-radius:20px;font-weight:500'>
                KS &gt; 0.30 — Good
            </span>
            <span style='background:#14532d;color:#86efac;font-size:11px;
                padding:3px 10px;border-radius:20px;font-weight:500'>
                Gini &gt; 0.40 — Good
            </span>
            <span style='background:#0f1f3d;color:#93c5fd;font-size:11px;
                padding:3px 10px;border-radius:20px;font-weight:500'>
                Model: Gradient Boosting · C=0.01
            </span>
        </div>
        """, unsafe_allow_html=True)

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("<div class='section-title'>ROC Curve</div>",
                        unsafe_allow_html=True)
            fpr, tpr, _ = roc_curve(y_true, y_score)
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=[0, 1], y=[0, 1],
                mode='lines',
                line=dict(color='#475569', width=1, dash='dash'),
                name='Random (AUC = 0.50)',
                showlegend=True
            ))
            fig.add_trace(go.Scatter(
                x=fpr, y=tpr,
                mode='lines',
                line=dict(color='#3b82f6', width=2.5),
                fill='tozeroy',
                fillcolor='rgba(59,130,246,0.08)',
                name=f'Gradient Boosting (AUC = {auc:.4f})'
            ))
            fig.update_layout(
                paper_bgcolor='#111827', plot_bgcolor='#111827',
                font=dict(color='#94a3b8', family='Sora', size=11),
                xaxis=dict(title='False Positive Rate', color='#475569',
                           gridcolor='#1e2d4a', zeroline=False),
                yaxis=dict(title='True Positive Rate', color='#475569',
                           gridcolor='#1e2d4a', zeroline=False),
                legend=dict(bgcolor='#111827', bordercolor='#1e2d4a',
                            font=dict(size=10)),
                margin=dict(t=10, b=40, l=50, r=10),
                height=300
            )
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.markdown("<div class='section-title'>Precision-Recall Curve</div>",
                        unsafe_allow_html=True)
            prec, rec, _ = precision_recall_curve(y_true, y_score)
            baseline = y_true.mean()
            fig2 = go.Figure()
            fig2.add_trace(go.Scatter(
                x=[0, 1], y=[baseline, baseline],
                mode='lines',
                line=dict(color='#475569', width=1, dash='dash'),
                name=f'Baseline (AP = {baseline:.2f})'
            ))
            fig2.add_trace(go.Scatter(
                x=rec, y=prec,
                mode='lines',
                line=dict(color='#a78bfa', width=2.5),
                fill='tozeroy',
                fillcolor='rgba(167,139,250,0.08)',
                name=f'GB Model (AP = {auc_pr:.4f})'
            ))
            fig2.update_layout(
                paper_bgcolor='#111827', plot_bgcolor='#111827',
                font=dict(color='#94a3b8', family='Sora', size=11),
                xaxis=dict(title='Recall', color='#475569',
                           gridcolor='#1e2d4a', zeroline=False),
                yaxis=dict(title='Precision', color='#475569',
                           gridcolor='#1e2d4a', zeroline=False),
                legend=dict(bgcolor='#111827', bordercolor='#1e2d4a',
                            font=dict(size=10)),
                margin=dict(t=10, b=40, l=50, r=10),
                height=300
            )
            st.plotly_chart(fig2, use_container_width=True)

        col3, col4 = st.columns(2)

        with col3:
            st.markdown("<div class='section-title'>PD Score Distribution</div>",
                        unsafe_allow_html=True)
            fig3 = go.Figure()
            fig3.add_trace(go.Histogram(
                x=y_score[y_true == 0],
                nbinsx=50, name='Non-Default',
                marker_color='#3b82f6', opacity=0.6,
                histnorm='probability density'
            ))
            fig3.add_trace(go.Histogram(
                x=y_score[y_true == 1],
                nbinsx=50, name='Default',
                marker_color='#ef4444', opacity=0.6,
                histnorm='probability density'
            ))
            fig3.update_layout(
                barmode='overlay',
                paper_bgcolor='#111827', plot_bgcolor='#111827',
                font=dict(color='#94a3b8', family='Sora', size=11),
                xaxis=dict(title='PD Score', color='#475569',
                           gridcolor='#1e2d4a'),
                yaxis=dict(title='Density', color='#475569',
                           gridcolor='#1e2d4a'),
                legend=dict(bgcolor='#111827', bordercolor='#1e2d4a'),
                margin=dict(t=10, b=40, l=50, r=10),
                height=280
            )
            st.plotly_chart(fig3, use_container_width=True)

        with col4:
            st.markdown("<div class='section-title'>KS Plot</div>",
                        unsafe_allow_html=True)
            thresholds  = np.linspace(0, 1, 200)
            tpr_ks, fpr_ks = [], []
            for t in thresholds:
                tpr_ks.append((y_score[y_true == 1] >= t).mean())
                fpr_ks.append((y_score[y_true == 0] >= t).mean())
            ks_diff = np.abs(np.array(tpr_ks) - np.array(fpr_ks))
            ks_idx  = ks_diff.argmax()

            fig4 = go.Figure()
            fig4.add_trace(go.Scatter(
                x=thresholds, y=tpr_ks,
                mode='lines', name='Default rate',
                line=dict(color='#ef4444', width=2)
            ))
            fig4.add_trace(go.Scatter(
                x=thresholds, y=fpr_ks,
                mode='lines', name='Non-default rate',
                line=dict(color='#3b82f6', width=2)
            ))
            fig4.add_vline(
                x=thresholds[ks_idx],
                line=dict(color='#f59e0b', width=1.5, dash='dot'),
                annotation_text=f"KS={ks_stat:.3f}",
                annotation_font_color='#f59e0b',
                annotation_font_size=11
            )
            fig4.update_layout(
                paper_bgcolor='#111827', plot_bgcolor='#111827',
                font=dict(color='#94a3b8', family='Sora', size=11),
                xaxis=dict(title='Threshold', color='#475569',
                           gridcolor='#1e2d4a'),
                yaxis=dict(title='Cumulative Rate', color='#475569',
                           gridcolor='#1e2d4a'),
                legend=dict(bgcolor='#111827', bordercolor='#1e2d4a'),
                margin=dict(t=10, b=40, l=50, r=10),
                height=280
            )
            st.plotly_chart(fig4, use_container_width=True)

    with tab2:

        if 'actual_lgd' not in lgd_test.columns or 'lgd_predicted' not in lgd_test.columns:
            st.warning("lgd_predictions_test.csv needs 'actual_lgd' and 'lgd_predicted' columns.")
            return

        y_lgd_true = lgd_test['actual_lgd']
        y_lgd_pred = lgd_test['lgd_predicted']

        rmse = np.sqrt(mean_squared_error(y_lgd_true, y_lgd_pred))
        mae  = np.mean(np.abs(y_lgd_true - y_lgd_pred))
        r2   = r2_score(y_lgd_true, y_lgd_pred)
        mbe  = np.mean(y_lgd_pred - y_lgd_true)

        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.metric("RMSE", f"{rmse:.4f}")
        with c2:
            st.metric("MAE", f"{mae:.4f}")
        with c3:
            st.metric("R²", f"{r2:.4f}")
        with c4:
            st.metric("Mean Bias Error", f"{mbe:+.4f}")

        st.markdown("""
        <div style='background:#111827;border:1px solid #1e2d4a;border-radius:10px;
            padding:10px 14px;font-size:12px;color:#64748b;margin:0.5rem 0 1.25rem;
            line-height:1.7;font-family:DM Mono,monospace'>
            Note: R² &lt; 0.30 is expected and normal for LGD regression on consumer loans.
            LGD targets are bounded [0,1] with bimodal distribution — academic literature
            reports R² of 0.10–0.25 for this task. RMSE &lt; 0.20 is the primary benchmark.
        </div>
        """, unsafe_allow_html=True)

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("<div class='section-title'>Predicted vs Actual LGD</div>",
                        unsafe_allow_html=True)
            sample = lgd_test.sample(min(2000, len(lgd_test)), random_state=42)
            fig5 = go.Figure()
            fig5.add_trace(go.Scatter(
                x=[0, 1], y=[0, 1],
                mode='lines',
                line=dict(color='#ef4444', width=1.5, dash='dash'),
                name='Perfect prediction'
            ))
            fig5.add_trace(go.Scatter(
                x=sample['actual_lgd'],
                y=sample['lgd_predicted'],
                mode='markers',
                marker=dict(color='#f97316', size=3, opacity=0.4),
                name='Predictions'
            ))
            fig5.update_layout(
                paper_bgcolor='#111827', plot_bgcolor='#111827',
                font=dict(color='#94a3b8', family='Sora', size=11),
                xaxis=dict(title='Actual LGD', color='#475569',
                           gridcolor='#1e2d4a', range=[0, 1]),
                yaxis=dict(title='Predicted LGD', color='#475569',
                           gridcolor='#1e2d4a', range=[0, 1]),
                legend=dict(bgcolor='#111827', bordercolor='#1e2d4a'),
                margin=dict(t=10, b=40, l=50, r=10),
                height=300
            )
            st.plotly_chart(fig5, use_container_width=True)

        with col2:
            st.markdown("<div class='section-title'>Residuals Plot</div>",
                        unsafe_allow_html=True)
            residuals = y_lgd_true.values - y_lgd_pred.values
            fig6 = go.Figure()
            fig6.add_trace(go.Scatter(
                x=y_lgd_pred,
                y=residuals,
                mode='markers',
                marker=dict(color='#f97316', size=3, opacity=0.4),
                name='Residuals'
            ))
            fig6.add_hline(
                y=0, line=dict(color='#ef4444', width=1.5, dash='dash')
            )
            fig6.update_layout(
                paper_bgcolor='#111827', plot_bgcolor='#111827',
                font=dict(color='#94a3b8', family='Sora', size=11),
                xaxis=dict(title='Predicted LGD', color='#475569',
                           gridcolor='#1e2d4a'),
                yaxis=dict(title='Residual (Actual − Predicted)',
                           color='#475569', gridcolor='#1e2d4a'),
                legend=dict(bgcolor='#111827', bordercolor='#1e2d4a'),
                margin=dict(t=10, b=40, l=50, r=10),
                height=300
            )
            st.plotly_chart(fig6, use_container_width=True)

        col3, col4 = st.columns(2)

        with col3:
            st.markdown("<div class='section-title'>LGD Distribution — Actual vs Predicted</div>",
                        unsafe_allow_html=True)
            fig7 = go.Figure()
            fig7.add_trace(go.Histogram(
                x=y_lgd_true, nbinsx=40,
                name='Actual LGD',
                marker_color='#22c55e', opacity=0.6,
                histnorm='probability density'
            ))
            fig7.add_trace(go.Histogram(
                x=y_lgd_pred, nbinsx=40,
                name='Predicted LGD',
                marker_color='#f97316', opacity=0.6,
                histnorm='probability density'
            ))
            fig7.update_layout(
                barmode='overlay',
                paper_bgcolor='#111827', plot_bgcolor='#111827',
                font=dict(color='#94a3b8', family='Sora', size=11),
                xaxis=dict(title='LGD', color='#475569',
                           gridcolor='#1e2d4a'),
                yaxis=dict(title='Density', color='#475569',
                           gridcolor='#1e2d4a'),
                legend=dict(bgcolor='#111827', bordercolor='#1e2d4a'),
                margin=dict(t=10, b=40, l=50, r=10),
                height=280
            )
            st.plotly_chart(fig7, use_container_width=True)

        with col4:
            st.markdown("<div class='section-title'>Error Distribution</div>",
                        unsafe_allow_html=True)
            fig8 = go.Figure()
            fig8.add_trace(go.Histogram(
                x=residuals, nbinsx=50,
                marker_color='#a78bfa', opacity=0.75,
                name='Residuals'
            ))
            fig8.add_vline(
                x=0, line=dict(color='#ef4444', width=1.5, dash='dash'),
                annotation_text='Zero error',
                annotation_font_color='#ef4444',
                annotation_font_size=10
            )
            fig8.update_layout(
                paper_bgcolor='#111827', plot_bgcolor='#111827',
                font=dict(color='#94a3b8', family='Sora', size=11),
                xaxis=dict(title='Residual', color='#475569',
                           gridcolor='#1e2d4a'),
                yaxis=dict(title='Count', color='#475569',
                           gridcolor='#1e2d4a'),
                margin=dict(t=10, b=40, l=50, r=10),
                height=280,
                showlegend=False
            )
            st.plotly_chart(fig8, use_container_width=True)

    with tab3:

        actual_dr   = y_true.mean()
        mean_pd_raw = y_raw.mean()
        mean_pd_cal = y_score.mean()

        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.metric("Actual default rate", f"{actual_dr*100:.2f}%")
        with c2:
            st.metric("Mean PD (raw)", f"{mean_pd_raw*100:.2f}%",
                      delta=f"{(mean_pd_raw - actual_dr)*100:+.2f}% gap")
        with c3:
            st.metric("Mean PD (calibrated)", f"{mean_pd_cal*100:.2f}%",
                      delta=f"{(mean_pd_cal - actual_dr)*100:+.2f}% gap")
        with c4:
            st.metric("Calibration method", "Platt Scaling")

        st.markdown("<hr>", unsafe_allow_html=True)
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("<div class='section-title'>Calibration Curve — Bucket Level</div>",
                        unsafe_allow_html=True)
            pd_preds['bucket'] = pd.qcut(y_score, 10, duplicates='drop')
            calib = pd_preds.groupby('bucket', observed=True).agg(
                pred=('pd_probability', 'mean'),
                actual=('actual_default', 'mean')
            ).reset_index()

            fig9 = go.Figure()
            fig9.add_trace(go.Scatter(
                x=[0, 0.5], y=[0, 0.5],
                mode='lines',
                line=dict(color='#475569', width=1.5, dash='dash'),
                name='Perfect calibration'
            ))
            fig9.add_trace(go.Scatter(
                x=calib['pred'], y=calib['actual'],
                mode='lines+markers',
                marker=dict(color='#3b82f6', size=8,
                            line=dict(color='#1d4ed8', width=1.5)),
                line=dict(color='#3b82f6', width=2),
                name='Actual vs Predicted'
            ))
            fig9.update_layout(
                paper_bgcolor='#111827', plot_bgcolor='#111827',
                font=dict(color='#94a3b8', family='Sora', size=11),
                xaxis=dict(title='Mean Predicted PD', color='#475569',
                           gridcolor='#1e2d4a'),
                yaxis=dict(title='Actual Default Rate', color='#475569',
                           gridcolor='#1e2d4a'),
                legend=dict(bgcolor='#111827', bordercolor='#1e2d4a'),
                margin=dict(t=10, b=40, l=50, r=10),
                height=300
            )
            st.plotly_chart(fig9, use_container_width=True)

        with col2:
            st.markdown("<div class='section-title'>Raw vs Calibrated PD Distribution</div>",
                        unsafe_allow_html=True)
            fig10 = go.Figure()
            fig10.add_trace(go.Histogram(
                x=y_raw, nbinsx=50,
                name=f'Raw PD (mean={mean_pd_raw*100:.1f}%)',
                marker_color='#ef4444', opacity=0.5,
                histnorm='probability density'
            ))
            fig10.add_trace(go.Histogram(
                x=y_score, nbinsx=50,
                name=f'Calibrated PD (mean={mean_pd_cal*100:.1f}%)',
                marker_color='#3b82f6', opacity=0.5,
                histnorm='probability density'
            ))
            fig10.add_vline(
                x=actual_dr,
                line=dict(color='#22c55e', width=2, dash='dot'),
                annotation_text=f"Actual DR {actual_dr*100:.1f}%",
                annotation_font_color='#22c55e',
                annotation_font_size=10
            )
            fig10.update_layout(
                barmode='overlay',
                paper_bgcolor='#111827', plot_bgcolor='#111827',
                font=dict(color='#94a3b8', family='Sora', size=11),
                xaxis=dict(title='Probability of Default', color='#475569',
                           gridcolor='#1e2d4a'),
                yaxis=dict(title='Density', color='#475569',
                           gridcolor='#1e2d4a'),
                legend=dict(bgcolor='#111827', bordercolor='#1e2d4a',
                            font=dict(size=10)),
                margin=dict(t=10, b=40, l=50, r=10),
                height=300
            )
            st.plotly_chart(fig10, use_container_width=True)

        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown("<div class='section-title'>Out-of-Time PSI — 2007–2016 vs 2017–2018</div>",
                    unsafe_allow_html=True)

        train_w = pd_year[pd_year['issue_year'] <= 2016]['pd_probability']
        oot_w   = pd_year[pd_year['issue_year'] >= 2017]['pd_probability']

        bins       = np.linspace(0, 1, 11)
        train_dist = np.histogram(train_w, bins=bins)[0] / len(train_w)
        oot_dist   = np.histogram(oot_w,   bins=bins)[0] / len(oot_w)
        train_dist = np.where(train_dist == 0, 1e-4, train_dist)
        oot_dist   = np.where(oot_dist   == 0, 1e-4, oot_dist)
        bucket_psi = (oot_dist - train_dist) * np.log(oot_dist / train_dist)
        total_psi  = bucket_psi.sum()

        psi_result = "STABLE" if total_psi < 0.10 else (
            "MONITOR" if total_psi < 0.25 else "UNSTABLE"
        )
        psi_color  = "#22c55e" if total_psi < 0.10 else (
            "#f59e0b" if total_psi < 0.25 else "#ef4444"
        )

        st.markdown(f"""
        <div style='display:flex;gap:20px;margin-bottom:1rem;flex-wrap:wrap'>
            <div style='background:#111827;border:1px solid #1e2d4a;border-radius:10px;
                padding:12px 20px;text-align:center'>
                <div style='font-size:22px;font-weight:600;color:{psi_color};
                    font-family:DM Mono,monospace'>{total_psi:.4f}</div>
                <div style='font-size:11px;color:#64748b;margin-top:3px'>PSI value</div>
            </div>
            <div style='background:#111827;border:1px solid #1e2d4a;border-radius:10px;
                padding:12px 20px;text-align:center'>
                <div style='font-size:22px;font-weight:600;color:{psi_color};
                    font-family:DM Mono,monospace'>{psi_result}</div>
                <div style='font-size:11px;color:#64748b;margin-top:3px'>Status</div>
            </div>
            <div style='background:#111827;border:1px solid #1e2d4a;border-radius:10px;
                padding:12px 20px;text-align:center'>
                <div style='font-size:22px;font-weight:600;color:#94a3b8;
                    font-family:DM Mono,monospace'>{len(train_w):,}</div>
                <div style='font-size:11px;color:#64748b;margin-top:3px'>Train window loans</div>
            </div>
            <div style='background:#111827;border:1px solid #1e2d4a;border-radius:10px;
                padding:12px 20px;text-align:center'>
                <div style='font-size:22px;font-weight:600;color:#94a3b8;
                    font-family:DM Mono,monospace'>{len(oot_w):,}</div>
                <div style='font-size:11px;color:#64748b;margin-top:3px'>OOT window loans</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        bin_labels = [f"{bins[i]:.1f}–{bins[i+1]:.1f}" for i in range(len(bins)-1)]
        psi_table  = pd.DataFrame({
            'PD Bucket'       : bin_labels,
            'Train proportion': [f"{v:.4f}" for v in train_dist],
            'OOT proportion'  : [f"{v:.4f}" for v in oot_dist],
            'Bucket PSI'      : [f"{v:.4f}" for v in bucket_psi]
        })
        st.dataframe(psi_table, use_container_width=True, hide_index=True)