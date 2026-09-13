import duckdb
import pandas as pd
from rapidfuzz import process, fuzz
import requests
from pathlib import Path

DB_PATH = Path("../../data/processed/faers.db")
OUTPUT_DB_PATH = Path("../../data/processed/faers_cleaned.db")

def fetch_openfda_generics():
    """Fetches a list of generic drug names from openFDA label API to use as canonical names."""
    print("Fetching drug names from openFDA...")
    url = 'https://api.fda.gov/drug/label.json?search=_exists_:openfda.generic_name&limit=1000'
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        results = data.get('results', [])
        generic_names = set()
        for res in results:
            if 'openfda' in res and 'generic_name' in res['openfda']:
                for name in res['openfda']['generic_name']:
                    generic_names.add(name.upper())
        print(f"Fetched {len(generic_names)} generic names from openFDA.")
        return list(generic_names)
    else:
        print("Failed to fetch openFDA data. Using local hardcoded list for demonstration.")
        # Fallback list of common generic names for demonstration
        return ['METFORMIN', 'WARFARIN', 'ASPIRIN', 'GLIMEPIRIDE', 'INSULIN']

def normalize_names(df, canonical_names):
    print("Normalizing drug names...")
    
    def match_name(name):
        if pd.isna(name):
            return name
        
        name = str(name).upper().strip()
        
        # Exact match
        if name in canonical_names:
            return name
            
        # Try finding partial matches like METFORMIN HCL -> METFORMIN
        for c_name in canonical_names:
            if name.startswith(c_name) or c_name in name:
                return c_name
                
        # Fuzzy match
        match = process.extractOne(name, canonical_names, scorer=fuzz.token_sort_ratio, score_cutoff=85)
        if match:
            return match[0]
            
        return name
        
    df['normalized_name'] = df['drugname'].apply(match_name)
    return df

def main():
    import os
    os.chdir(Path(__file__).parent)
    
    con = duckdb.connect(str(DB_PATH))
    
    # Check if tables exist
    tables = con.execute("SHOW TABLES").fetchall()
    table_names = [t[0] for t in tables]
    
    if 'drug' not in table_names:
        print("Drug table not found. Please run faers_loader.py first.")
        con.close()
        return

    canonical_names = fetch_openfda_generics()
    
    print("Extracting unique drug names from database...")
    # Get unique raw drug names to minimize fuzzy matching calls
    unique_drugs = con.execute("SELECT DISTINCT drugname FROM drug WHERE drugname IS NOT NULL LIMIT 10000").fetchdf()
    
    if unique_drugs.empty:
        print("No drug names found in database.")
        con.close()
        return
        
    normalized_drugs = normalize_names(unique_drugs, canonical_names)
    
    print("Updating database with normalized names...")
    # Save the mapping as a new table
    con.execute("CREATE OR REPLACE TABLE drug_master AS SELECT drugname as raw_name, normalized_name FROM normalized_drugs")
    
    print("Done normalizing drug names.")
    con.close()

if __name__ == "__main__":
    main()
