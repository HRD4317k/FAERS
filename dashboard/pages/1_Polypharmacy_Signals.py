import streamlit as st
import duckdb
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent))
from src.analytics.eda import DB_PATH

st.set_page_config(page_title="Polypharmacy Signals", layout="wide")
st.title("Emerging 3-Drug Polypharmacy Signals")
st.markdown("These are the most statistically significant 3-drug interactions that passed all gating criteria (Support, ROR, Hierarchical ROR Comparison, 3-Way Logistic Regression, and FDR).")

try:
    con = duckdb.connect(str(DB_PATH), read_only=True)
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
