# ETF Holdings Aggregator

A Python tool that consolidates ISIN investments across multiple ETF holdings Excel files.

## Overview

This tool processes multiple ETF holdings Excel files, extracts ISIN data, instrument names, and portfolio percentages, then aggregates the investments to produce a consolidated portfolio report.

### Key Features

- **Automatic column detection**: Handles varying Excel formats and column names
- **Fuzzy matching**: Identifies ISIN, instrument name, and percentage columns automatically
- **Investment calculation**: Assumes configurable investment amount per ETF file
- **Aggregation**: Combines investments for ISINs appearing in multiple files
- **Dual output**: Generates both Excel (.xlsx) and CSV files
- **Formatted reports**: Professional Excel output with formatting and summary statistics

## Requirements

- Python 3.7 or higher
- Required libraries:
  - pandas >= 1.0.0
  - openpyxl >= 3.0.0
  - xlrd >= 2.0.0

## Installation

1. Clone or download this repository
2. Install dependencies:

```bash
pip install -r requirements.txt
```

Or install manually:

```bash
pip install pandas openpyxl xlrd
```

## Usage

### Basic Usage

```bash
python etf_aggregator.py --input <folder_path> --output <output_name>
```

### Examples

**Process all Excel files in the "April" folder:**
```bash
python etf_aggregator.py --input "April" --output "consolidated_portfolio"
```

**Process with custom investment amount (₹50,000 per ETF):**
```bash
python etf_aggregator.py -i "April" -o "portfolio_50k" --investment 50000
```

**Process files in a specific directory:**
```bash
python etf_aggregator.py -i "C:\Users\sachin_gupta\OneDrive - R Systems International Ltd\Documents\Sachin\Personal\Documents\Demat\FY_26_27\ETF\April" -o "April_2026"
```

### Command-Line Arguments

| Argument | Short | Required | Default | Description |
|----------|-------|----------|---------|-------------|
| `--input` | `-i` | Yes | - | Input folder containing Excel files |
| `--output` | `-o` | No | `consolidated_portfolio` | Output file base name |
| `--investment` | - | No | `100000` | Investment amount per ETF file (₹) |

## Input File Requirements

Your Excel files should contain a table with the following columns (column names can vary):

### Required Columns

1. **ISIN Column** - Examples:
   - ISIN
   - ISIN Code
   - ISINCode
   - ISIN No

2. **Instrument Name Column** - Examples:
   - Name
   - Instrument Name
   - Stock Name
   - Script Name
   - Company Name

3. **Percentage Column** - Examples:
   - % of NAV
   - %
   - Percentage
   - Weight
   - % Weight
   - Portfolio %

### Supported Formats

- **.xlsx** - Excel 2007 and later
- **.xls** - Excel 97-2003
- **.xlsm** - Excel with macros

The tool automatically:
- Detects header rows (skips metadata)
- Handles merged cells
- Validates ISIN format
- Parses percentage values in various formats (5.25%, 5.25, 0.0525)

## Output

The tool generates two files with timestamps:

1. **Excel file** (`consolidated_portfolio_YYYYMMDD_HHMMSS.xlsx`):
   - Formatted table with 4 columns
   - Bold headers and total row
   - Number formatting (currency and percentages)
   - Auto-adjusted column widths

2. **CSV file** (`consolidated_portfolio_YYYYMMDD_HHMMSS.csv`):
   - Same data in CSV format for compatibility

### Output Columns

| Column | Description |
|--------|-------------|
| ISIN | 12-character ISIN code |
| Instrument Name | Name of the security |
| Total Investment (₹) | Aggregated investment amount across all ETF files |
| % of Portfolio | Percentage of total portfolio |

The last row shows the **TOTAL** with sum of all investments and portfolio percentage (100%).

## How It Works

1. **File Discovery**: Scans the input folder for Excel files (.xlsx, .xls, .xlsm)

2. **Column Detection**: For each file:
   - Detects the header row
   - Identifies ISIN, name, and percentage columns using fuzzy matching
   - Validates column presence

3. **Data Extraction**: 
   - Reads table data
   - Validates ISIN format (12 alphanumeric characters)
   - Parses percentage values
   - Calculates investment: `(% of NAV / 100) × Investment Amount`

4. **Aggregation**:
   - Combines data from all files
   - Sums investments for duplicate ISINs
   - Uses first encountered name for each ISIN

5. **Output Generation**:
   - Calculates total investment and portfolio percentages
   - Generates formatted Excel file
   - Exports CSV file
   - Displays summary statistics

## Example Output

```
ETF Holdings Aggregator
============================================================
Input folder: April
Investment per ETF: ₹100,000.00
Output base name: consolidated_portfolio

Found 22 Excel file(s)
============================================================
Processing: CC.xlsx
  ✓ Found 45 ISINs, Total: 99.85%
Processing: EE.xlsx
  ✓ Found 38 ISINs, Total: 100.12%
...
============================================================

Processing complete:
  ✓ Successfully processed: 22 files
  ✗ Failed: 0 files
  Total unique ISINs: 156

✓ Excel file saved: consolidated_portfolio_20260526_143022.xlsx
✓ CSV file saved: consolidated_portfolio_20260526_143022.csv

============================================================
SUMMARY
============================================================
Total Investment: ₹2,200,000.00
Unique ISINs: 156
Files processed: 22

Top 5 Holdings:
  INE002A01018: ₹145,320.00 (6.61%)
  INE040A01034: ₹132,150.00 (6.01%)
  INE062A01020: ₹128,740.00 (5.85%)
  ...

Done!
```

---

## Mstock Pending Alerts Parser

A utility to parse stock price alerts from mstock pending alerts export files and generate an organized Excel report.

### Overview

This tool reads a `mstock_pending_alerts.txt` file (exported from mstock mobile app), parses individual stock alert records, and exports key information to a formatted Excel workbook for easy review and tracking.

### Features

- **Automatic parsing**: Extracts stock symbols, notes, and alert trigger conditions
- **Handles optional notes**: Gracefully processes records with or without notes
- **Extracts trigger rules**: Captures price conditions (LTP >= price, LTP <= price)
- **Excel export**: Creates a professional formatted workbook with timestamp
- **Filters non-essential data**: Omits price data, day change %, and action buttons from output

### Usage

```bash
python mstock_alerts.py --input <file_path> --output <output_name>
```

### Examples

**Basic usage - parse the alerts file:**
```bash
python mstock_alerts.py --input mstock_pending_alerts.txt
```
If a relative filename is provided, the tool first looks in `docs/` by default.

**Custom output file name:**
```bash
python mstock_alerts.py --input mstock_pending_alerts.txt --output my_alerts
```

**With full path:**
```bash
python mstock_alerts.py -i "C:\Users\sachin_gupta\Downloads\mstock_pending_alerts.txt" -o "stock_alerts"
```

### Command-Line Arguments

| Argument | Short | Required | Default | Description |
|----------|-------|----------|---------|-------------|
| `--input` | `-i` | Yes | - | Input file path (absolute path used directly; relative path searched in `docs/` first) |
| `--output` | `-o` | No | `mstock_alerts` | Output file base name |

### Input File Format

The input file should be an export from the mstock mobile app containing pending price alerts. Each record includes:

- **Stock Name**: NSE stock symbol (e.g., NYKAA, RELIANCE)
- **Exchange**: NSE indicator
- **Note** (optional): User annotation (e.g., "bp", "buy", "review", "add", or blank)
- **Current Price**: Last traded price - *omitted from output*
- **Day Change**: Change and percentage since open - *omitted from output*
- **Trigger Rule**: Price condition (e.g., "LTP >= 300.00", "LTP <= 700.00")
- **Action buttons**: Open, Edit, Delete - *omitted from output*

### Output

The tool generates an Excel file with timestamp in the format: `{output_name}_{YYYYMMDD}.xlsx`

**Output Columns:**
1. **Stock Name** - NSE stock symbol
2. **Note** - User annotation (empty if not provided)
3. **Trigger Rule** - Price alert condition (e.g., "LTP >= 300.00")

**Example:**

| Stock Name | Note | Trigger Rule |
|-----------|------|--------------|
| NYKAA | bp | LTP >= 300.00 |
| JSWENERGY | bp | LTP >= 650.00 |
| TATACHEM | review | LTP <= 700.00 |
| SCHNEIDER | | LTP >= 1,400.00 |

**File Location**: Output file is saved in the same directory as the resolved input file

When using a relative input like `mstock_pending_alerts.txt`, the tool resolves it to `docs/mstock_pending_alerts.txt` (if present), so output is created in `docs/`.

### Workflow Example

```bash
# 1. Export pending alerts from mstock app to mstock_pending_alerts.txt
# 2. Run the parser
python mstock_alerts.py --input mstock_pending_alerts.txt

# 3. Review output
# File created: mstock_alerts_20260617.xlsx
# Records exported: 18

# 4. Open in Excel to review, sort, or analyze your alerts
```

---

## Troubleshooting

### "ISIN column not found"
- Check that your Excel file contains a column with "ISIN" in its name
- Verify the table format matches expected structure

### "No valid data found"
- Ensure your Excel file contains valid ISIN codes (12 alphanumeric characters)
- Check that percentage values are numeric

### "Percentages sum to X% (expected ~100%)"
- This is a warning when holdings don't sum to approximately 100%
- The tool will still process the file, but results may need verification

## Assumptions

- **Investment Model**: Each Excel file represents one ETF with a specified investment amount (default: ₹100,000)
- **ISIN Uniqueness**: Same ISIN appearing in multiple files represents the same security
- **Name Conflicts**: When an ISIN appears with different names, the first encountered name is used
- **Format Consistency**: All files contain tabular data with required columns

## Limitations

- Does not fetch real-time data or perform API calls
- Does not track historical changes across time periods
- Does not perform advanced portfolio analytics (risk metrics, correlations)
- Supports INR currency only
- Processes one folder at a time

## Project Structure

```
ExcelTool/
├── etf_aggregator.py          # Main script
├── requirements.txt            # Python dependencies
├── README.md                   # This file
├── IMPLEMENTATION_PLAN.md     # Detailed implementation plan
└── output/                     # Output files (created by script)
```

## License

This tool is provided as-is for personal use.

## Support

For issues or questions, refer to the IMPLEMENTATION_PLAN.md for detailed technical information.
