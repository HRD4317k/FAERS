import duckdb
from pathlib import Path
import os

DB_PATH = Path("../../data/processed/faers.db")

def main():
    os.chdir(Path(__file__).parent)
    con = duckdb.connect(str(DB_PATH))
    
    tables = con.execute("SHOW TABLES").fetchall()
    table_names = [t[0] for t in tables]
    
    if 'reac' not in table_names:
        print("Reaction table not found.")
        return
        
    print("Cleaning reaction data...")
    # Deduplicate reactions for the same caseid
    con.execute("""
        CREATE OR REPLACE TABLE clean_reac AS
        SELECT DISTINCT
            caseid,
            reaction
        FROM reac
        WHERE reaction IS NOT NULL
    """)
    print(f"Cleaned reaction data created: {con.execute('SELECT COUNT(*) FROM clean_reac').fetchone()[0]} rows.")
    con.close()

if __name__ == "__main__":
    main()
