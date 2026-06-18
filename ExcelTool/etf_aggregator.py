"""
ETF Holdings Aggregator
Reads multiple ETF holdings Excel files and consolidates ISIN investments.
"""

import pandas as pd
import os
import sys
import argparse
from datetime import datetime
from pathlib import Path


class ETFAggregator:
    """Main class for processing and aggregating ETF holdings data"""
    
    # Column name variations for fuzzy matching
    ISIN_KEYWORDS = ['isin', 'isincode', 'isin code', 'isin no', 'isin_code']
    NAME_KEYWORDS = ['name', 'instrument', 'stock', 'script', 'company', 
                     'security', 'scrip', 'instrument name', 'stock name', 
                     'script name', 'company name', 'security name']
    PERCENTAGE_KEYWORDS = ['%', 'nav', 'weight', 'percentage', 'percent', 
                          '% of nav', 'nav %', '% weight', 'portfolio %',
                          'portfolio weight', 'allocation']
    
    def __init__(self, investment_per_etf=100000):
        """
        Initialize the aggregator
        
        Args:
            investment_per_etf: Investment amount per ETF file (default: 100,000)
        """
        self.investment_per_etf = investment_per_etf
        self.processed_files = []
        self.failed_files = []
        self.isin_data = {}  # {ISIN: {'name': str, 'investment': float, 'sources': [files]}}
        
    def detect_column(self, df, column_type):
        """
        Detect column by fuzzy matching column names
        
        Args:
            df: pandas DataFrame
            column_type: 'isin', 'name', or 'percentage'
            
        Returns:
            Column name or None if not found
        """
        if column_type == 'isin':
            keywords = self.ISIN_KEYWORDS
        elif column_type == 'name':
            keywords = self.NAME_KEYWORDS
        elif column_type == 'percentage':
            keywords = self.PERCENTAGE_KEYWORDS
        else:
            return None
        
        # Get column names and clean them
        columns = df.columns.tolist()
        
        for col in columns:
            # Skip pandas auto-generated unnamed columns (these are usually index/serial number columns)
            if str(col).startswith('Unnamed:'):
                continue
            
            col_clean = str(col).lower().strip()
            
            # Check for exact or partial matches
            for keyword in keywords:
                if keyword in col_clean:
                    return col
        
        return None
    
    def find_header_row(self, file_path, sheet_name=0):
        """
        Find the header row in Excel file (skip metadata rows)
        
        Args:
            file_path: Path to Excel file
            sheet_name: Sheet name or index
            
        Returns:
            Row index of header (0-based)
        """
        # Try reading first 20 rows
        df_preview = pd.read_excel(file_path, sheet_name=sheet_name, nrows=20, header=None)
        
        # Look for row containing ISIN keyword
        for idx, row in df_preview.iterrows():
            row_str = ' '.join([str(x).lower() for x in row if pd.notna(x)])
            if 'isin' in row_str:
                return idx
        
        # Default to first row if not found
        return 0
    
    def parse_percentage(self, value):
        """
        Parse percentage value from various formats
        
        Args:
            value: Value to parse (can be "5.25%", "5.25", 0.0525, etc.)
            
        Returns:
            Float percentage value or None if invalid
        """
        if pd.isna(value):
            return None
        
        try:
            # Convert to string and clean
            value_str = str(value).strip().replace('%', '').replace(',', '')
            
            # Convert to float
            pct = float(value_str)
            
            # If value is between 0 and 1, assume it's decimal format (0.0525 = 5.25%)
            if 0 < pct < 1:
                pct = pct * 100
            
            return pct
        except (ValueError, TypeError):
            return None
    
    def validate_isin(self, isin):
        """
        Validate ISIN format (basic check: 12 alphanumeric characters)
        
        Args:
            isin: ISIN string to validate
            
        Returns:
            True if valid format, False otherwise
        """
        if pd.isna(isin):
            return False
        
        isin_str = str(isin).strip()
        
        # ISIN should be 12 characters, alphanumeric
        if len(isin_str) == 12 and isin_str.isalnum():
            return True
        
        return False
    
    def extract_etf_name(self, file_path):
        """
        Extract ETF name from Excel file by searching for strings containing 'ETF'
        
        Args:
            file_path: Path to Excel file
            
        Returns:
            ETF name string (from file content or filename as fallback)
        """
        try:
            # Read first 25 rows without header to find ETF name in metadata
            df_preview = pd.read_excel(file_path, sheet_name=0, header=None, nrows=25)
            
            # Search for ETF names with priority: ending with 'ETF' first, then containing 'ETF'
            etf_ending = []
            etf_containing = []
            
            for idx, row in df_preview.iterrows():
                for cell_value in row:
                    if pd.notna(cell_value):
                        cell_str = str(cell_value).strip()
                        # Filter out very short strings (likely not ETF names)
                        if len(cell_str) > 5:
                            if cell_str.upper().endswith('ETF'):
                                etf_ending.append(cell_str)
                            elif 'ETF' in cell_str.upper():
                                etf_containing.append(cell_str)
            
            # Return first match with priority: ending with ETF first
            if etf_ending:
                return etf_ending[0]
            if etf_containing:
                return etf_containing[0]
            
            # Fallback: use filename without extension
            filename = os.path.basename(file_path)
            etf_name = os.path.splitext(filename)[0]  # Remove extension
            return etf_name
            
        except Exception as e:
            # On error, use filename as fallback
            filename = os.path.basename(file_path)
            return os.path.splitext(filename)[0]
    
    def read_excel_file(self, file_path):
        """
        Read single Excel file and extract ISIN data
        
        Args:
            file_path: Path to Excel file
            
        Returns:
            DataFrame with [ISIN, Name, Investment] columns or None if failed
        """
        try:
            print(f"Processing: {os.path.basename(file_path)}")
            
            # Find header row
            header_row = self.find_header_row(file_path)
            
            # Read Excel file
            df = pd.read_excel(file_path, sheet_name=0, header=header_row)
            
            # Detect columns
            isin_col = self.detect_column(df, 'isin')
            name_col = self.detect_column(df, 'name')
            pct_col = self.detect_column(df, 'percentage')
            
            if not isin_col:
                print(f"  ⚠️  Warning: ISIN column not found in {os.path.basename(file_path)}")
                return None
            
            if not pct_col:
                print(f"  ⚠️  Warning: Percentage column not found in {os.path.basename(file_path)}")
                return None
            
            if not name_col:
                print(f"  ⚠️  Warning: Name column not found in {os.path.basename(file_path)}")
                # Try to use ISIN as name if name column not found
                name_col = isin_col
            
            # Extract relevant columns
            result_df = pd.DataFrame()
            result_df['ISIN'] = df[isin_col]
            result_df['Name'] = df[name_col]
            result_df['Percentage'] = df[pct_col].apply(self.parse_percentage)
            
            # Filter valid rows
            result_df = result_df[result_df['ISIN'].apply(self.validate_isin)]
            result_df = result_df[result_df['Percentage'].notna()]
            result_df = result_df[result_df['Percentage'] > 0]
            
            if len(result_df) == 0:
                print(f"  ⚠️  Warning: No valid data found in {os.path.basename(file_path)}")
                return None
            
            # Calculate investments
            result_df['Investment'] = result_df['Percentage'] * self.investment_per_etf / 100
            
            # Validate percentages sum to approximately 100%
            total_pct = result_df['Percentage'].sum()
            if total_pct < 95 or total_pct > 105:
                print(f"  ⚠️  Warning: Percentages sum to {total_pct:.2f}% (expected ~100%)")
            
            print(f"  ✓ Found {len(result_df)} ISINs, Total: {total_pct:.2f}%")
            
            return result_df[['ISIN', 'Name', 'Investment']]
            
        except Exception as e:
            print(f"  ✗ Error reading {os.path.basename(file_path)}: {str(e)}")
            return None
    
    def aggregate_data(self, input_folder):
        """
        Process all Excel files in folder and aggregate investments
        
        Args:
            input_folder: Path to folder containing Excel files
        """
        # Get all Excel files
        excel_files = []
        for ext in ['*.xlsx', '*.xls', '*.xlsm']:
            excel_files.extend(Path(input_folder).glob(ext))
        
        if len(excel_files) == 0:
            print(f"No Excel files found in {input_folder}")
            return
        
        print(f"\nFound {len(excel_files)} Excel file(s)")
        print("=" * 60)
        
        # Process each file
        for file_path in excel_files:
            # Extract ETF name before processing data
            etf_name = self.extract_etf_name(str(file_path))
            
            df = self.read_excel_file(str(file_path))
            
            if df is not None:
                self.processed_files.append(os.path.basename(str(file_path)))
                
                # Aggregate data
                for _, row in df.iterrows():
                    isin = row['ISIN']
                    name = row['Name']
                    investment = row['Investment']
                    
                    if isin in self.isin_data:
                        # ISIN already exists, add investment
                        self.isin_data[isin]['investment'] += investment
                        # Store tuple of (file_path, etf_name)
                        self.isin_data[isin]['sources'].append((str(file_path.absolute()), etf_name))
                        
                        # Update name if current one is empty and new one is not
                        current_name = str(self.isin_data[isin]['name']).strip()
                        new_name = str(name).strip()
                        if (not current_name or current_name == 'nan') and new_name and new_name != 'nan':
                            self.isin_data[isin]['name'] = name
                    else:
                        # New ISIN
                        self.isin_data[isin] = {
                            'name': name,
                            'investment': investment,
                            # Store tuple of (file_path, etf_name)
                            'sources': [(str(file_path.absolute()), etf_name)]
                        }
            else:
                self.failed_files.append(os.path.basename(str(file_path)))
        
        print("=" * 60)
        print(f"\nProcessing complete:")
        print(f"  ✓ Successfully processed: {len(self.processed_files)} files")
        print(f"  ✗ Failed: {len(self.failed_files)} files")
        print(f"  Total unique ISINs: {len(self.isin_data)}")
    
    def generate_output(self, output_path):
        """
        Generate Excel and CSV output files
        
        Args:
            output_path: Base output path (without extension)
        """
        if len(self.isin_data) == 0:
            print("\nNo data to export")
            return
        
        # Calculate max number of ETFs any ISIN belongs to
        max_etf_count = max(len(data['sources']) for data in self.isin_data.values())
        
        # Create DataFrame
        output_data = []
        for isin, data in self.isin_data.items():
            row_data = {
                'ISIN': isin,
                'Instrument Name': data['name'],
                'Total Investment (₹)': data['investment']
            }
            
            # Add ETF columns (ETF-1, ETF-2, etc.)
            for i in range(max_etf_count):
                if i < len(data['sources']):
                    # Extract ETF name from tuple (file_path, etf_name)
                    etf_name = data['sources'][i][1]
                    row_data[f'ETF-{i+1}'] = etf_name
                else:
                    row_data[f'ETF-{i+1}'] = ''
            
            output_data.append(row_data)
        
        df = pd.DataFrame(output_data)
        
        # Sort by investment amount (descending)
        df = df.sort_values('Total Investment (₹)', ascending=False)
        
        # Calculate total and percentage
        total_investment = df['Total Investment (₹)'].sum()
        df['% of Portfolio'] = (df['Total Investment (₹)'] / total_investment * 100).round(2)
        
        # Add sum row
        sum_row_data = {
            'ISIN': 'TOTAL',
            'Instrument Name': '',
            'Total Investment (₹)': total_investment,
            '% of Portfolio': 100.0
        }
        # Add empty ETF columns for sum row
        for i in range(max_etf_count):
            sum_row_data[f'ETF-{i+1}'] = ''
        
        sum_row = pd.DataFrame([sum_row_data])
        
        df_with_total = pd.concat([df, sum_row], ignore_index=True)
        
        # Generate output files
        excel_path = f"{output_path}.xlsx"
        csv_path = f"{output_path}.csv"
        
        # Export to Excel with formatting
        try:
            with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
                # Write main consolidated portfolio sheet
                df_with_total.to_excel(writer, sheet_name='Consolidated Portfolio', index=False)
                
                # Get workbook and worksheet
                workbook = writer.book
                worksheet = writer.sheets['Consolidated Portfolio']
                
                # Format headers (bold)
                for cell in worksheet[1]:
                    cell.font = cell.font.copy(bold=True)
                
                # Auto-adjust column widths
                for column in worksheet.columns:
                    max_length = 0
                    column_letter = column[0].column_letter
                    for cell in column:
                        try:
                            if len(str(cell.value)) > max_length:
                                max_length = len(str(cell.value))
                        except:
                            pass
                    adjusted_width = min(max_length + 2, 50)
                    worksheet.column_dimensions[column_letter].width = adjusted_width
                
                # Format numbers
                from openpyxl.styles import numbers
                # Percentage column is after ISIN, Name, Investment, and all ETF columns
                # Column order: A=ISIN, B=Name, C=Investment, D...=ETF-1 to ETF-N, Last='% of Portfolio'
                percentage_col_index = 4 + max_etf_count  # 1(ISIN) + 1(Name) + 1(Investment) + 1(first ETF column) + (max_etf_count-1)
                from openpyxl.utils import get_column_letter
                percentage_col_letter = get_column_letter(percentage_col_index)
                
                for row in range(2, len(df_with_total) + 2):
                    # Investment column (C)
                    worksheet[f'C{row}'].number_format = '#,##0.00'
                    # Percentage column (dynamic based on ETF count)
                    worksheet[f'{percentage_col_letter}{row}'].number_format = '0.00'
                
                # Bold the total row
                total_row = len(df_with_total) + 1
                for cell in worksheet[total_row]:
                    cell.font = cell.font.copy(bold=True)
                
                # Create Missing Names worksheet
                missing_names_data = []
                for isin, data in self.isin_data.items():
                    name_str = str(data['name']).strip()
                    if not name_str or name_str == 'nan' or name_str == '':
                        # Extract file path from tuple (file_path, etf_name)
                        first_source = data['sources'][0][0] if data['sources'] else 'Unknown'
                        missing_names_data.append({
                            'ISIN': isin,
                            'Total Investment (₹)': data['investment'],
                            'First Source File': first_source
                        })
                
                if missing_names_data:
                    df_missing = pd.DataFrame(missing_names_data)
                    df_missing = df_missing.sort_values('Total Investment (₹)', ascending=False)
                    df_missing.to_excel(writer, sheet_name='ISINs Missing Names', index=False)
                    
                    # Format the missing names worksheet
                    ws_missing = writer.sheets['ISINs Missing Names']
                    
                    # Bold headers
                    for cell in ws_missing[1]:
                        cell.font = cell.font.copy(bold=True)
                    
                    # Auto-adjust column widths
                    for column in ws_missing.columns:
                        max_length = 0
                        column_letter = column[0].column_letter
                        for cell in column:
                            try:
                                if len(str(cell.value)) > max_length:
                                    max_length = len(str(cell.value))
                            except:
                                pass
                        adjusted_width = min(max_length + 2, 50)
                        ws_missing.column_dimensions[column_letter].width = adjusted_width
                    
                    # Format investment column
                    for row in range(2, len(df_missing) + 2):
                        ws_missing[f'B{row}'].number_format = '#,##0.00'
                    
                    print(f"  → Added 'ISINs Missing Names' sheet with {len(missing_names_data)} entries")
            
            print(f"\n✓ Excel file saved: {excel_path}")
        except Exception as e:
            print(f"\n✗ Error saving Excel file: {str(e)}")
        
        # Export to CSV
        try:
            df_with_total.to_csv(csv_path, index=False)
            print(f"✓ CSV file saved: {csv_path}")
        except Exception as e:
            print(f"✗ Error saving CSV file: {str(e)}")
        
        # Print summary
        print("\n" + "=" * 60)
        print("SUMMARY")
        print("=" * 60)
        print(f"Total Investment: ₹{total_investment:,.2f}")
        print(f"Unique ISINs: {len(self.isin_data)}")
        print(f"Files processed: {len(self.processed_files)}")
        print(f"\nTop 5 Holdings:")
        for idx, row in df.head(5).iterrows():
            print(f"  {row['ISIN']}: ₹{row['Total Investment (₹)']:,.2f} ({row['% of Portfolio']:.2f}%)")


def main():
    """Main function to orchestrate the ETF aggregation process"""
    
    parser = argparse.ArgumentParser(
        description='ETF Holdings Aggregator - Consolidate ISIN investments across multiple ETF holdings files',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python etf_aggregator.py --input "April" --output "consolidated_portfolio"
  python etf_aggregator.py -i "C:/Data/ETFs" -o "output/portfolio" --investment 50000
        """
    )
    
    parser.add_argument(
        '--input', '-i',
        required=True,
        help='Input folder containing Excel files'
    )
    
    parser.add_argument(
        '--output', '-o',
        default='consolidated_portfolio',
        help='Output file base name (default: consolidated_portfolio)'
    )
    
    parser.add_argument(
        '--investment',
        type=float,
        default=100000,
        help='Investment amount per ETF file (default: 100000)'
    )
    
    args = parser.parse_args()
    
    # Validate input folder
    if not os.path.exists(args.input):
        print(f"Error: Input folder '{args.input}' does not exist")
        sys.exit(1)
    
    if not os.path.isdir(args.input):
        print(f"Error: '{args.input}' is not a directory")
        sys.exit(1)
    
    # Add timestamp to output filename
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_path = f"{args.output}_{timestamp}"
    
    # Create aggregator and process
    print("ETF Holdings Aggregator")
    print("=" * 60)
    print(f"Input folder: {args.input}")
    print(f"Investment per ETF: ₹{args.investment:,.2f}")
    print(f"Output base name: {args.output}")
    
    aggregator = ETFAggregator(investment_per_etf=args.investment)
    aggregator.aggregate_data(args.input)
    aggregator.generate_output(output_path)
    
    print("\nDone!")


if __name__ == '__main__':
    main()
