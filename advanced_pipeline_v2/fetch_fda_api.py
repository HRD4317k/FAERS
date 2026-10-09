# fetch_fda_api.py
import requests
import pandas as pd
import time
import os
import argparse
from pathlib import Path

def fetch_data(api_key, limit_per_request=100, max_records=2000):
    base_url = "https://api.fda.gov/drug/event.json"
    records = []
    skip = 0
    
    print(f"Starting data fetch. Target: {max_records} records.")
    
    while len(records) < max_records:
        params = {
            "search": "receivedate:[20230101 TO 20231231]",
            "limit": limit_per_request,
            "skip": skip
        }
        if api_key:
            params["api_key"] = api_key
            
        try:
            response = requests.get(base_url, params=params)
            if response.status_code == 429:
                print("Rate limited. Waiting 10 seconds...")
                time.sleep(10)
                continue
            
            response.raise_for_status()
            data = response.json()
            
            results = data.get("results", [])
            if not results:
                break
                
            for item in results:
                patient = item.get("patient", {})
                drugs = patient.get("drug", [])
                reactions = patient.get("reaction", [])
                
                # Extract drug names
                drug_names = []
                for d in drugs:
                    name = d.get("medicinalproduct")
                    if name:
                        drug_names.append(name.upper())
                
                # Extract reactions
                reaction_names = []
                for r in reactions:
                    term = r.get("reactionmeddrapt")
                    if term:
                        reaction_names.append(term.upper())
                
                if len(drug_names) >= 3 and len(reaction_names) > 0:
                    records.append({
                        "report_id": item.get("safetyreportid"),
                        "date": item.get("receiptdate"),
                        "patient_sex": patient.get("patientsex", "UNKNOWN"),
                        "patient_age": patient.get("patientonsetage", "UNKNOWN"),
                        "drugs": sorted(list(set(drug_names))),
                        "reactions": list(set(reaction_names))
                    })
            
            skip += limit_per_request
            print(f"Fetched {skip} raw records... Extracted {len(records)} viable polypharmacy records.")
            time.sleep(0.5) # Gentle on the API
            
            if skip >= 24000:
                print("Reached maximum skip allowed by OpenFDA without downloading bulk files.")
                break
                
        except Exception as e:
            print(f"Error fetching data: {e}")
            break
            
    df = pd.DataFrame(records)
    
    if df.empty:
        print("Failed to fetch any actual data.")
        return
        
    # Explode reactions so each row is a report-reaction pair
    df = df.explode("reactions").rename(columns={"reactions": "reaction"})
    
    output_dir = Path("data")
    output_dir.mkdir(exist_ok=True)
    df.to_parquet(output_dir / "structured_fda_data.parquet", index=False)
    print(f"Saved {len(df)} structured records to data/structured_fda_data.parquet")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--api-key", help="OpenFDA API Key", default=os.environ.get("OPENFDA_API_KEY"))
    parser.add_argument("--max-records", type=int, default=20000, help="Maximum number of valid polypharmacy records to extract")
    args = parser.parse_args()
    
    if not args.api_key:
        print("WARNING: No API key provided. OpenFDA rate limits will apply (1000/day).")
    
    fetch_data(args.api_key, max_records=args.max_records)
