import streamlit as st
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))
from src.analytics.eda import get_overall_stats

st.set_page_config(page_title="FDA Polypharmacy Intelligence", layout="wide")

st.title("FDA Polypharmacy Intelligence Dashboard")
st.markdown("Advanced Pharmacovigilance Mining using ML & Disproportionality Analysis.")

st.header("Database Overview")
stats = get_overall_stats()
if "Error" not in stats:
    cols = st.columns(3)
    for i, (key, value) in enumerate(stats.items()):
        cols[i].metric(key, value)
else:
    st.error(f"Could not load database. {stats['Error']}")

st.divider()

st.markdown("""
### Welcome to the Dashboard!
Please navigate using the sidebar to explore:
- **Polypharmacy Signals**: View statistically validated 3-drug adverse event signals.
- **Drug Explorer**: Search for specific drugs and see their top adverse events.
- **Advanced Models**: View predictive metrics from XGBoost, Random Forest, and Lasso Regression.
- **Glossary**: Learn about the medical and statistical terminologies used in this platform.

<small><b>Disclaimer:</b> Statistical associations identified in FAERS reports do not establish causality.</small>
""", unsafe_allow_html=True)
