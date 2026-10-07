import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import sys
from pathlib import Path
import pandas as pd

sys.path.append(str(Path(__file__).parent.parent.parent))
from src.analytics.eda import search_drug_stats
from src.analytics.signal_detection import get_drug_ae_signals, get_temporal_trends

st.set_page_config(page_title="Drug Explorer", layout="wide", page_icon="🔍")
st.title("🔍 Drug Explorer & Signal Analysis")

search_query = st.text_input("🔎 Search Drug (e.g., FENTANYL, MORPHINE, ASPIRIN):", placeholder="Type a drug name...")

if search_query:
    with st.spinner(f"Analyzing FAERS data for {search_query.upper()}..."):
        drug_data = search_drug_stats(search_query)
        signals_df = get_drug_ae_signals(search_query, top_n=20)
        temporal_df = get_temporal_trends(search_query)
        
    if not drug_data:
        st.warning(f"No reports found for '{search_query}'. Try the generic drug name.")
    else:
        st.subheader(f"Results for: **{search_query.upper()}**")
        st.metric("Total Reports", f"{drug_data['reports_count']:,}")
        
        tab1, tab2, tab3 = st.tabs(["📋 Top Adverse Events", "📊 ROR / PRR Signals", "📈 Temporal Trend"])
        
        with tab1:
            if not drug_data['top_adrs'].empty:
                adr_df = drug_data['top_adrs'].rename(columns={'reaction': 'Adverse Event', 'report_count': 'Reports'})
                fig = px.bar(adr_df.head(15), x='Reports', y='Adverse Event', orientation='h',
                             color='Reports', color_continuous_scale='Blues',
                             title=f'Top Adverse Events for {search_query.upper()}')
                fig.update_layout(plot_bgcolor='white', height=450)
                st.plotly_chart(fig, use_container_width=True)
                st.dataframe(adr_df, use_container_width=True, hide_index=True)
        
        with tab2:
            if not signals_df.empty:
                st.markdown("**Signal Classification:** HIGH = PRR_lower > 2 & Chi² ≥ 4 | MODERATE = ROR > 1 | LOW")
                color_map = {'HIGH': 'red', 'MODERATE': 'orange', 'LOW': 'green'}
                
                fig2 = px.scatter(signals_df, x='ROR', y='Chi2', size='Reports',
                                  color='Signal', color_discrete_map=color_map,
                                  hover_name='Adverse Event', hover_data=['PRR'],
                                  title='ROR vs Chi-Square Signal Map',
                                  labels={'Chi2': 'Chi-Square Statistic', 'ROR': 'Reporting Odds Ratio'})
                fig2.add_hline(y=4, line_dash='dash', line_color='gray', annotation_text='Chi² = 4 threshold')
                fig2.add_vline(x=2, line_dash='dash', line_color='gray', annotation_text='ROR = 2')
                fig2.update_layout(plot_bgcolor='white', height=430)
                st.plotly_chart(fig2, use_container_width=True)
                
                def highlight_signal(row):
                    if row['Signal'] == 'HIGH': return ['background-color: #ffcccc'] * len(row)
                    elif row['Signal'] == 'MODERATE': return ['background-color: #fff3cc'] * len(row)
                    return [''] * len(row)
                
                st.dataframe(signals_df.style.apply(highlight_signal, axis=1), use_container_width=True, hide_index=True)
            else:
                st.info("Not enough data to compute ROR/PRR signals for this drug.")
        
        with tab3:
            if not temporal_df.empty:
                fig3 = px.line(temporal_df, x='year', y='reports', markers=True,
                               title=f'Yearly Report Trend for {search_query.upper()}',
                               labels={'year': 'Year', 'reports': 'Number of Reports'})
                fig3.update_traces(line_color='#1565C0', line_width=3)
                fig3.update_layout(plot_bgcolor='white', height=350)
                st.plotly_chart(fig3, use_container_width=True)
            else:
                st.info("No temporal data available for this drug.")
else:
    st.info("👆 Enter a drug name above to explore adverse event signals and trends.")
