import os
import json
import zipfile
import duckdb
from pathlib import Path
import glob

DATA_DIR = Path("../../data/raw/faers")
DB_PATH = Path("../../data/processed/faers.db")

def init_db():
    print(f"Connecting to database at {DB_PATH}")
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect(str(DB_PATH))
    
    con.execute("""
        CREATE TABLE IF NOT EXISTS demo (
            caseid VARCHAR,
            receive_date VARCHAR,
            sex VARCHAR,
            age VARCHAR
        )
    """)
    
    con.execute("""
        CREATE TABLE IF NOT EXISTS drug (
            caseid VARCHAR,
            role_cod VARCHAR,
            drugname VARCHAR
        )
    """)
    
    con.execute("""
        CREATE TABLE IF NOT EXISTS reac (
            caseid VARCHAR,
            reaction VARCHAR
        )
    """)
    
    return con

def process_file(zip_path, con):
    demo_batch = []
    drug_batch = []
    reac_batch = []
    
    try:
        with zipfile.ZipFile(zip_path, 'r') as z:
            for filename in z.namelist():
                if not filename.endswith('.json'):
                    continue
                
                with z.open(filename) as f:
                    data = json.load(f)
                    results = data.get('results', [])
                    
                    for r in results:
                        caseid = r.get('safetyreportid')
                        if not caseid:
                            continue
                            
                        patient = r.get('patient', {})
                        
                        demo_batch.append((
                            caseid,
                            r.get('receivedate'),
                            patient.get('patientsex'),
                            patient.get('patientonsetage')
                        ))
                        
                        for d in patient.get('drug', []):
                            drug_batch.append((
                                caseid,
                                d.get('drugcharacterization'),
                                d.get('medicinalproduct')
                            ))
                            
                        for react in patient.get('reaction', []):
                            reac_batch.append((
                                caseid,
                                react.get('reactionmeddrapt')
                            ))
    except Exception as e:
        print(f"Error processing {zip_path}: {e}")
        return

    # Insert batches
    if demo_batch:
        con.executemany("INSERT INTO demo VALUES (?, ?, ?, ?)", demo_batch)
    if drug_batch:
        con.executemany("INSERT INTO drug VALUES (?, ?, ?)", drug_batch)
    if reac_batch:
        con.executemany("INSERT INTO reac VALUES (?, ?)", reac_batch)

def main():
    con = init_db()
    zip_files = glob.glob(str(DATA_DIR / "*.json.zip"))
    
    print(f"Found {len(zip_files)} zip files to process.")
    for idx, zip_file in enumerate(zip_files):
        print(f"[{idx+1}/{len(zip_files)}] Processing {os.path.basename(zip_file)}...")
        process_file(zip_file, con)
        
    print("Data loading complete.")
    con.close()

if __name__ == "__main__":
    os.chdir(Path(__file__).parent)
    main()
