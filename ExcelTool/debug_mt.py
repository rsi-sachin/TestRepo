"""
Test script: Check if improved ETF name extraction will work on problematic files
Tests both CURRENT logic (endswith 'ETF') vs IMPROVED logic (contains 'ETF')
"""

import pandas as pd
import os
from pathlib import Path

ETF_FOLDER = r"C:\Users\sachin_gupta\OneDrive - R Systems International Ltd\Documents\Sachin\Personal\Documents\Demat\FY_26_27\ETF\April"

# Files that currently show abbreviated names (2-3 chars) - likely failed extractions
PROBLEMATIC_FILES = ['NH.xlsx', 'NO.xlsx', 'NZ.xlsx', 'NB.xlsx', 'CC.xlsx', 'EE.xlsx', 
                     'FT.xlsx', 'HS.xlsx', 'HT.xlsx', 'IB.xlsx', 'ID.xlsx', 'JZ.xlsx', 
                     'MC.xlsx', 'ND.xlsx', 'TP.xlsx']

def extract_etf_name_current(file_path):
    """CURRENT logic: Only strings ENDING with 'ETF'"""
    try:
        df_preview = pd.read_excel(file_path, sheet_name=0, header=None, nrows=20)
        etf_candidates = []
        for idx, row in df_preview.iterrows():
            for cell_value in row:
                if pd.notna(cell_value):
                    cell_str = str(cell_value).strip()
                    if cell_str.upper().endswith('ETF'):
                        etf_candidates.append(cell_str)
        if etf_candidates:
            return etf_candidates[0]
        return None
    except:
        return None

def extract_etf_name_improved(file_path):
    """IMPROVED logic: Strings CONTAINING 'ETF' (with priority for ending with ETF)"""
    try:
        df_preview = pd.read_excel(file_path, sheet_name=0, header=None, nrows=25)
        
        # Priority 1: Strings ending with 'ETF'
        etf_ending = []
        etf_containing = []
        
        for idx, row in df_preview.iterrows():
            for cell_value in row:
                if pd.notna(cell_value):
                    cell_str = str(cell_value).strip()
                    if len(cell_str) > 5:  # Avoid very short strings
                        if cell_str.upper().endswith('ETF'):
                            etf_ending.append(cell_str)
                        elif 'ETF' in cell_str.upper():
                            etf_containing.append(cell_str)
        
        # Return first match with priority
        if etf_ending:
            return etf_ending[0]
        if etf_containing:
            return etf_containing[0]
        return None
    except:
        return None

print("=" * 80)
print("ETF NAME EXTRACTION - TESTING IMPROVED LOGIC")
print("=" * 80)

results = []

print("\nTesting files that currently show abbreviated names...\n")

for filename in PROBLEMATIC_FILES:
    file_path = os.path.join(ETF_FOLDER, filename)
    
    if not os.path.exists(file_path):
        print(f"⚠️  {filename}: FILE NOT FOUND")
        continue
    
    try:
        current_result = extract_etf_name_current(file_path)
        improved_result = extract_etf_name_improved(file_path)
        
        # Fallback to filename if still nothing
        fallback = os.path.splitext(filename)[0]
        
        status = "✓ IMPROVED" if improved_result and improved_result != fallback else "✗ STILL FAILS"
        
        results.append({
            'file': filename,
            'current': current_result or f"(fallback: {fallback})",
            'improved': improved_result or f"(fallback: {fallback})",
            'status': status
        })
        
        print(f"{filename}")
        print(f"  Current:  {current_result or '❌ None'}")
        print(f"  Improved: {improved_result or '❌ None'}")
        print(f"  Status:   {status}\n")
        
    except Exception as e:
        print(f"❌ {filename}: ERROR - {str(e)}\n")

print("=" * 80)
print("SUMMARY")
print("=" * 80)

current_success = sum(1 for r in results if r['current'] and not r['current'].startswith('(fallback'))
improved_success = sum(1 for r in results if r['improved'] and not r['improved'].startswith('(fallback'))

print(f"\nTotal files tested: {len(results)}")
print(f"Current logic success: {current_success}/{len(results)}")
print(f"Improved logic success: {improved_success}/{len(results)}")
print(f"Improvement: +{improved_success - current_success} files\n")

if improved_success > current_success:
    print("✓ IMPROVED LOGIC IS BETTER - Recommend implementing the change")
else:
    print("⚠️  IMPROVED LOGIC SHOWS NO IMPROVEMENT - Need different approach")


