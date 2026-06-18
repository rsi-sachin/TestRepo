"""
Quick test of Phase 2 parsing implementation
Tests PDF parsing with real ETSI specifications
"""

import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from app.parsers.pdf_parser import PdfParser
from app.parsers.test_clause_extractor import TestClauseExtractor
from app.models.oran import SpecType

def test_pdf_parsing():
    print("="*60)
    print("Testing Phase 2 - ETSI Spec Parsing")
    print("="*60)
    
    # Path to TS 103 989
    pdf_path = Path("../../ORAN/docs/ts_103989v040200p.pdf")
    
    if not pdf_path.exists():
        print(f"❌ PDF not found: {pdf_path}")
        return
    
    print(f"\n📄 Testing with: {pdf_path.name}")
    
    # Test 1: PDF Parser
    print("\n--- Test 1: PDF Parser ---")
    try:
        parser = PdfParser()
        page_count = parser.get_page_count(pdf_path)
        print(f"✅ Page count: {page_count}")
        
        # Extract first 3 pages
        text = parser.extract_page_range(pdf_path, 1, 3)
        print(f"✅ Extracted {len(text)} characters from pages 1-3")
        print(f"\nFirst 500 characters:")
        print(text[:500])
        
    except Exception as e:
        print(f"❌ PDF parser error: {e}")
        return
    
    # Test 2: Test Clause Extractor
    print("\n--- Test 2: Clause Extraction ---")
    try:
        # Extract full text
        full_text = parser.parse_file(pdf_path)
        print(f"✅ Full text extracted: {len(full_text)} characters")
        
        # Extract test clauses
        extractor = TestClauseExtractor()
        clauses = extractor.extract_clauses(full_text, SpecType.TS_103_989)
        print(f"✅ Extracted {len(clauses)} test clauses")
        
        # Show first 3 clauses
        print(f"\nFirst 3 test clauses:")
        for i, clause in enumerate(clauses[:3], 1):
            print(f"\n{i}. Section {clause.clause_number}: {clause.title}")
            print(f"   Page: {clause.page_number}")
            print(f"   Description: {clause.description[:100]}...")
            
    except Exception as e:
        print(f"❌ Clause extraction error: {e}")
        import traceback
        traceback.print_exc()
        return
    
    print("\n" + "="*60)
    print("✅ Phase 2 parsing test PASSED")
    print("="*60)

if __name__ == "__main__":
    test_pdf_parsing()
