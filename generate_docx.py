import os
from docx import Document
from docx.shared import Pt, Inches, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.shared import OxmlElement, qn

def set_margins(doc, margin):
    sections = doc.sections
    for section in sections:
        section.top_margin = Inches(margin)
        section.bottom_margin = Inches(margin)
        section.left_margin = Inches(margin)
        section.right_margin = Inches(margin)

def main():
    doc = Document()
    
    # Set narrow margins to fit on 2 pages
    set_margins(doc, 0.6)
    
    # Add logo and header using a table for layout
    table = doc.add_table(rows=1, cols=2)
    table.columns[0].width = Inches(1.5)
    table.columns[1].width = Inches(5.5)
    
    # Logo in the left cell
    cell_logo = table.cell(0, 0)
    p_logo = cell_logo.paragraphs[0]
    p_logo.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_logo = p_logo.add_run()
    if os.path.exists("iit_logo.png"):
        r_logo.add_picture("iit_logo.png", width=Inches(1.2))
        
    # Header in the right cell
    cell_header = table.cell(0, 1)
    p_header = cell_header.paragraphs[0]
    p_header.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    r1 = p_header.add_run("Indian Institute of Technology Kharagpur\n")
    r1.bold = True
    r1.font.size = Pt(13)
    
    r2 = p_header.add_run("Department of Industrial and Systems Engineering\n")
    r2.font.size = Pt(11)
    
    r3 = p_header.add_run("BTP-I Mid-Semester Project Summary\nAutumn Semester 2026-27")
    r3.font.size = Pt(11)

    # Divider
    doc.add_paragraph("_" * 70).alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    # Student Info Table
    info_table = doc.add_table(rows=1, cols=3)
    info_table.columns[0].width = Inches(2.5)
    info_table.columns[1].width = Inches(2.0)
    info_table.columns[2].width = Inches(2.5)
    
    # Headers
    h_row = info_table.rows[0].cells
    r_n = h_row[0].paragraphs[0].add_run("Name")
    r_n.bold = True
    r_r = h_row[1].paragraphs[0].add_run("Roll No.")
    r_r.bold = True
    r_s = h_row[2].paragraphs[0].add_run("Supervisor Professor")
    r_s.bold = True
    
    # Values
    v_row = info_table.add_row().cells
    v_row[0].paragraphs[0].add_run("Rishabh Dehariya")
    v_row[1].paragraphs[0].add_run("23IM10028")
    v_row[2].paragraphs[0].add_run("Sarada Prasad Sarmah")
    
    # Title
    title = doc.add_paragraph("\nAdvanced Pharmacovigilance: A Multi-Gate Polypharmacy Mining Framework Using Disproportionality Analysis and Machine Learning")
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    title.runs[0].bold = True
    title.runs[0].font.size = Pt(12)
    
    # Text formatting helper
    def add_section(heading, text):
        h = doc.add_paragraph()
        h.paragraph_format.space_before = Pt(6)
        h.paragraph_format.space_after = Pt(2)
        r = h.add_run(heading)
        r.bold = True
        r.font.size = Pt(11)
        
        p = doc.add_paragraph(text)
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p.paragraph_format.space_after = Pt(4)
        for run in p.runs:
            run.font.size = Pt(10)

    add_section("Background and Motivation", 
                "Adverse Drug Reactions (ADRs) are a leading cause of morbidity and mortality globally. With the increasing prevalence of polypharmacy (the concurrent use of multiple medications), identifying harmful drug-drug interactions is critical. Spontaneous reporting systems, such as the FDA Adverse Event Reporting System (FAERS), collect millions of post-marketing safety reports. However, analyzing this data is highly challenging due to extreme sparsity, reporting biases, and the combinatorial explosion of potential multi-drug interactions.\n"
                "While conventional data mining in pharmacovigilance focuses primarily on single-drug effects or 2-drug interactions, clinically significant ADRs are often triggered by higher-order combinations (3 or more drugs). Identifying these signals requires differentiating the true synergistic interaction from the individual toxicities of the constituent drugs. This project aims to address this gap by developing a robust, mathematically defensible pipeline that goes beyond mere co-occurrence, rigorously isolating authentic 3-drug polypharmacy signals from millions of nested FAERS records.")

    add_section("Related Work and Research Direction",
                "Prior research extensively explores 2-drug interactions in pharmacovigilance. Ibrahim et al. (2016) proposed a Hybrid Apriori approach that pairs frequent itemset mining with the Proportional Reporting Ratio (PRR) and Chi-square statistics to detect Drug Interaction Adverse Event (DIAE) signals. Crucially, they employed a Logistic Regression model to test for confounding and to isolate the specific 2-drug interaction coefficient [1].\n"
                "However, scaling these methodologies to 3-drug combinations introduces significant statistical noise and computational complexity. Simple rule mining generates thousands of spurious patterns driven by highly reported baseline drugs. This project extends the methodology of Ibrahim et al. by introducing a 'Multi-Gate' statistical framework for 3-drug combinations, utilizing FP-Growth for efficient candidate generation, Hierarchical Reporting Odds Ratio (ROR) comparisons, and 3-way Logistic Regression with Benjamini-Hochberg False Discovery Rate (FDR) correction to rigorously control type I errors.")
                
    add_section("Aim and Objectives",
                "The primary aim of this project is to develop and evaluate a scalable, automated pipeline to detect and statistically validate 3-drug polypharmacy adverse event signals from the OpenFDA database. The specific objectives are:\n"
                "• Data Integration: To engineer a pipeline capable of parsing millions of nested OpenFDA JSON reports into a high-performance relational database (DuckDB).\n"
                "• Candidate Generation: To apply the FP-Growth algorithm to efficiently mine frequent 3-drug itemsets that meet minimum absolute and relative support thresholds.\n"
                "• Hierarchical Validation: To compute the ROR for 3-drug combinations and mathematically compare them against all lower-order components (individual drugs and pairs) to ensure the triplet exhibits unique interaction risk.\n"
                "• Statistical Modeling: To implement a 3-way Logistic Regression model, extracting the interaction coefficient while adjusting for multiple testing using FDR correction.\n"
                "• Predictive Analytics: To evaluate the performance of advanced Machine Learning models (XGBoost, Random Forest, Lasso) in predicting the occurrence of severe ADRs based on patient drug exposure profiles.")
                
    add_section("Proposed System Architecture",
                "The system architecture separates data ingestion, statistical gating, predictive modeling, and interactive visualization into modular components. The pipeline flows as follows:\n"
                "1. OpenFDA JSON Data Ingestion & Relational Parsing (DuckDB)\n"
                "2. FP-Growth: Frequent 3-Drug Pattern Mining\n"
                "3. Hierarchical ROR & Confidence Interval Validation\n"
                "4. 3-Way Logistic Regression & FDR (q < 0.05) Gating\n"
                "5. Predictive ML Models (XGBoost, Random Forest, Lasso)\n"
                "6. Streamlit Interactive Polypharmacy Dashboard")
                
    add_section("Current Progress",
                "A functional prototype of the end-to-end framework has been implemented and validated on a subset of the 2023 FAERS dataset. The current achievements include:\n"
                "• Ingestion Pipeline: Developed an automated script that securely fetches, streams, and flattens OpenFDA zip partitions directly into a DuckDB analytical database without intermediary disk extraction, dramatically optimizing storage and ingestion speed.\n"
                "• Multi-Gate Polypharmacy Miner: Implemented the core analytical engine in Python using mlxtend and statsmodels. The engine successfully mines 3-drug combinations, computes subset ROR comparisons (producing a novel Interaction Strength metric), and fits the 3-way Logistic Regression model.\n"
                "• Signal Detection: The pipeline successfully detected true, statistically significant polypharmacy signals (e.g., Fentanyl + Opana + Percocet leading to Overdose) that survived all mathematical gating and FDR thresholds.\n"
                "• Advanced ML Models: Designed an automated module that engineers sparse one-hot encoded drug matrices and trains XGBoost, Random Forest, and Lasso Regression models to classify adverse event occurrences, capturing complex non-linear drug interactions.\n"
                "• Interactive Dashboard: Built a multi-page Streamlit application that dynamically visualizes the surviving polypharmacy signals, predictive model metrics (Accuracy, ROC-AUC, F1), and provides an exploratory interface for single-drug ADR statistics.")
                
    add_section("Planned Experimental Study and Further Development",
                "The next phase of the project will focus on scaling the framework and incorporating temporal analysis:\n"
                "• Full-Scale Execution: Execute the ingestion and Multi-Gate mining pipeline over the entire multi-year OpenFDA database (millions of reports) to uncover hidden, rare 3-drug signals.\n"
                "• Temporal Persistence Analysis: Analyze quarter-over-quarter growth rates of detected signals to ensure they are consistent over time rather than isolated anomalies, culminating in a robust Emerging Signal Score.\n"
                "• Model Optimization & Deep Learning: Tune the hyperparameters of the XGBoost and Random Forest classifiers. Explore the application of tabular transformer architectures (e.g., TabNet) if computational resources permit.\n"
                "• FDA Label Integration: Integrate the openFDA Drug Labeling API to automatically cross-reference discovered signals against documented manufacturer warnings.")
                
    add_section("Expected Outcome",
                "This project is expected to deliver a highly defensible, end-to-end data mining and machine learning framework capable of separating true multi-drug interaction signals from baseline reporting noise in massive pharmacovigilance datasets. The resulting open-source pipeline and interactive dashboard will serve as a powerful exploratory tool, demonstrating a rigorous statistical methodology that improves upon conventional 2-drug association rule mining.")
                
    add_section("References",
                "[1] H. Ibrahim, A. El-Makky, and G. Taha, \"Mining association patterns of drug-interactions using post marketing FDA's spontaneous reporting data,\" Journal of Biomedical Informatics, 2016.\n"
                "[2] Y. Harpaz et al., \"Mining Electronic Health Records for Adverse Drug Effects,\" Clinical Pharmacology & Therapeutics, 2012.\n"
                "[3] E. Noguchi et al., \"Performance of Apriori Algorithm for Detecting Drug-Drug Interactions from Spontaneous Reporting Systems,\" Pharmacy, 2021.\n"
                "[4] C. Bate et al., \"The Evolving Role of Disproportionality Analysis in Pharmacovigilance,\" Drug Safety, 2020.\n"
                "[5] X. Li et al., \"Detecting Adverse High-Order Drug Combinations from Individual Case Safety Reports,\" Computational Statistics, 2023.")
                
    doc.add_paragraph("\n")
    
    # Signatures
    sig_table = doc.add_table(rows=1, cols=2)
    sig_table.columns[0].width = Inches(3.5)
    sig_table.columns[1].width = Inches(3.5)
    
    row = sig_table.rows[0].cells
    
    # Student
    p1 = row[0].paragraphs[0]
    p1.add_run("Submitted by\n\n\n________________________\nRishabh Dehariya\nRoll No.: 23IM10028\nDepartment of Industrial and Systems Engineering\nIIT Kharagpur").font.size = Pt(10)
    
    # Supervisor
    p2 = row[1].paragraphs[0]
    p2.add_run("Supervisor's Signature\n\n\n________________________\nProf. Sarada Prasad Sarmah\nDepartment of Industrial and Systems Engineering\nIIT Kharagpur").font.size = Pt(10)

    doc.save('Rishabh_Dehariya_BTP_Summary_v2.docx')
    print("Saved Rishabh_Dehariya_BTP_Summary_v2.docx")

if __name__ == "__main__":
    main()
