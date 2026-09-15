# FDA Drug Adverse Event Pattern Miner (BTP Polypharmacy Extension)

A pharmacovigilance analytics platform that ingests OpenFDA JSON adverse event reports and surfaces drug-adverse event associations, **3-drug polypharmacy risk patterns**, statistical safety signals, and temporal trends — with FDA label context — through a searchable dashboard.

## Overview

This project analyzes the OpenFDA JSON database to find meaningful polypharmacy patterns (specifically 3-drug combinations). It extends existing methodologies (like Ibrahim et al.) by utilizing a rigorous multi-gate framework involving FP-Growth, Reporting Odds Ratio (ROR), Hierarchical comparisons, 3-way Logistic Regression, and FDR correction. 

## Project Roadmap

### Phase 1: Foundation (Weeks 1-4)
- **Data Ingestion**: Automate downloading of the massive OpenFDA JSON dataset (`src/ingestion/download_faers.py`), strictly scoped to 2023.
- **JSON Parsing**: Efficiently stream and parse nested JSON directly into a DuckDB relational architecture (`src/ingestion/faers_loader.py`).
- **Cleaning**: Deduplicate records and isolate true Primary/Secondary suspect drugs.

### Phase 2: Advanced Polypharmacy Mining (Weeks 5-8)
We define a statistically meaningful 3-drug polypharmacy signal via a **Multi-Gate Methodology**:
1. **Gate 1 & 2 (Exposure & Event Support)**: Use `FP-Growth` to identify frequent 3-drug patterns (e.g., Support ≥ 20).
2. **Gate 3 (Disproportionality)**: Calculate $ROR_{ABC}$ and 95% Confidence Intervals. Require $ROR_{lower 95\%} > 1$.
3. **Gate 4 (Higher-Order Effect)**: Compare $ROR_{ABC}$ against lower-order individual ($ROR_A, ROR_B, ROR_C$) and pairwise ($ROR_{AB}, ROR_{AC}, ROR_{BC}$) effects to ensure the triple adds unique risk.
4. **Gate 5 (Three-Way Regression)**: Fit a 3-way Logistic Regression model (`logit(P(AE)) = β0 + βA*A + βB*B + βC*C + βAB*AB + βAC*AC + βBC*BC + βABC*ABC`). Require the 3-way interaction coefficient $β_{ABC}$ to be statistically significant after **Benjamini–Hochberg FDR correction** ($q < 0.05$).
- **Script**: `src/analytics/polypharmacy_miner.py`

### Phase 3: Temporal Analysis & FDA Label Context (Weeks 9-10)
- Calculate temporal persistence (QoQ growth).
- Derive the **Emerging Signal Score**.
- Integrate openFDA Label API for contextualization.

### Phase 4: Product & Deployment (Weeks 11-13)
- Build an interactive Streamlit application.
- Deploy to Render/Streamlit Cloud.

## Getting Started

1. Create a virtual environment and install requirements:
   ```bash
   pip install -r requirements.txt
   ```
2. Download 2023 FAERS JSON data:
   ```bash
   python src/ingestion/download_faers.py
   ```
3. Run the ingestion pipeline to build the analytical DuckDB database:
   ```bash
   python src/ingestion/faers_loader.py
   ```
4. Run the Polypharmacy Mining framework:
   ```bash
   python src/analytics/polypharmacy_miner.py
   ```

## Disclaimer
This system analyzes spontaneous adverse-event reports for research and educational purposes. Statistical associations identified in FAERS reports do not establish causality. Findings should not be used as a substitute for clinical judgment, regulatory assessment, or medical advice.
