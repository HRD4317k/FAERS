import streamlit as st
import json
import pandas as pd
from pathlib import Path

METRICS_PATH = Path(__file__).parent.parent.parent / "data" / "processed" / "model_metrics.json"

st.set_page_config(page_title="Advanced Models", layout="wide")
st.title("Advanced Predictive Models")
st.markdown("Comparing the performance of various machine learning algorithms in predicting Adverse Events (e.g., Overdose) based on drug exposure profiles.")

if METRICS_PATH.exists():
    with open(METRICS_PATH, "r") as f:
        data = json.load(f)
        
    st.subheader(f"Target Prediction: {data.get('Target', 'Unknown')}")
    
    models = data.get("Models", {})
    
    # Convert to DataFrame
    df_data = []
    for model_name, metrics in models.items():
        row = {"Model": model_name}
        row.update({k: v for k, v in metrics.items() if k != "Note"})
        df_data.append(row)
        
    df = pd.DataFrame(df_data)
    
    st.dataframe(df.style.highlight_max(subset=['Accuracy', 'Precision', 'Recall', 'F1 Score', 'ROC AUC'], color='lightgreen', axis=0), use_container_width=True)
    
    # Display notes if any
    for model_name, metrics in models.items():
        if "Note" in metrics:
            st.info(f"**{model_name} Note:** {metrics['Note']}")
            
    st.divider()
    st.markdown("### Model Interpretations")
    st.markdown("""
    - **Lasso Regression (L1):** Excellent for feature selection in high-dimensional sparse data. It shrinks less important drug coefficients to exactly zero, leaving only the most predictive drugs.
    - **Random Forest:** Handles non-linear interactions well and is highly robust to outliers in the reporting data.
    - **XGBoost:** A powerful gradient boosting framework that typically yields the highest predictive accuracy by minimizing a regularized objective function.
    - **Transformer (Tabular):** Modern deep learning architectures (like TabNet) apply self-attention mechanisms to tabular data, allowing the model to focus on the most relevant features (drugs) for each specific patient report.
    """)
else:
    st.warning("Model metrics not found. Please run `python src/analytics/advanced_models.py` to train the models and generate results.")
