import os
import glob
import duckdb
from pathlib import Path

# Paths
DATA_DIR = Path("../../data/raw/faers")
DB_PATH = Path("../../data/processed/faers.db")

def init_db():
    print(f"Connecting to database at {DB_PATH}")
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect(str(DB_PATH))
    
    # Create tables if they don't exist
    con.execute("""
        CREATE TABLE IF NOT EXISTS demo (
            primaryid VARCHAR,
            caseid VARCHAR,
            caseversion VARCHAR,
            i_f_code VARCHAR,
            event_dt VARCHAR,
            mfr_dt VARCHAR,
            init_fda_dt VARCHAR,
            fda_dt VARCHAR,
            rept_cod VARCHAR,
            auth_num VARCHAR,
            mfr_num VARCHAR,
            mfr_sndr VARCHAR,
            lit_ref VARCHAR,
            age VARCHAR,
            age_cod VARCHAR,
            age_grp VARCHAR,
            sex VARCHAR,
            e_sub VARCHAR,
            wt VARCHAR,
            wt_cod VARCHAR,
            rept_dt VARCHAR,
            to_mfr VARCHAR,
            occp_cod VARCHAR,
            reporter_country VARCHAR,
            occr_country VARCHAR
        )
    """)
    
    con.execute("""
        CREATE TABLE IF NOT EXISTS drug (
            primaryid VARCHAR,
            caseid VARCHAR,
            drug_seq VARCHAR,
            role_cod VARCHAR,
            drugname VARCHAR,
            prod_ai VARCHAR,
            val_vbm VARCHAR,
            route VARCHAR,
            dose_vbm VARCHAR,
            cum_dose_chr VARCHAR,
            cum_dose_unit VARCHAR,
            dechal VARCHAR,
            rechal VARCHAR,
            lot_num VARCHAR,
            exp_dt VARCHAR,
            nda_num VARCHAR,
            dose_amt VARCHAR,
            dose_unit VARCHAR,
            dose_form VARCHAR,
            dose_freq VARCHAR
        )
    """)
    
    con.execute("""
        CREATE TABLE IF NOT EXISTS reac (
            primaryid VARCHAR,
            caseid VARCHAR,
            pt VARCHAR,
            drug_rec_act VARCHAR
        )
    """)
    
    con.execute("""
        CREATE TABLE IF NOT EXISTS outc (
            primaryid VARCHAR,
            caseid VARCHAR,
            outc_cod VARCHAR
        )
    """)
    
    return con

def load_data(con):
    quarters = [d for d in DATA_DIR.iterdir() if d.is_dir()]
    
    for quarter_dir in quarters:
        print(f"Processing directory: {quarter_dir.name}")
        
        # FAERS ASCII files are typically in an 'ascii' folder inside the extracted zip
        ascii_dir = quarter_dir / "ascii"
        if not ascii_dir.exists():
            # sometimes files are in root of zip
            ascii_dir = quarter_dir
            
        demo_files = glob.glob(str(ascii_dir / "DEMO*.txt"))
        drug_files = glob.glob(str(ascii_dir / "DRUG*.txt"))
        reac_files = glob.glob(str(ascii_dir / "REAC*.txt"))
        outc_files = glob.glob(str(ascii_dir / "OUTC*.txt"))
        
        for f in demo_files:
            print(f"Loading {os.path.basename(f)} into demo table...")
            con.execute(f"COPY demo FROM '{f}' (DELIMITER '$', HEADER, QUOTE '')")
            
        for f in drug_files:
            print(f"Loading {os.path.basename(f)} into drug table...")
            con.execute(f"COPY drug FROM '{f}' (DELIMITER '$', HEADER, QUOTE '')")
            
        for f in reac_files:
            print(f"Loading {os.path.basename(f)} into reac table...")
            con.execute(f"COPY reac FROM '{f}' (DELIMITER '$', HEADER, QUOTE '')")
            
        for f in outc_files:
            print(f"Loading {os.path.basename(f)} into outc table...")
            con.execute(f"COPY outc FROM '{f}' (DELIMITER '$', HEADER, QUOTE '')")

def main():
    os.chdir(Path(__file__).parent)
    con = init_db()
    load_data(con)
    print("Data loading complete.")
    con.close()

if __name__ == "__main__":
    main()
