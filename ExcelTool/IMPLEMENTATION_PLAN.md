# ETF Holdings Aggregator - Implementation Plan

## Overview
Create a Python tool that reads multiple ETF holdings Excel files, extracts ISIN, instrument names, and % of NAV data, assumes ₹100,000 investment per ETF, aggregates investments across all ISINs, and outputs a consolidated Excel/CSV report with total investments and portfolio percentages.

## Requirements

### Input
- Multiple Excel files (.xlsx) containing ETF holdings
- Each file contains a table with columns:
  - ISIN (or variations: ISIN Code, ISINCode, etc.)
  - Instrument Name (or: Stock Name, Script Name, Company Name)
  - % of NAV (or: %, Percentage, Weight, % Weight)

### Processing
- Assume ₹100,000 investment per ETF file
- Calculate investment per ISIN: (% of NAV / 100) × 100,000
- Aggregate investments across all files for each unique ISIN

### Output
- Consolidated Excel (.xlsx) and CSV files with:
  - Column 1: ISIN
  - Column 2: Instrument Name
  - Column 3: Total Investment (₹)
  - Column 4: % of Portfolio
  - Sum row at bottom showing totals

## Implementation Steps

### Phase 1: Setup and Dependencies
1. **Install required Python libraries**
   ```bash
   pip install pandas openpyxl xlrd
   ```
   - pandas: Data manipulation and Excel I/O
   - openpyxl: Reading .xlsx files
   - xlrd: Reading older .xls files

### Phase 2: Core Implementation

2. **Create main script structure** (`etf_aggregator.py`)
   - Main orchestration function
   - Command-line argument parsing
   - Configuration management

3. **Implement column detection**
   - Fuzzy matching for column identification
   - ISIN variations: 'ISIN', 'ISIN Code', 'ISINCode', 'ISIN No'
   - Name variations: 'Name', 'Instrument Name', 'Stock Name', 'Script Name', 'Company Name'
   - Percentage variations: '% of NAV', '%', 'Percentage', 'Weight', '% Weight', 'NAV %'
   - Case-insensitive matching with keyword search

4. **Implement Excel file reader**
   - Read Excel files using pandas
   - Auto-detect header row (skip metadata rows)
   - Extract table data using detected columns
   - Handle merged cells and formatting issues
   - Skip empty rows and non-table data
   - Support multiple sheets (default: first sheet)

5. **Implement investment calculation**
   - Parse percentage values (handle formats: "5.25%", "5.25", "0.0525")
   - Calculate: investment = (% / 100) × 100,000 for each ISIN
   - Validate percentages sum to ~100% per file (tolerance: ±5%)
   - Handle edge cases (missing values, invalid formats)

6. **Implement aggregation logic**
   - Collect all ISINs across files
   - Sum investments for each unique ISIN
   - Use first encountered name for each ISIN
   - Track source files for each ISIN

### Phase 3: Output Generation

7. **Calculate portfolio statistics**
   - Sum total investment across all ISINs
   - Calculate % of portfolio: (ISIN investment / total) × 100
   - Verify percentages sum to 100%

8. **Generate output files**
   - Create Excel file with formatting:
     - Headers: ISIN | Instrument Name | Total Investment (₹) | % of Portfolio
     - Data rows for each ISIN
     - Sum row at bottom
     - Apply number formatting (currency, percentage)
     - Auto-adjust column widths
   - Export CSV file with same data
   - Naming convention: `consolidated_portfolio_YYYYMMDD.xlsx/csv`

### Phase 4: Error Handling and Validation

9. **Add error handling**
   - Try-catch for file reading errors
   - Handle missing/undetectable columns
   - Validate ISIN format (12 alphanumeric characters)
   - Handle missing or invalid percentage data
   - Gracefully skip problematic files with warnings

10. **Add logging and reporting**
    - Print progress for each file processed
    - Summary report:
      - Total files processed
      - Files skipped/failed
      - Total ISINs found
      - Total investment amount
    - Warnings for ISINs with multiple names
    - Validation warnings (percentage sums, format issues)

## Technical Design

### Main Functions

```python
def detect_columns(df, column_type):
    """
    Detect column index by fuzzy matching column names
    Args:
        df: pandas DataFrame
        column_type: 'isin', 'name', or 'percentage'
    Returns:
        Column index or None if not found
    """

def read_excel_file(file_path, investment_amount=100000):
    """
    Read single Excel file and extract ISIN data
    Args:
        file_path: Path to Excel file
        investment_amount: Investment amount for this ETF
    Returns:
        DataFrame with [ISIN, Name, Investment] columns
    """

def calculate_investments(df, percentage_col, investment_amount):
    """
    Calculate investment amounts from percentages
    Args:
        df: DataFrame with percentage column
        percentage_col: Column index for percentages
        investment_amount: Total investment amount
    Returns:
        Series with investment amounts
    """

def aggregate_data(file_list, input_folder, investment_per_etf=100000):
    """
    Process all files and aggregate investments
    Args:
        file_list: List of Excel file paths
        input_folder: Base folder path
        investment_per_etf: Investment amount per ETF
    Returns:
        Aggregated DataFrame with totals
    """

def generate_output(df, output_path):
    """
    Generate Excel and CSV output files
    Args:
        df: Aggregated data
        output_path: Base output path (without extension)
    """

def main():
    """
    Main orchestration function
    Parse arguments, process files, generate output
    """
```

### Command-Line Interface

```bash
python etf_aggregator.py --input <folder_path> --output <output_base_name> [--investment <amount>]

Options:
  --input, -i       Input folder containing Excel files (required)
  --output, -o      Output file base name (default: consolidated_portfolio)
  --investment      Investment amount per ETF (default: 100000)
  --sheet          Sheet name/index to read (default: 0 = first sheet)
  --help, -h       Show help message
```

## Verification Plan

### 1. Unit Testing
- Test column detection with various column name formats
- Test percentage parsing (%, decimal, text formats)
- Test ISIN validation
- Test aggregation logic with mock data

### 2. Integration Testing
- Run on April folder with 22 Excel files
- Verify output file structure
- Check sum row calculations
- Verify percentages sum to 100%

### 3. Manual Validation
- Spot check 3-5 ISINs manually:
  - Open source Excel files
  - Manually calculate expected investment
  - Compare with tool output
- Verify ISINs appearing in multiple files are correctly summed

### 4. Edge Case Testing
- Files with different layouts
- Files with merged cells
- Files with metadata rows before table
- Missing columns
- Invalid percentage values
- Empty files

## Key Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Investment model | ₹100,000 per Excel file | Each file represents one ETF portfolio |
| Column matching | Fuzzy/keyword matching | Handle varying Excel formats automatically |
| ISIN name conflicts | Use first encountered | Simple, deterministic approach |
| Output formats | Both Excel and CSV | Flexibility for different use cases |
| File selection | All .xlsx files in folder | Process complete folder automatically |
| Error handling | Skip problematic files | Continue processing despite individual failures |

## Out of Scope

- Real-time data fetching or API integration
- Historical tracking across multiple time periods
- Advanced portfolio analytics (Sharpe ratio, correlations, sector analysis)
- Multi-currency support (all in INR)
- Database storage
- Web interface or GUI

## Dependencies

- Python 3.7+
- pandas >= 1.0
- openpyxl >= 3.0
- xlrd >= 2.0 (for .xls support)

## File Structure

```
ExcelTool/
├── etf_aggregator.py          # Main script
├── requirements.txt            # Python dependencies
├── README.md                   # User documentation
├── test/                       # Test files (optional)
│   ├── test_column_detection.py
│   └── test_aggregation.py
└── output/                     # Output directory (created by script)
    ├── consolidated_portfolio.xlsx
    └── consolidated_portfolio.csv
```

## Next Steps

1. Install dependencies: `pip install pandas openpyxl xlrd`
2. Implement `etf_aggregator.py` following the technical design
3. Test with sample files from April folder
4. Validate output and refine column detection if needed
5. Document usage in README.md
6. Package for easy distribution
