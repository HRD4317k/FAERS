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
    # Deduplicate and keep only Suspect drugs (role_cod = '1')
    con.execute("""
        CREATE OR REPLACE TABLE clean_drug AS
        SELECT DISTINCT
            caseid,
            drugname,
            role_cod
        FROM drug
        WHERE role_cod = '1' AND drugname IS NOT NULL
    """)
    print(f"Cleaned drug data created: {con.execute('SELECT COUNT(*) FROM clean_drug').fetchone()[0]} rows.")
    con.close()

if __name__ == "__main__":
    main()
