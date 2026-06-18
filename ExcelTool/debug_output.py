"""Debug script to inspect the output file"""
import pandas as pd

output_file = r"C:\TestRepo\ExcelTool\consolidated_portfolio_20260526_153048.xlsx"

print("=" * 80)
print("Inspecting output file - ISINs Missing Names sheet")
print("=" * 80)

# Read the ISINs Missing Names sheet
df = pd.read_excel(output_file, sheet_name='ISINs Missing Names')

print(f"\nTotal ISINs with missing names: {len(df)}")
print(f"\nColumn names: {list(df.columns)}")

print("\n" + "=" * 80)
print("First 10 entries:")
print(df.head(10))

print("\n" + "=" * 80)
# Check for the specific ISIN mentioned by user
target_isin = "INE048G01026"
result = df[df['ISIN'] == target_isin]
print(f"\nSearching for ISIN: {target_isin}")
if len(result) > 0:
    print("Found in Missing Names sheet:")
    print(result)
else:
    print("NOT found in Missing Names sheet - checking main sheet...")
    df_main = pd.read_excel(output_file, sheet_name='Consolidated Portfolio')
    result_main = df_main[df_main['ISIN'] == target_isin]
    if len(result_main) > 0:
        print("Found in main sheet:")
        print(result_main)

print("\n" + "=" * 80)
print("Sample of source files:")
print(df[['ISIN', 'First Source File']].head(10))
