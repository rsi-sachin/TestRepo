"""Quick test to check if the fixed pattern matches"""
import sys
import os
from pathlib import Path
import re

# Set working directory
backend_dir = Path(__file__).parent.parent
os.chdir(backend_dir)
sys.path.insert(0, str(backend_dir))

from app.parsers.pdf_parser import PdfParser

print("Testing Pattern Matching...")

# Load PDF
pdf_path = Path(r"C:\TestRepo\ORAN\docs\ts_103989v040200p.pdf")
text = PdfParser.parse_file(pdf_path)

print(f"Document: {pdf_path.name}")
print(f"Length: {len(text):,} chars")
print()

# Test the fixed pattern
pattern = r"^\d+\.?\s*Test\s+Methodology"
print(f"Pattern: {pattern}")
print()

matches = list(re.finditer(pattern, text, re.MULTILINE | re.IGNORECASE))
print(f"Total matches: {len(matches)}")

if matches:
    print("\nFirst 5 matches:")
    for i, match in enumerate(matches[:5], 1):
        matched_text = match.group(0)
        context_start = max(0, match.start() - 20)
        context_end = min(len(text), match.end() + 80)
        context = text[context_start:context_end].replace('\n', ' ').strip()
        print(f"{i}. '{matched_text}'")
        print(f"   Context: ...{context}...")
        print()
else:
    print("\nSearching for partial matches...")
    # Test different variations
    variations = [
        r"\d+\s+Test\s+Methodology",  # No anchor
        r"Test\s+Methodology",        # Just the words
        r"\d+\s+Test",                # Just number + Test
        r"\d+\s+methodology",         # Lowercase
    ]
    for var in variations:
        matches_var = list(re.finditer(var, text, re.IGNORECASE))
        if matches_var:
            print(f"  ✓ Found {len(matches_var)} matches with: {var}")
            print(f"    Example: '{matches_var[0].group(0)}'")
        else:
            print(f"  ✗ No matches with: {var}")
