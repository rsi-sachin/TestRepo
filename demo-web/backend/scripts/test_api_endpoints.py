"""
Test script for new rule-based API endpoints

Tests the following endpoints:
- GET /api/oran/rules - List rule packs
- GET /api/oran/rules/{id} - Get rule pack details
- POST /api/oran/hierarchy/extract - Extract hierarchy
- GET /api/oran/hierarchy/{hash} - Get cached hierarchy
"""

import requests
import json
from pathlib import Path

BASE_URL = "http://localhost:8000/api/oran"

def test_list_rule_packs():
    """Test listing rule packs"""
    print("\n" + "="*80)
    print("TEST 1: List Rule Packs")
    print("="*80)
    
    response = requests.get(f"{BASE_URL}/rules")
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        rule_packs = response.json()
        print(f"Found {len(rule_packs)} rule packs:")
        for pack in rule_packs:
            print(f"  - {pack['name']} (ID: {pack['id']})")
            print(f"    Type: {pack['document_type']}")
            print(f"    Success: {pack['success_count']}, Failure: {pack['failure_count']}")
            print(f"    Avg Quality: {pack['avg_quality_score']:.2f}")
        return rule_packs
    else:
        print(f"Error: {response.text}")
        return []


def test_get_rule_pack(rule_pack_id):
    """Test getting specific rule pack"""
    print("\n" + "="*80)
    print(f"TEST 2: Get Rule Pack Details")
    print("="*80)
    
    response = requests.get(f"{BASE_URL}/rules/{rule_pack_id}")
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        pack = response.json()
        print(f"Name: {pack['name']}")
        print(f"Document Type: {pack['document_type']}")
        print(f"Max Depth: {pack['hierarchy_config']['max_depth']}")
        print(f"Levels:")
        for level, name in sorted(pack['hierarchy_config']['level_definitions'].items()):
            print(f"  Level {level}: {name}")
        print(f"Extraction Rules: {len(pack['extraction_rules'])}")
        for rule in pack['extraction_rules']:
            print(f"  - Level {rule['level']} ({rule['level_name']}): {rule['extraction_method']}")
        return pack
    else:
        print(f"Error: {response.text}")
        return None


def test_extract_hierarchy():
    """Test extracting hierarchy"""
    print("\n" + "="*80)
    print("TEST 3: Extract Hierarchy")
    print("="*80)
    
    payload = {
        "spec_type": "TS_103_989",
        "use_rules": True
    }
    
    response = requests.post(f"{BASE_URL}/hierarchy/extract", json=payload)
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"Spec Type: {result['spec_type']}")
        print(f"Extraction Method: {result['extraction_method']}")
        print(f"Quality Score: {result['quality_score']:.2f}")
        print(f"Total Nodes: {result['total_nodes']}")
        print(f"Max Depth: {result['max_depth']}")
        print(f"Avg Confidence: {result['avg_confidence']:.2f}")
        print(f"Fallback Used: {result['fallback_used']}")
        print(f"Document Hash: {result['document_hash']}")
        
        # Show hierarchy summary
        if result.get('hierarchy_tree'):
            tree = result['hierarchy_tree']
            print(f"\nHierarchy Structure:")
            print(f"  Root Nodes: {len(tree['root_nodes'])}")
            for root in tree['root_nodes'][:3]:  # Show first 3
                print(f"    - {root['section_number']} {root['title']}")
                print(f"      Children: {root['child_count']}")
        
        return result
    else:
        print(f"Error: {response.text}")
        return None


def test_get_cached_hierarchy(document_hash):
    """Test retrieving cached hierarchy"""
    print("\n" + "="*80)
    print("TEST 4: Get Cached Hierarchy")
    print("="*80)
    
    response = requests.get(f"{BASE_URL}/hierarchy/{document_hash}")
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        tree = response.json()
        print(f"Document: {tree['document_name']}")
        print(f"Total Nodes: {tree['total_nodes']}")
        print(f"Max Depth: {tree['max_depth']}")
        print(f"Avg Confidence: {tree['avg_confidence']:.2f}")
        return tree
    else:
        print(f"Error: {response.text}")
        return None


def main():
    """Run all tests"""
    print("\n" + "="*80)
    print("TESTING RULE-BASED API ENDPOINTS")
    print("="*80)
    print("\nNOTE: Make sure the backend server is running!")
    print("Run: cd demo-web/backend && uvicorn app.main:app --reload")
    print("\nPress Enter to continue...")
    input()
    
    # Test 1: List rule packs
    rule_packs = test_list_rule_packs()
    
    if not rule_packs:
        print("\nNo rule packs found. Please run the baseline generation script first.")
        return
    
    # Test 2: Get details of first rule pack
    first_pack = rule_packs[0]
    test_get_rule_pack(first_pack['id'])
    
    # Test 3: Extract hierarchy
    hierarchy_result = test_extract_hierarchy()
    
    if hierarchy_result and hierarchy_result.get('document_hash'):
        # Test 4: Get cached hierarchy
        test_get_cached_hierarchy(hierarchy_result['document_hash'])
    
    print("\n" + "="*80)
    print("✓ ALL API TESTS COMPLETED!")
    print("="*80)


if __name__ == "__main__":
    main()
