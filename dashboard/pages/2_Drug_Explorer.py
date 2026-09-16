import streamlit as st
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent))
from src.analytics.eda import search_drug_stats

st.set_page_config(page_title="Drug Explorer", layout="wide")
st.title("Drug Explorer")

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
