import streamlit as st

st.set_page_config(page_title="Glossary", layout="wide", page_icon="📖")
st.title("📖 Glossary of Medical & Statistical Terminology")

tab1, tab2, tab3 = st.tabs(["🏥 Medical Terms", "📊 Statistical Terms", "💻 Technical Terms"])

with tab1:
    terms = {
        "Adverse Drug Reaction (ADR)": "Any untoward medical occurrence associated with drug use in humans, whether or not considered drug-related.",
        "Adverse Event (AE)": "Any untoward medical occurrence in a patient administered a medicinal product. Broader than ADR — doesn't require causality to be established.",
        "Polypharmacy": "Concurrent use of 5 or more medications by a patient. In this project, we study 3-drug polypharmacy interactions.",
        "Drug-Drug Interaction (DDI)": "A pharmacokinetic or pharmacodynamic change caused by one drug altering the behavior of another when co-administered.",
        "Pharmacovigilance": "WHO-defined science and activities relating to the detection, assessment, understanding, and prevention of drug-related problems.",
        "Spontaneous Reporting System (SRS)": "A passive surveillance system where healthcare professionals and patients voluntarily submit reports of suspected ADRs.",
        "FAERS": "FDA Adverse Event Reporting System — the primary spontaneous reporting database in the United States.",
        "MedDRA": "Medical Dictionary for Regulatory Activities — the international medical terminology used to classify adverse events in FAERS.",
        "Concomitant Drug": "A drug given at the same time as, or shortly after, another drug being investigated.",
        "Primary Suspect Drug": "The drug determined by the reporter to be the most likely cause of the adverse event (role code = 1 in FAERS).",
    }
    for term, definition in terms.items():
        with st.expander(f"**{term}**"):
            st.write(definition)

with tab2:
    stats_terms = {
        "Reporting Odds Ratio (ROR)": "The odds of a specific AE occurring with a drug combination, divided by the odds of that AE with all other drugs. ROR > 1 indicates disproportional reporting.",
        "Proportional Reporting Ratio (PRR)": "The proportion of AE reports for a drug divided by the same proportion for all other drugs. PRR > 2 with Chi² ≥ 4 is a standard signal threshold.",
        "Chi-Square (χ²)": "A statistical test measuring the deviation of observed vs expected frequencies. Threshold: χ² ≥ 4 (Evans criteria for signal detection).",
        "95% Confidence Interval (CI)": "Range within which the true parameter lies with 95% probability. If the lower CI > 1 for ROR, the signal is statistically significant.",
        "False Discovery Rate (FDR)": "The expected proportion of false positives among all significant results. Controlled using Benjamini-Hochberg correction.",
        "Q-Value": "FDR-adjusted p-value. A q < 0.05 means at most 5% of detected signals are expected to be false positives.",
        "Interaction Strength": "A novel metric in this project: log(ROR_ABC) − max[log(ROR_A), log(ROR_B), log(ROR_AB), ...]. Positive value implies the triplet adds unique risk beyond all subsets.",
        "Emerging Signal Score": "A composite ranking metric = Interaction_Strength × ROR_Lower_CI. Higher scores indicate stronger, more reliable signals.",
        "Disproportionality Analysis": "Statistical method to detect if an AE is reported more frequently with a drug than expected from the background rate.",
        "Beta_ABC": "The 3-way interaction coefficient in the Logistic Regression model. Represents the unique effect of the drug triplet beyond individual and pairwise effects.",
    }
    for term, definition in stats_terms.items():
        with st.expander(f"**{term}**"):
            st.write(definition)

with tab3:
    tech_terms = {
        "FP-Growth Algorithm": "A frequent pattern mining algorithm that uses a compressed FP-Tree structure. More efficient than Apriori — avoids candidate generation entirely.",
        "Apriori Algorithm": "Association rule mining algorithm using a level-wise, breadth-first search. Baseline comparison for FP-Growth in this project.",
        "DuckDB": "An in-process analytical SQL database engine optimized for columnar read-heavy workloads. Used here to store and query millions of FAERS records.",
        "XGBoost": "Extreme Gradient Boosting — an ensemble ML method that trains decision trees sequentially, each correcting errors of the previous.",
        "Random Forest": "Ensemble of decision trees trained on random data subsets. Reduces overfitting and handles high-dimensional sparse drug matrices well.",
        "LASSO (L1 Regression)": "Logistic regression with L1 penalty. Shrinks irrelevant drug coefficients to exactly zero — effective feature selector for sparse FAERS data.",
        "Logistic Regression": "A statistical classification model. Used here with all pairwise and 3-way interaction terms to isolate the β_ABC interaction coefficient.",
        "Transformer (TabNet)": "A deep learning architecture applying self-attention to tabular data. Selectively focuses on the most relevant drug features per patient report.",
        "OpenFDA API": "The public REST API by the FDA providing structured access to FAERS, drug labels, and other regulatory databases in JSON format.",
        "One-Hot Encoding": "Converting categorical drug names into binary matrix columns (1 = drug present, 0 = absent) for use in ML models.",
    }
    for term, definition in tech_terms.items():
        with st.expander(f"**{term}**"):
            st.write(definition)
