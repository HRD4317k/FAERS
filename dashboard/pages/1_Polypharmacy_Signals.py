import streamlit as st
import duckdb
import pandas as pd
import plotly.express as px
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent))
from src.analytics.eda import DB_PATH

st.set_page_config(page_title="Polypharmacy Signals", layout="wide", page_icon="🔬")
st.title("🔬 3-Drug Polypharmacy Signals")
st.markdown("Statistically validated drug triplets that survived all **7 gates**: Support → ROR → Hierarchical ROR → 3-Way Logistic Regression → FDR (q < 0.05)")

try:
    con = duckdb.connect(str(DB_PATH), read_only=True)
    tables = [t[0] for t in con.execute("SHOW TABLES").fetchall()]
    
    if 'polypharmacy_signals' in tables:
        df = con.execute("SELECT * FROM polypharmacy_signals ORDER BY Emerging_Signal_Score DESC").fetchdf()
        
        if len(df) > 0:
            # Summary metrics
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Total Signals", len(df))
            col2.metric("Max ROR", f"{df['ROR_ABC'].max():.2f}")
            col3.metric("Min Q-Value", f"{df['Q_Value'].min():.2e}")
            col4.metric("Max Interaction Strength", f"{df['Interaction_Strength'].max():.3f}")
            
            st.divider()
            
            # Table
            st.subheader("📋 Signal Table")
            display_cols = ['Drug 1', 'Drug 2', 'Drug 3', 'Adverse Event', 'a', 'ROR_ABC', 'ROR_ABC_Lower_CI', 'Interaction_Strength', 'Q_Value', 'Emerging_Signal_Score']
            display_cols = [c for c in display_cols if c in df.columns]
            styled = df[display_cols].style\
                .background_gradient(cmap='Reds', subset=['Emerging_Signal_Score'])\
                .background_gradient(cmap='Blues', subset=['ROR_ABC'])\
                .format({'ROR_ABC': '{:.2f}', 'Interaction_Strength': '{:.4f}', 'Q_Value': '{:.2e}', 'Emerging_Signal_Score': '{:.3f}', 'ROR_ABC_Lower_CI': '{:.2f}'})
            st.dataframe(styled, use_container_width=True)
            
            # Bar chart
            st.divider()
            st.subheader("📊 Emerging Signal Score Ranking")
            df['Triplet'] = df['Drug 1'] + ' + ' + df['Drug 2'] + ' + ' + df['Drug 3']
            fig = px.bar(df.head(10), x='Emerging_Signal_Score', y='Triplet', orientation='h',
                         color='Interaction_Strength', color_continuous_scale='Reds',
                         labels={'Emerging_Signal_Score': 'Emerging Signal Score', 'Triplet': 'Drug Triplet'},
                         title='Top 3-Drug Polypharmacy Signals')
            fig.update_layout(height=400, plot_bgcolor='white')
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No signals passed the strict FDR thresholds. Try lowering the minimum support threshold in `polypharmacy_miner.py` and rerunning.")
    else:
        st.warning("⚠️ Run `python src/analytics/polypharmacy_miner.py` to generate signals first.")
        
except Exception as e:
    st.error(f"Error: {e}")
finally:
    if 'con' in locals(): con.close()
