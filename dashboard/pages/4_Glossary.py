import streamlit as st

st.set_page_config(page_title="Glossary", layout="wide")
st.title("Glossary of Medical & Statistical Terminology")

st.markdown("""
### Medical Terminologies
*   **Adverse Event (AE) / Adverse Drug Reaction (ADR):** Any untoward medical occurrence associated with the use of a drug in humans, whether or not considered drug-related.
*   **Polypharmacy:** The concurrent use of multiple medications by a patient. In this project, we specifically focus on 3-drug polypharmacy interactions.
*   **Concomitant Drug:** A drug given at the same time as, or shortly after, another drug.
*   **Primary/Secondary Suspect Drug:** The drug(s) determined by the reporter to be the most likely cause of the adverse event.

### Statistical & Methodological Terminologies
*   **Disproportionality Analysis:** A method used in pharmacovigilance to determine if an adverse event is reported more frequently with a specific drug (or combination) than with all other drugs in the database.
*   **Reporting Odds Ratio (ROR):** The odds of a specific event occurring with a specific drug combination, compared to the odds of that event occurring with all other combinations.
*   **Proportional Reporting Ratio (PRR):** A measure of disproportionality similar to Relative Risk.
*   **Interaction Strength:** A novel metric defined for this project. It is the difference between the log(ROR) of the 3-drug combination and the maximum log(ROR) of any subset (individual drug or pair). A value > 0 implies the 3-drug combination has unique risk beyond lower-order combinations.
*   **Logistic Regression:** A statistical model used here to estimate the true independent effect ($\beta$) of a drug or interaction on the probability of an adverse event, while controlling for confounding covariates.
*   **Benjamini-Hochberg FDR (False Discovery Rate):** A statistical method to correct P-values when conducting multiple tests, ensuring that we limit false positive signals across thousands of drug combinations.
*   **FP-Growth Algorithm:** A highly efficient data mining algorithm used to discover frequent itemsets (combinations of drugs) in large transaction databases without generating candidate itemsets explicitly.
""")
