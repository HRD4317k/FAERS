import streamlit as st
import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

METRICS_PATH = Path(__file__).parent.parent.parent / "data" / "processed" / "model_metrics.json"

st.set_page_config(page_title="Advanced Models", layout="wide", page_icon="🤖")
st.title("🤖 Advanced Predictive Models")
st.markdown("Comparing **Lasso Regression, Random Forest, XGBoost** and conceptual **Transformer** for predicting Adverse Events from drug exposure profiles.")

if METRICS_PATH.exists():
    with open(METRICS_PATH, "r") as f:
        data = json.load(f)

    st.subheader(f"🎯 Target Prediction: `{data.get('Target', 'Unknown')}`")
    models = data.get("Models", {})

    rows = []
    for name, m in models.items():
        rows.append({"Model": name, **{k: v for k, v in m.items() if k != "Note"}})
    df = pd.DataFrame(rows)

    # Metrics table
    metric_cols = ['Accuracy', 'Precision', 'Recall', 'F1 Score', 'ROC AUC']
    metric_cols = [c for c in metric_cols if c in df.columns]

    st.subheader("📊 Performance Comparison Table")
    styled = df.style.highlight_max(subset=metric_cols, color='#c8f7c5', axis=0)\
                     .highlight_min(subset=metric_cols, color='#f7c8c8', axis=0)\
                     .format({c: '{:.4f}' for c in metric_cols})
    st.dataframe(styled, use_container_width=True, hide_index=True)

    # Radar chart
    st.divider()
    st.subheader("🕸️ Model Performance Radar Chart")
    categories = metric_cols
    fig = go.Figure()
    colors = ['#1565C0', '#C62828', '#2E7D32', '#6A1B9A']
    for i, (_, row) in enumerate(df.iterrows()):
        vals = [row.get(c, 0) for c in categories]
        vals += vals[:1]
        fig.add_trace(go.Scatterpolar(
            r=vals,
            theta=categories + [categories[0]],
            fill='toself',
            name=row['Model'],
            line_color=colors[i % len(colors)],
            opacity=0.6
        ))
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 1])),
        showlegend=True, height=500,
        title="Model Comparison Radar"
    )
    st.plotly_chart(fig, use_container_width=True)

    # Bar comparison
    st.divider()
    st.subheader("📈 ROC-AUC Comparison")
    if 'ROC AUC' in df.columns:
        fig2 = px.bar(df, x='Model', y='ROC AUC', color='Model',
                      color_discrete_sequence=px.colors.qualitative.Bold,
                      text='ROC AUC', title='ROC-AUC by Model')
        fig2.update_traces(texttemplate='%{text:.3f}', textposition='outside')
        fig2.update_layout(plot_bgcolor='white', height=380, showlegend=False, yaxis_range=[0, 1.1])
        st.plotly_chart(fig2, use_container_width=True)

    # Notes
    st.divider()
    st.subheader("📝 Model Interpretations")
    col1, col2 = st.columns(2)
    with col1:
        st.info("**Lasso (L1 Regression):** Shrinks coefficients of irrelevant drugs to zero. Excellent for feature selection — tells you exactly which drugs are predictive.")
        st.success("**Random Forest:** Handles non-linear drug interactions via ensemble decision trees. Resistant to outliers and noisy reporting patterns in FAERS.")
    with col2:
        st.warning("**XGBoost:** Gradient boosting with regularization. Typically the highest predictive accuracy for tabular data. Handles class imbalance via `scale_pos_weight`.")
        st.error("**Transformer (TabNet/stub):** Self-attention on tabular features. Requires PyTorch + GPU. Best suited for extremely large datasets when you scale to the full FAERS database.")

    for name, m in models.items():
        if "Note" in m:
            st.caption(f"ℹ️ {name}: {m['Note']}")
else:
    st.warning("⚠️ Model metrics not found. Run `python src/analytics/advanced_models.py` first.")
    st.code("python src/analytics/advanced_models.py", language="bash")
