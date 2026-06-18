"""Verify improved ETF name extraction"""
import pandas as pd

output_file = r"C:\TestRepo\ExcelTool\consolidated_portfolio_20260528_134154.xlsx"

print("=" * 80)
print("VERIFYING IMPROVED ETF NAME EXTRACTION")
print("=" * 80)

df = pd.read_excel(output_file, sheet_name="Consolidated Portfolio")

# Test specific ISINs from files that were problematic
test_cases = {
    'NH.xlsx': ('INE068V01023', 'Nippon India Nifty Pharma'),
    'NO.xlsx': ('INE976G01028', 'Nippon India Nifty Auto'),
    'NZ.xlsx': ('INE669E01016', 'Nippon India ETF Nifty IT'),
    'NB.xlsx': ('INE021A01026', 'NIPPON INDIA ETF NIFTY 50 BEES'),
    'CC.xlsx': ('INE053A01029', 'CPSE ETF'),
    'IB.xlsx': ('INE855F01042', 'INFRASTRUCTURE'),
    'JZ.xlsx': ('INE338I01027', 'NIFTY NEXT 50')
}

print("\nChecking previously problematic files:\n")

for filename, (isin, expected_text) in test_cases.items():
    row = df[df['ISIN'] == isin]
    
    if row.empty:
        print(f"⚠️  {filename}: ISIN {isin} not found")
        continue
    
    # Get all ETF names for this ISIN
    etf_cols = [f'ETF-{i}' for i in range(1, 8)]
    etfs = []
    for col in etf_cols:
        if pd.notna(row.iloc[0].get(col)) and row.iloc[0].get(col):
            etfs.append(row.iloc[0][col])
    
    # Check if any ETF name contains the expected text
    found_full_name = False
    full_etf_name = None
    
    for etf in etfs:
        if expected_text.upper() in etf.upper():
            found_full_name = True
            full_etf_name = etf
            break
    
    if found_full_name:
        # Truncate long names
        display_name = full_etf_name[:70] + "..." if len(full_etf_name) > 70 else full_etf_name
        print(f"✓ {filename}: {display_name}")
    else:
        print(f"❌ {filename}: Still showing abbreviated name or not found")
        print(f"   ETFs found: {etfs}")

print("\n" + "=" * 80)
print("OVERALL STATISTICS")
print("=" * 80)

# Count how many ISINs have full ETF names vs abbreviated
etf_cols = [f'ETF-{i}' for i in range(1, 8)]
abbreviated_count = 0
full_name_count = 0

for idx, row in df.iterrows():
    if row['ISIN'] == 'TOTAL':
        continue
    
    for col in etf_cols:
        etf_name = row.get(col)
        if pd.notna(etf_name) and etf_name:
            # Check if it's abbreviated (2-3 chars only)
            if len(etf_name) <= 3:
                abbreviated_count += 1
            else:
                full_name_count += 1

total_etf_entries = abbreviated_count + full_name_count
print(f"\nTotal ETF entries: {total_etf_entries}")
print(f"Full ETF names: {full_name_count} ({full_name_count*100/total_etf_entries:.1f}%)")
print(f"Abbreviated names: {abbreviated_count} ({abbreviated_count*100/total_etf_entries:.1f}%)")

if abbreviated_count == 0:
    print("\n✓✓✓ SUCCESS! All ETF names extracted properly!")
else:
    print(f"\n⚠️  Still have {abbreviated_count} abbreviated names")



