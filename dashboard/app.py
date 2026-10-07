import streamlit as st
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))
from src.analytics.eda import get_overall_stats

st.set_page_config(
    page_title="PharmaSense | FDA Polypharmacy Intelligence",
    layout="wide",
    page_icon="💊"
)

# Custom CSS
st.markdown("""
<style>
[data-testid="stMetricValue"] { font-size: 2rem; font-weight: 700; color: #1565C0; }
[data-testid="stMetricLabel"] { font-size: 0.9rem; color: #555; }
.block-container { padding-top: 2rem; }
.stDataFrame { border-radius: 10px; }
div[data-testid="metric-container"] {
    background: linear-gradient(135deg, #E3F2FD, #BBDEFB);
    border-radius: 12px;
    padding: 1rem 1.5rem;
    border-left: 5px solid #1565C0;
}
</style>
""", unsafe_allow_html=True)

st.title("💊 PharmaSense — FDA Polypharmacy Intelligence")
st.markdown("*Advanced Multi-Gate 3-Drug Interaction Mining from OpenFDA Adverse Event Reports*")
st.divider()

col1, col2 = st.columns([2, 1])
with col1:
    st.markdown("""
    ### Welcome to PharmaSense
    This platform implements a rigorous **Multi-Gate Polypharmacy Signal Detection** framework:
    - 🔬 **FP-Growth** for efficient 3-drug pattern mining
    - 📊 **Hierarchical ROR/PRR** disproportionality analysis  
    - 🧮 **3-Way Logistic Regression** with FDR correction
    - 🤖 **XGBoost, Random Forest, LASSO** predictive models
    - 📈 **Temporal trend** and signal persistence tracking
    
    Navigate using the **sidebar** to explore each analytical layer.
    """)

with col2:
    st.markdown("### 📊 Database Stats")
    with st.spinner("Loading..."):
        stats = get_overall_stats()
        if "Error" not in stats:
            for key, val in stats.items():
                st.metric(key, val)
        else:
            st.error(stats["Error"])

st.divider()
st.markdown("""
<small><b>Disclaimer:</b> Statistical associations in FAERS reports do not establish causality. 
This tool is for research and educational purposes only.</small>
""", unsafe_allow_html=True)
