import streamlit as st
import pandas as pd
import duckdb
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))
from src.analytics.eda import get_overall_stats, search_drug_stats, DB_PATH

st.set_page_config(page_title="FDA Polypharmacy Intelligence", layout="wide")
st.title("FDA Polypharmacy Intelligence Dashboard")
st.markdown("Advanced Pharmacovigilance Mining of 3-Drug Interactions using Logistic Regression and FDR.")

# 1. Overview
st.header("1. Database Overview")
stats = get_overall_stats()
if "Error" not in stats:
    cols = st.columns(3)
    for i, (key, value) in enumerate(stats.items()):
        cols[i].metric(key, value)
else:
    st.error(f"Could not load database. {stats['Error']}")

st.divider()

# 2. Detected Polypharmacy Signals
st.header("2. Emerging 3-Drug Polypharmacy Signals")
st.markdown("These are the most statistically significant 3-drug interactions that passed all gating criteria (Support, ROR, Hierarchical ROR Comparison, 3-Way Logistic Regression, and FDR).")

try:
    con = duckdb.connect(str(DB_PATH), read_only=True)
    # Check if table exists
    tables = [t[0] for t in con.execute("SHOW TABLES").fetchall()]
    if 'polypharmacy_signals' in tables:
        signals_df = con.execute("SELECT * FROM polypharmacy_signals ORDER BY Emerging_Signal_Score DESC").fetchdf()
        
        if len(signals_df) > 0:
            st.dataframe(signals_df.style.background_gradient(cmap="Reds", subset=['Emerging_Signal_Score', 'Interaction_Strength']), use_container_width=True)
        else:
            st.info("No significant signals passed the strict FDR thresholds.")
    else:
        st.info("Polypharmacy signals table not found. Please run the `polypharmacy_miner.py` script.")
except Exception as e:
    st.error(f"Failed to load polypharmacy signals: {e}")
finally:
    if 'con' in locals():
        con.close()

st.divider()

# 3. Drug Explorer
st.header("3. Drug Explorer")
search_query = st.text_input("Enter a Drug Name to see its most reported Adverse Events (e.g., FENTANYL, MORPHINE):")

if search_query:
    with st.spinner(f"Analyzing {search_query}..."):
        drug_data = search_drug_stats(search_query)
        if not drug_data:
            st.warning(f"No reports found for '{search_query}'.")
        else:
            st.subheader(f"Results for: {search_query.upper()}")
            st.metric("Total Reports involving this drug", f"{drug_data['reports_count']:,}")
            
            st.write("**Top 10 Adverse Events**")
            st.dataframe(
                drug_data['top_adrs'].rename(columns={"reaction": "Adverse Event", "report_count": "Reports"}),
                use_container_width=True,
                hide_index=True
            )

st.divider()
st.markdown("""<small><b>Disclaimer:</b> Statistical associations identified in FAERS reports do not establish causality.</small>""", unsafe_allow_html=True)
