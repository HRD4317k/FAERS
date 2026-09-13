import streamlit as st
import pandas as pd
import sys
from pathlib import Path

# Add src to path so we can import from src.analytics
sys.path.append(str(Path(__file__).parent.parent))
from src.analytics.eda import get_overall_stats, search_drug_stats

st.set_page_config(page_title="FDA Drug Safety Intelligence", layout="wide")

st.title("FDA Drug Safety Intelligence 💊")
st.markdown("A Pharmacovigilance Analytics Platform for Adverse Event Pattern Mining.")

# Dashboard Overview
st.header("Overview")
with st.spinner("Loading overall statistics..."):
    stats = get_overall_stats()
    
    if "Error" not in stats:
        cols = st.columns(4)
        for i, (key, value) in enumerate(stats.items()):
            cols[i].metric(key, value)
    else:
        st.error(f"Could not load database. Have you run the ingestion pipeline? Error: {stats['Error']}")

st.divider()

# Drug Explorer
st.header("Drug Explorer")
st.markdown("Search for a specific drug (e.g., METFORMIN, WARFARIN, ASPIRIN) to see associated adverse events.")

search_query = st.text_input("Enter Drug Name:")

if search_query:
    with st.spinner(f"Analyzing FAERS reports for {search_query}..."):
        drug_data = search_drug_stats(search_query)
        
        if not drug_data:
            st.warning(f"No reports found for '{search_query}'. Try a generic name.")
        else:
            st.subheader(f"Results for: {search_query.upper()}")
            st.metric("Total Reports", f"{drug_data['reports_count']:,}")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Top 10 Adverse Events**")
                st.dataframe(
                    drug_data['top_adrs'].rename(columns={"reaction": "Adverse Event", "report_count": "Reports"}),
                    use_container_width=True,
                    hide_index=True
                )
            
            with col2:
                st.write("**Outcomes Breakdown**")
                # Outcome codes in FAERS: DE=Death, HO=Hospitalization, LT=Life-Threatening, DS=Disability, etc.
                outcome_mapping = {
                    "DE": "Death", "HO": "Hospitalization - Initial or Prolonged", 
                    "LT": "Life-Threatening", "DS": "Disability", 
                    "CA": "Congenital Anomaly", "RI": "Required Intervention",
                    "OT": "Other Serious (Important Medical Event)"
                }
                
                outcomes_df = drug_data['outcomes'].copy()
                outcomes_df['Outcome'] = outcomes_df['outc_cod'].map(lambda x: outcome_mapping.get(x, str(x)))
                st.dataframe(
                    outcomes_df[['Outcome', 'outcome_count']].rename(columns={'outcome_count': 'Count'}).sort_values(by='Count', ascending=False),
                    use_container_width=True,
                    hide_index=True
                )

st.divider()
st.markdown("""
<small>
<b>Disclaimer:</b> This application analyzes spontaneous adverse-event reports for research and exploratory pharmacovigilance. 
Statistical associations do not establish causality and should not be used as a substitute for clinical judgment or regulatory assessment.
</small>
""", unsafe_allow_html=True)
