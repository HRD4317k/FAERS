import duckdb
from pathlib import Path
import os

DB_PATH = Path("../../data/processed/faers.db")

def main():
    os.chdir(Path(__file__).parent)
    con = duckdb.connect(str(DB_PATH))
    
    tables = con.execute("SHOW TABLES").fetchall()
    table_names = [t[0] for t in tables]
    
    if 'drug' not in table_names:
        print("Drug table not found.")
        return
        
    print("Cleaning drug data...")
    # Example cleaning: deduplicate based on caseid and drug_seq, keep only Primary Suspect (PS) or Secondary Suspect (SS)
    con.execute("""
        CREATE OR REPLACE TABLE clean_drug AS
        SELECT DISTINCT
            caseid,
            drug_seq,
            drugname,
            role_cod,
            route
        FROM drug
        WHERE role_cod IN ('PS', 'SS')
    """)
    print(f"Cleaned drug data created: {con.execute('SELECT COUNT(*) FROM clean_drug').fetchone()[0]} rows.")
    con.close()

if __name__ == "__main__":
    main()
