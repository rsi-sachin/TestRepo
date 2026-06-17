"""
Mstock Pending Alerts Parser

Reads mstock_pending_alerts.txt and exports stock alert records to Excel.
Extracts: Stock Name, Note, and Trigger Rule (LTP condition).
"""

import argparse
import re
from datetime import datetime
from pathlib import Path
from typing import List, Dict

from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment


def resolve_input_path(input_arg: str) -> Path:
    """
    Resolve input path.

    If an absolute path is provided, use it as-is.
    If a relative path is provided, first try workspace/docs, then current directory.
    """
    input_path = Path(input_arg)
    if input_path.is_absolute():
        return input_path

    script_dir = Path(__file__).resolve().parent
    docs_candidate = script_dir / "docs" / input_path
    if docs_candidate.exists():
        return docs_candidate

    return input_path


class MstockAlertsParser:
    """Parser for mstock pending alerts text file."""

    def __init__(self, file_path: str):
        """Initialize parser with input file path."""
        self.file_path = Path(file_path)
        if not self.file_path.exists():
            raise FileNotFoundError(f"Input file not found: {file_path}")

    def parse(self) -> List[Dict[str, str]]:
        """
        Parse the mstock_pending_alerts.txt file.
        
        Returns:
            List of dicts with keys: stock_name, note, trigger_rule
        """
        with open(self.file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        alerts = []
        i = 0

        while i < len(lines):
            line = lines[i].strip()

            # Skip empty lines
            if not line:
                i += 1
                continue

            # Check if this is the start of a new record (stock symbol)
            # Stock symbol is a line that's not "NSE" and not a number/price pattern
            if self._is_stock_symbol(line):
                stock_name = line
                note = ""
                trigger_rule = ""

                # Process the record (typically 9-10 lines per record)
                i += 1
                record_start = i

                # Expected: NSE on next line
                if i < len(lines) and lines[i].strip() == "NSE":
                    i += 1

                    # Next line should have Note or be empty/whitespace
                    if i < len(lines):
                        note_line = lines[i].rstrip()
                        if note_line.startswith("Note:"):
                            # Extract note text after "Note: "
                            note = note_line.replace("Note:", "").strip()
                        i += 1

                    # Skip empty line
                    if i < len(lines) and not lines[i].strip():
                        i += 1

                    # Skip LTP price line (decimal number)
                    if i < len(lines):
                        i += 1

                    # Skip day change line (e.g., "7.00 (2.57%)")
                    if i < len(lines):
                        i += 1

                    # Skip empty line
                    if i < len(lines) and not lines[i].strip():
                        i += 1

                    # Extract trigger rule from line with "LTP >= " or "LTP <= "
                    if i < len(lines):
                        trigger_line = lines[i].rstrip()
                        trigger_rule = self._extract_trigger_rule(trigger_line)
                        i += 1

                    # Skip "delete" line or other action lines
                    if i < len(lines) and "delete" in lines[i].lower():
                        i += 1

                    # Create alert record
                    alerts.append({
                        "stock_name": stock_name,
                        "note": note,
                        "trigger_rule": trigger_rule,
                    })
                else:
                    # Malformed record, skip
                    i = record_start + 8  # Skip expected record size

            else:
                i += 1

        return alerts

    @staticmethod
    def _is_stock_symbol(text: str) -> bool:
        """
        Check if text appears to be a stock symbol (not NSE, not a number, etc.).
        
        Args:
            text: Line text to check
            
        Returns:
            True if likely a stock symbol, False otherwise
        """
        # Exclude common non-symbol patterns
        if text in ("NSE", "Open", "edit", "delete"):
            return False

        # Stock symbols are typically uppercase letters/digits, no spaces
        if re.match(r"^[A-Z][A-Z0-9]{1,20}$", text):
            return True

        return False

    @staticmethod
    def _extract_trigger_rule(line: str) -> str:
        """
        Extract trigger rule (LTP >= price or LTP <= price) from line.
        
        Args:
            line: Line potentially containing trigger rule and actions
            
        Returns:
            Trigger rule string (e.g., "LTP >= 300.00"), empty if not found
        """
        # Match pattern: LTP >= or <= followed by price
        match = re.search(r"LTP\s*(?:>=|<=)\s*[\d,]+\.?\d*", line)
        if match:
            return match.group(0).strip()
        return ""


class ExcelExporter:
    """Export alerts to Excel workbook."""

    def __init__(self, output_path: str, worksheet_name: str = "Mstock Alerts"):
        """
        Initialize exporter.
        
        Args:
            output_path: Path to output Excel file
            worksheet_name: Name for the worksheet
        """
        self.output_path = Path(output_path)
        self.worksheet_name = worksheet_name

    def export(self, alerts: List[Dict[str, str]]) -> None:
        """
        Export alerts to Excel workbook.
        
        Args:
            alerts: List of alert dictionaries
        """
        # Create workbook and worksheet
        wb = Workbook()
        ws = wb.active
        ws.title = self.worksheet_name

        # Define headers
        headers = ["Stock Name", "Note", "Trigger Rule"]
        ws.append(headers)

        # Format header row
        header_fill = PatternFill(start_color="D3D3D3", end_color="D3D3D3", fill_type="solid")
        header_font = Font(bold=True)

        for cell in ws[1]:
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = Alignment(horizontal="center", vertical="center")

        # Add data rows
        for alert in alerts:
            ws.append([
                alert.get("stock_name", ""),
                alert.get("note", ""),
                alert.get("trigger_rule", ""),
            ])

        # Auto-adjust column widths
        ws.column_dimensions["A"].width = 20
        ws.column_dimensions["B"].width = 25
        ws.column_dimensions["C"].width = 25

        # Center-align all data cells
        for row in ws.iter_rows(min_row=2, max_row=ws.max_row):
            for cell in row:
                cell.alignment = Alignment(horizontal="left", vertical="center")

        # Save workbook
        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        wb.save(self.output_path)
        print(f"✓ Excel file created: {self.output_path}")
        print(f"  Records exported: {len(alerts)}")


def main():
    """Main entry point for CLI."""
    parser = argparse.ArgumentParser(
        description="Parse mstock pending alerts and export to Excel",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python mstock_alerts.py --input mstock_pending_alerts.txt
  python mstock_alerts.py -i mstock_pending_alerts.txt -o my_alerts
  python mstock_alerts.py --input "c:\\path\\to\\alerts.txt" --output "alerts_export"
        """,
    )

    parser.add_argument(
        "--input",
        "-i",
        required=True,
        help="Path to mstock_pending_alerts.txt file",
    )
    parser.add_argument(
        "--output",
        "-o",
        default="mstock_alerts",
        help='Output file base name (default: "mstock_alerts")',
    )

    args = parser.parse_args()

    try:
        resolved_input_path = resolve_input_path(args.input)

        # Parse input file
        print(f"Reading: {resolved_input_path}")
        alert_parser = MstockAlertsParser(str(resolved_input_path))
        alerts = alert_parser.parse()

        if not alerts:
            print("⚠ No alerts found in input file.")
            return

        print(f"✓ Parsed {len(alerts)} alert records")

        # Generate output filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d")
        output_filename = f"{args.output}_{timestamp}.xlsx"
        
        # Determine output directory (same as input file)
        output_path = resolved_input_path.parent / output_filename

        # Export to Excel
        print(f"Writing to: {output_path}")
        exporter = ExcelExporter(str(output_path))
        exporter.export(alerts)

        print("✓ Done!")

    except FileNotFoundError as e:
        print(f"✗ Error: {e}")
        exit(1)
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        exit(1)


if __name__ == "__main__":
    main()
