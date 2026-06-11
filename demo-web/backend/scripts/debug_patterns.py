"""Debug script to test rule patterns against actual document text"""
import sys
import re
import os
from pathlib import Path

# Change to backend directory for correct relative paths
backend_dir = Path(__file__).parent.parent
os.chdir(backend_dir)
print(f'Working directory: {os.getcwd()}')
print()

sys.path.insert(0, str(backend_dir))

from app.parsers.pdf_parser import PdfParser
from app.repositories.rule_pack_repository import RulePackRepository

# Parse document
pdf_parser = PdfParser()
pdf_path = Path(r'C:\TestRepo\ORAN\docs\ts_103989v040200p.pdf')
print(f'Parsing {pdf_path.name}...')
text = pdf_parser.parse_file(pdf_path)
print(f'Extracted {len(text)} characters')
print()

# Load rule pack
repo = RulePackRepository()
packs = repo.list_rule_packs()
print(f'Rule packs: {len(packs)}')
if not packs:
    print('No rule packs found!')
    sys.exit(1)

pack = repo.load_rule_pack(packs[0].id)
print(f'Using: {pack.name}')
print()

# Test each rule pattern
for rule in pack.extraction_rules:
    pattern = rule.pattern
    if not pattern:
        print(f'Level {rule.level} ({rule.level_name}): No pattern!')
        continue
    
    print(f'Level {rule.level} ({rule.level_name}):')
    print(f'  Method: {rule.extraction_method}')
    print(f'  Pattern: {repr(pattern)}')
    
    try:
        matches = list(re.finditer(pattern, text, re.MULTILINE | re.IGNORECASE))
        print(f'  Matches: {len(matches)}')
        for m in matches[:5]:
            snippet = m.group(0)[:80].replace('\n', '\\n')
            print(f'    -> {repr(snippet)}')
    except re.error as e:
        print(f'  ERROR: Invalid regex: {e}')
    
    # Test keyword scan
    if rule.keywords:
        print(f'  Keywords (first 3): {rule.keywords[:3]}')
        for kw in rule.keywords[:3]:
            count = text.lower().count(kw.lower())
            print(f'    "{kw}": {count} occurrences')
    
    print()
