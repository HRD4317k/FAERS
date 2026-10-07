import streamlit as st
import plotly.express as px
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent))
from src.analytics.signal_detection import get_ae_heatmap_data, get_top_drug_pairs

st.set_page_config(page_title="Signal Heatmap", layout="wide", page_icon="🌡️")
st.title("🌡️ Drug × Adverse Event Heatmap")
st.markdown("Co-occurrence frequency matrix of top drugs vs top adverse events. Darker cells indicate stronger co-reporting.")

try:
    with st.spinner("Building heatmap..."):
        pivot = get_ae_heatmap_data(top_drugs=15, top_aes=15)
    
    if not pivot.empty:
        fig = px.imshow(pivot, 
                        color_continuous_scale='Blues',
                        title='Drug × Adverse Event Co-occurrence Heatmap',
                        labels={'x': 'Adverse Event', 'y': 'Drug', 'color': 'Reports'},
                        aspect='auto')
        fig.update_layout(height=600, xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)
    
    st.divider()
    st.subheader("🔗 Top Drug Co-occurrence Pairs")
    pairs_df = get_top_drug_pairs(top_n=20)
    if not pairs_df.empty:
        fig2 = px.bar(pairs_df.head(15), x='co_reports', y='drug1', 
                      text='drug2', orientation='h',
                      color='co_reports', color_continuous_scale='Purples',
                      title='Most Frequently Co-Reported Drug Pairs',
                      labels={'co_reports': 'Co-Reports', 'drug1': 'Drug 1'})
        fig2.update_layout(plot_bgcolor='white', height=450)
        st.plotly_chart(fig2, use_container_width=True)
except Exception as e:
    st.error(f"Error generating heatmap: {e}")
