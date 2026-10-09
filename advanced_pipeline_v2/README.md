# Advanced FDA Polypharmacy Pipeline

This directory contains a new pipeline designed to process large amounts of data directly from the OpenFDA API using API keys, while strictly filtering out non-pharmacological or purely behavioral reactions (e.g., Overdose, Dependence, Intentional Misuse) that don't yield significant biological learnings.

## Setup

1. Install requirements:
   ```bash
   pip install -r requirements.txt
   ```

2. (Optional but Recommended) Get an OpenFDA API key at [open.fda.gov](https://open.fda.gov/apis/authentication/).

## Pipeline Execution

1. **Fetch and Structure Data**
   Run the fetching script. It connects to the OpenFDA API, extracts massive nested JSON responses, and structures them into a clean Parquet dataset.
   ```bash
   python fetch_fda_api.py --api-key YOUR_API_KEY_HERE --max-records 50000
   ```

2. **Clean Data and Mine Signals**
   Run the processing script. It automatically filters out uninformative reactions ("OVERDOSE", "DRUG DEPENDENCE", etc.) and uses FP-Growth and Reporting Odds Ratio (ROR) analysis to identify significant 3-drug synergistic risks.
   ```bash
   python process_and_mine.py
   ```

3. **Visualize Meaningful Results**
   Launch the streamlined dashboard to view the high-quality interactions.
   ```bash
   streamlit run dashboard.py
   ```
