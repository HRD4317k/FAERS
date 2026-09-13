# FDA Drug Adverse Event Pattern Miner

A pharmacovigilance analytics platform that ingests 20M+ FDA adverse event reports and surfaces drug-adverse event associations, polypharmacy risk patterns, statistical safety signals, and temporal trends — with FDA label context — through a searchable dashboard.

## Overview

This project analyzes the FDA Adverse Event Reporting System (FAERS) database to find patterns between drugs and adverse events. It uses descriptive analytics, association rule mining, and signal detection (ROR) to prioritize statistically notable patterns, which are then compared with the openFDA Drug Labeling API.

## Project Roadmap

### Phase 1: Foundation (Weeks 1-4)
- Set up repository structure.
- Download FAERS 2023–2024 data (8 quarters).
- Develop data ingestion pipeline (`src/ingestion/faers_loader.py`) to load raw ASCII/CSV into a DuckDB database.
- Develop drug name normalization (`src/preprocessing/normalize_drugs.py`) using `rapidfuzz` against openFDA generic names.
- Clean and deduplicate data (`src/preprocessing/clean_drugs.py`, `src/preprocessing/clean_reactions.py`).
- Create EDA scripts for basic statistics.
- Build initial Streamlit Drug Explorer page.

### Phase 2: Association Rule Mining (Weeks 5-6)
- Transform reports into transactions (Drug→ADR, DrugPair→ADR, DrugTriple→ADR).
- Run Apriori algorithm (`mlxtend`) to find frequent itemsets and association rules.
- Filter results based on minimum support, confidence, and lift.
- Store results in a `rules` table.
- Build the Combination Explorer page in Streamlit.

### Phase 3: ROR & Signal Detection (Weeks 7-8)
- Calculate Reporting Odds Ratio (ROR) and 95% Confidence Intervals for drug-ADR pairs.
- Flag statistical safety signals (HIGH/MEDIUM).
- Develop Emerging Signal Score.
- Build Emerging Signals page.

### Phase 4: Temporal Analysis & FDA Label Context (Weeks 9-10)
- Calculate quarter-over-quarter growth rates for identified signals.
- Integrate openFDA Label API.
- Compare FAERS observed signals with documented FDA label warnings and adverse reactions.
- Complete the Signal vs. Label comparison view in the dashboard.
- Optional: Clustering and classification.

### Phase 5: Deployment (Weeks 11-13)
- Deploy application (Streamlit Cloud or Render).
- Finalize documentation, video demo, and README.

## Getting Started

1. Create a virtual environment and install requirements:
   ```bash
   pip install -r requirements.txt
   ```
2. Download FAERS Quarterly data and extract to `data/raw/faers/`.
3. Run the ingestion pipeline to build the analytical database.

## Disclaimer
This system analyzes spontaneous adverse-event reports for research and educational purposes. Statistical associations identified in FAERS reports do not establish causality. Findings should not be used as a substitute for clinical judgment, regulatory assessment, or medical advice.
