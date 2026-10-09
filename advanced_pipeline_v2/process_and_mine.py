import pandas as pd
import numpy as np
from pathlib import Path
from mlxtend.preprocessing import TransactionEncoder
from mlxtend.frequent_patterns import fpgrowth
import math

# Reactions to exclude as they don't provide significant pharmacological learning
EXCLUDED_REACTIONS = {
    "OVERDOSE", "DRUG DEPENDENCE", "INTENTIONAL OVERDOSE", "DRUG ABUSE", 
    "TOXICITY TO VARIOUS AGENTS", "SUICIDE ATTEMPT", "COMPLETED SUICIDE",
    "SUBSTANCE ABUSE", "ACCIDENTAL OVERDOSE", "DRUG INEFFECTIVE",
    "OFF LABEL USE", "PRODUCT USE IN UNAPPROVED INDICATION",
    "INTENTIONAL PRODUCT MISUSE", "PRODUCT USE ISSUE",
    "PLASMA CELL MYELOMA", "COVID-19", "ASTHMA", "RHEUMATOID ARTHRITIS",
    "PSORIASIS", "DEATH", "PRODUCT DOSE OMISSION ISSUE", "ILLNESS",
    "CONDITION AGGRAVATED", "INAPPROPRIATE SCHEDULE OF PRODUCT ADMINISTRATION",
    "INCORRECT DOSE ADMINISTERED", "INTENTIONAL PRODUCT USE ISSUE"
}

def clean_data(df):
    print(f"Original records: {len(df)}")
    
    # Filter out uninformative reactions
    df = df[~df['reaction'].isin(EXCLUDED_REACTIONS)]
    print(f"After removing uninformative behavioral/overdose reactions: {len(df)}")
    
    # Drop rows with missing crucial data
    df = df.dropna(subset=['drugs', 'reaction'])
    return df

def calculate_ror(contingency_table):
    """Calculate Reporting Odds Ratio (ROR) and 95% CI Lower Bound"""
    # a: drug + reaction, b: drug + other reactions
    # c: other drugs + reaction, d: other drugs + other reactions
    a, b, c, d = contingency_table
    
    # Add 0.5 to cells to prevent division by zero (Haldane-Anscombe correction)
    a, b, c, d = a + 0.5, b + 0.5, c + 0.5, d + 0.5
    
    ror = (a * d) / (b * c)
    se = math.sqrt(1/a + 1/b + 1/c + 1/d)
    ci_lower = math.exp(math.log(ror) - 1.96 * se)
    
    return ror, ci_lower

def mine_polypharmacy_signals(df, min_support=0.01):
    print("Starting frequent itemset mining using FP-Growth...")
    
    signals = []
    
    # We analyze per reaction to find synergistic drug triplets
    reactions = df['reaction'].value_counts()
    # Focus on top 50 meaningful reactions for processing time
    top_reactions = reactions.head(50).index
    
    report_df = df.groupby('report_id').agg({
        'drugs': 'first',
        'reaction': lambda x: set(x)
    }).reset_index()

    for reaction in top_reactions:
        print(f"Mining signals for: {reaction}")
        
        # Subset data
        rx_df = df[df['reaction'] == reaction]
        if len(rx_df) < 20: continue
            
        te = TransactionEncoder()
        te_ary = te.fit(rx_df['drugs']).transform(rx_df['drugs'])
        transactions = pd.DataFrame(te_ary, columns=te.columns_)
        
        # FP-Growth for triplets
        try:
            freq_items = fpgrowth(transactions, min_support=0.05, use_colnames=True, max_len=3)
        except TypeError: # Fallback if max_len isn't supported in this version
            freq_items = fpgrowth(transactions, min_support=0.05, use_colnames=True)
            
        freq_items['length'] = freq_items['itemsets'].apply(lambda x: len(x))
        triplets = freq_items[freq_items['length'] == 3]
        
        mask_reaction_report = report_df['reaction'].apply(lambda rx_set: reaction in rx_set)
        
        for _, row in triplets.iterrows():
            triplet = list(row['itemsets'])
            
            # Count occurrences at the report level
            def has_triplet(drug_list):
                return all(d in drug_list for d in triplet)
            
            mask_triplet = report_df['drugs'].apply(has_triplet)
            
            a = (mask_triplet & mask_reaction_report).sum()
            b = (mask_triplet & ~mask_reaction_report).sum()
            c = (~mask_triplet & mask_reaction_report).sum()
            d = (~mask_triplet & ~mask_reaction_report).sum()
            
            if a >= 5: # Minimum 5 co-occurrences
                ror, ror_lcl = calculate_ror((a, b, c, d))
                
                signals.append({
                    "drug_a": triplet[0],
                    "drug_b": triplet[1],
                    "drug_c": triplet[2],
                    "reaction": reaction,
                    "n_reports": a,
                    "ror": ror,
                    "ror_lcl": ror_lcl
                })
                
    results_df = pd.DataFrame(signals)
    if not results_df.empty:
        # Filter for statistically significant signals (Lower CI > 1.0)
        results_df = results_df[results_df['ror_lcl'] > 1.0]
        results_df = results_df.sort_values('ror', ascending=False)
        
        output_dir = Path("data")
        output_dir.mkdir(exist_ok=True)
        results_df.to_csv(output_dir / "significant_triplets.csv", index=False)
        print(f"Saved {len(results_df)} significant 3-drug signals to data/significant_triplets.csv")
    else:
        print("No significant signals found with current parameters.")

if __name__ == "__main__":
    data_path = Path("data/structured_fda_data.parquet")
    if not data_path.exists():
        print("Data file not found. Run fetch_fda_api.py first.")
        exit(1)
        
    df = pd.read_parquet(data_path)
    clean_df = clean_data(df)
    mine_polypharmacy_signals(clean_df, min_support=0.02)
