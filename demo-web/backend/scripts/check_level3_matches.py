"""Check what Level 3 is matching"""
import sys
import os
from pathlib import Path
import re

# Set working directory
backend_dir = Path(__file__).parent.parent
os.chdir(backend_dir)
sys.path.insert(0, str(backend_dir))

from app.parsers.pdf_parser import PdfParser

print("Checking Level 3 Pattern Matches...")

# Load PDF
pdf_path = Path(r"C:\TestRepo\ORAN\docs\ts_103989v040200p.pdf")
text = PdfParser.parse_file(pdf_path)

print(f"Document: {pdf_path.name}")
print(f"Length: {len(text):,} chars")
print()

# Test Level 3 pattern
pattern = r"^\d+\.\d+\s*.*Test\s+[Cc]ases"
print(f"Pattern: {pattern}")
print()

matches = list(re.finditer(pattern, text, re.MULTILINE | re.IGNORECASE))
print(f"Total matches: {len(matches)}")
print()

if matches:
    print("First 15 matches:")
    for i, match in enumerate(matches[:15], 1):
        matched_text = match.group(0)[:100]  # Truncate long matches
        print(f"{i}. '{matched_text}'")

print("\n\nTesting more specific pattern:")
specific_pattern = r"^\d+\.\d+\s+(?:Conformance\s+)?[Tt]est\s+[Cc]ases"
specific_matches = list(re.finditer(specific_pattern, text, re.MULTILINE))
print(f"Pattern: {specific_pattern}")
print(f"Matches: {len(specific_matches)}")

if specific_matches:
    print("\nMatches:")
    for i, match in enumerate(specific_matches[:10], 1):
        print(f"{i}. '{match.group(0)}'")
