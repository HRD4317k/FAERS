import duckdb
import pandas as pd
import numpy as np
import statsmodels.api as sm
import statsmodels.formula.api as smf
from statsmodels.stats.multitest import multipletests
from mlxtend.preprocessing import TransactionEncoder
from mlxtend.frequent_patterns import fpgrowth
from pathlib import Path
import os
from tqdm import tqdm

DB_PATH = Path("../../data/processed/faers.db")

def calculate_ror(a, b, c, d):
    # ROR = (a/b) / (c/d) = (a*d) / (b*c)
    # Add 0.5 to cells to prevent division by zero (Haldane-Anscombe correction)
    a, b, c, d = a+0.5, b+0.5, c+0.5, d+0.5
    ror = (a * d) / (b * c)
    se = np.sqrt(1/a + 1/b + 1/c + 1/d)
    lower_ci = np.exp(np.log(ror) - 1.96 * se)
    upper_ci = np.exp(np.log(ror) + 1.96 * se)
    return ror, lower_ci, upper_ci

def get_lower_order_counts(con, d1, d2, d3, ae):
    """Get the 'a' counts (co-occurrences with AE) for all subsets of {D1, D2, D3}"""
    drugs = [d1, d2, d3]
    counts = {}
    
    # Total reports with AE
    n_ae = con.execute("SELECT COUNT(DISTINCT caseid) FROM clean_reac WHERE reaction = ?", (ae,)).fetchone()[0]
    total = con.execute("SELECT COUNT(DISTINCT caseid) FROM demo").fetchone()[0]
    
    # Helper to calculate subset ROR
    def calc_subset_ror(subset_drugs):
        conditions = " AND ".join([f"EXISTS (SELECT 1 FROM clean_drug dg WHERE dg.caseid = r.caseid AND dg.drugname = '{d}')" for d in subset_drugs])
        # 'a' = has subset + AE
        q_a = f"SELECT COUNT(DISTINCT r.caseid) FROM clean_reac r WHERE r.reaction = ? AND {conditions}"
        a = con.execute(q_a, (ae,)).fetchone()[0]
        
        # 'a+b' = has subset
        q_ab_conditions = " AND ".join([f"EXISTS (SELECT 1 FROM clean_drug dg WHERE dg.caseid = d.caseid AND dg.drugname = '{d}')" for d in subset_drugs])
        q_ab = f"SELECT COUNT(DISTINCT d.caseid) FROM demo d WHERE {q_ab_conditions}"
        ab = con.execute(q_ab).fetchone()[0]
        
        b = ab - a
        c = n_ae - a
        d = total - ab - n_ae + a
        ror, _, _ = calculate_ror(a, b, c, d)
        return ror

    # Individual
    counts['A'] = calc_subset_ror([d1])
    counts['B'] = calc_subset_ror([d2])
    counts['C'] = calc_subset_ror([d3])
    
    # Pairwise
    counts['AB'] = calc_subset_ror([d1, d2])
    counts['AC'] = calc_subset_ror([d1, d3])
    counts['BC'] = calc_subset_ror([d2, d3])
    
    return counts

def test_3way_interaction(con, d1, d2, d3, ae):
    # Fetch boolean matrix for Logistic Regression
    query = f"""
        SELECT 
            d.caseid,
            MAX(CASE WHEN dg.drugname = '{d1}' THEN 1 ELSE 0 END) as d1,
            MAX(CASE WHEN dg.drugname = '{d2}' THEN 1 ELSE 0 END) as d2,
            MAX(CASE WHEN dg.drugname = '{d3}' THEN 1 ELSE 0 END) as d3,
            MAX(CASE WHEN r.reaction = '{ae}' THEN 1 ELSE 0 END) as y
        FROM demo d
        LEFT JOIN clean_drug dg ON d.caseid = dg.caseid AND dg.drugname IN ('{d1}', '{d2}', '{d3}')
        LEFT JOIN clean_reac r ON d.caseid = r.caseid AND r.reaction = '{ae}'
        GROUP BY d.caseid
    """
    df = con.execute(query).fetchdf()
    
    if df['y'].sum() < 5 or df['d1'].sum() == 0 or df['d2'].sum() == 0 or df['d3'].sum() == 0:
        return None, None
        
    df['d1_d2'] = df['d1'] * df['d2']
    df['d1_d3'] = df['d1'] * df['d3']
    df['d2_d3'] = df['d2'] * df['d3']
    df['d1_d2_d3'] = df['d1'] * df['d2'] * df['d3']
    
    try:
        model = smf.logit("y ~ d1 + d2 + d3 + d1_d2 + d1_d3 + d2_d3 + d1_d2_d3", data=df).fit(disp=0)
        p_value = model.pvalues.get('d1_d2_d3', 1.0)
        coef = model.params.get('d1_d2_d3', 0.0)
        return coef, p_value
    except Exception:
        return None, None

def main():
    os.chdir(Path(__file__).parent)
    con = duckdb.connect(str(DB_PATH))
    
    # Configuration
    MIN_SUPPORT_ABS = 20 # Minimum occurrences of (D1, D2, D3)
    MIN_SUPPORT_AE = 10  # Minimum occurrences of (D1, D2, D3, AE)
    
    total_reports = con.execute("SELECT COUNT(DISTINCT caseid) FROM demo").fetchone()[0]
    if total_reports == 0:
        print("Database is empty. Please run data ingestion first.")
        return
        
    print(f"Total reports: {total_reports}")
    
    # 1. FP-Growth to find candidate 3-drug patterns
    print("Extracting drug transactions for FP-Growth...")
    # To save memory, we can limit to drugs that appear at least 100 times in the dataset
    freq_drugs = con.execute("SELECT drugname FROM clean_drug GROUP BY drugname HAVING COUNT(DISTINCT caseid) > 100").fetchdf()['drugname'].tolist()
    
    # Get lists of drugs per caseid
    tx_df = con.execute(f"SELECT caseid, list(drugname) as drugs FROM clean_drug WHERE drugname IN {tuple(freq_drugs)} GROUP BY caseid HAVING count(drugname) >= 3").fetchdf()
    transactions = tx_df['drugs'].tolist()
    
    print("Running FP-Growth...")
    te = TransactionEncoder()
    te_ary = te.fit(transactions).transform(transactions, sparse=True)
    df_sparse = pd.DataFrame.sparse.from_spmatrix(te_ary, columns=te.columns_)
    
    # We want itemsets of length 3 that appear >= MIN_SUPPORT_ABS
    min_sup_rel = MIN_SUPPORT_ABS / len(transactions)
    frequent_itemsets = fpgrowth(df_sparse, min_support=min_sup_rel, use_colnames=True)
    frequent_itemsets['length'] = frequent_itemsets['itemsets'].apply(lambda x: len(x))
    triplets = frequent_itemsets[frequent_itemsets['length'] == 3].copy()
    
    print(f"Found {len(triplets)} frequent 3-drug triplets.")
    
    results = []
    
    # Limit processing for demonstration to top 50 most frequent triplets
    triplets = triplets.sort_values(by='support', ascending=False).head(50)
    
    for idx, row in tqdm(triplets.iterrows(), total=len(triplets), desc="Processing Triplets"):
        drugs = list(row['itemsets'])
        d1, d2, d3 = drugs[0], drugs[1], drugs[2]
        
        # Find AEs that co-occur >= MIN_SUPPORT_AE
        query_aes = f"""
            SELECT r.reaction, COUNT(DISTINCT r.caseid) as a
            FROM clean_reac r
            JOIN clean_drug dg1 ON r.caseid = dg1.caseid AND dg1.drugname = '{d1}'
            JOIN clean_drug dg2 ON r.caseid = dg2.caseid AND dg2.drugname = '{d2}'
            JOIN clean_drug dg3 ON r.caseid = dg3.caseid AND dg3.drugname = '{d3}'
            GROUP BY r.reaction
            HAVING COUNT(DISTINCT r.caseid) >= {MIN_SUPPORT_AE}
        """
        aes = con.execute(query_aes).fetchdf()
        
        # Ab count
        query_ab = f"""
            SELECT COUNT(DISTINCT d.caseid) 
            FROM demo d
            JOIN clean_drug dg1 ON d.caseid = dg1.caseid AND dg1.drugname = '{d1}'
            JOIN clean_drug dg2 ON d.caseid = dg2.caseid AND dg2.drugname = '{d2}'
            JOIN clean_drug dg3 ON d.caseid = dg3.caseid AND dg3.drugname = '{d3}'
        """
        ab = con.execute(query_ab).fetchone()[0]
        
        for _, ae_row in aes.iterrows():
            ae = ae_row['reaction']
            a = ae_row['a']
            
            # Gate 1 & 2: Support checks (Already met)
            
            # N_ae
            n_ae = con.execute("SELECT COUNT(DISTINCT caseid) FROM clean_reac WHERE reaction = ?", (ae,)).fetchone()[0]
            
            b = ab - a
            c = n_ae - a
            d = total_reports - ab - n_ae + a
            
            # Gate 3: Disproportionality
            ror_abc, ci_low, ci_high = calculate_ror(a, b, c, d)
            if ror_abc <= 1 or ci_low <= 1:
                continue
                
            # Gate 4: Higher-order effect (Hierarchical Comparison)
            lower_rors = get_lower_order_counts(con, d1, d2, d3, ae)
            max_lower_ror = max(lower_rors.values())
            interaction_strength = np.log(ror_abc) - np.log(max_lower_ror)
            
            if interaction_strength <= 0:
                continue
                
            # Gate 5: Three-way Regression
            beta_abc, p_val = test_3way_interaction(con, d1, d2, d3, ae)
            if beta_abc is None:
                continue
                
            results.append({
                'Drug 1': d1,
                'Drug 2': d2,
                'Drug 3': d3,
                'Adverse Event': ae,
                'a': a,
                'ROR_ABC': ror_abc,
                'ROR_ABC_Lower_CI': ci_low,
                'Max_Lower_Order_ROR': max_lower_ror,
                'Interaction_Strength': interaction_strength,
                'Beta_ABC': beta_abc,
                'P_Value': p_val
            })
            
    if not results:
        print("No significant 3-drug polypharmacy signals found.")
        con.close()
        return
        
    results_df = pd.DataFrame(results)
    
    # FDR Correction (Gate 5 extension)
    _, q_values, _, _ = multipletests(results_df['P_Value'], alpha=0.05, method='fdr_bh')
    results_df['Q_Value'] = q_values
    
    # Filter by Q-value
    final_signals = results_df[results_df['Q_Value'] < 0.05].copy()
    
    # Gate 6 & 7: Temporal persistence and Emerging Signal Score can be added later
    final_signals['Emerging_Signal_Score'] = final_signals['Interaction_Strength'] * final_signals['ROR_ABC_Lower_CI']
    final_signals = final_signals.sort_values(by='Emerging_Signal_Score', ascending=False)
    
    print("\n--- FINAL 3-DRUG POLYPHARMACY SIGNALS ---")
    print(final_signals.to_string(index=False))
    
    # Save to database
    con.execute("CREATE OR REPLACE TABLE polypharmacy_signals AS SELECT * FROM final_signals")
    print("Signals saved to 'polypharmacy_signals' table.")
    
    con.close()

if __name__ == "__main__":
    main()
