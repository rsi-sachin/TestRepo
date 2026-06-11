import requests

BASE_URL = 'http://localhost:8000/api/oran'

results = []

# TEST 1: List Rule Packs
print('\n=== TEST 1: List Rule Packs ===')
r = requests.get(f'{BASE_URL}/rules')
print(f'Status: {r.status_code}')
data = r.json()
print(f'Rule Packs: {len(data)}')
for p in data:
    name = p['name']
    dtype = p['document_type']
    q = p['avg_quality_score']
    print(f'  - {name} (type={dtype}, quality={q:.2f})')
results.append(('List Rule Packs', r.status_code == 200, r.status_code))

# TEST 2: Hierarchy Extract (rule-based)
print('\n=== TEST 2: Hierarchy Extract (rules=True) ===')
r = requests.post(f'{BASE_URL}/hierarchy/extract', params={'spec_type': 'TS_103_989', 'use_rules': True})
print(f'Status: {r.status_code}')
if r.status_code == 200:
    d = r.json()
    print(f'  Method: {d["extraction_method"]}')
    print(f'  Quality: {d["quality_score"]:.2f}')
    print(f'  Total Nodes: {d["total_nodes"]}')
    print(f'  Fallback Used: {d["fallback_used"]}')
    print(f'  Doc Hash: {d["document_hash"]}')
    doc_hash = d['document_hash']
    results.append(('Hierarchy Extract (rules)', True, r.status_code))
else:
    print(f'  Error: {r.text[:200]}')
    doc_hash = None
    results.append(('Hierarchy Extract (rules)', False, r.status_code))

# TEST 3: Hierarchy Extract (heuristic)
print('\n=== TEST 3: Hierarchy Extract (rules=False) ===')
r = requests.post(f'{BASE_URL}/hierarchy/extract', params={'spec_type': 'TS_103_989', 'use_rules': False})
print(f'Status: {r.status_code}')
if r.status_code == 200:
    d = r.json()
    print(f'  Method: {d["extraction_method"]}')
    print(f'  Quality: {d["quality_score"]:.2f}')
    print(f'  Total Nodes: {d["total_nodes"]}')
    results.append(('Hierarchy Extract (heuristic)', True, r.status_code))
else:
    print(f'  Error: {r.text[:200]}')
    results.append(('Hierarchy Extract (heuristic)', False, r.status_code))

# TEST 4: Get cached hierarchy
if doc_hash:
    print(f'\n=== TEST 4: Get Cached Hierarchy ({doc_hash[:8]}...) ===')
    r = requests.get(f'{BASE_URL}/hierarchy/{doc_hash}')
    print(f'Status: {r.status_code}')
    if r.status_code == 200:
        d = r.json()
        print(f'  Document: {d.get("document_name", "N/A")}')
        print(f'  Total Nodes: {d.get("total_nodes", 0)}')
        root_nodes = d.get('root_nodes', [])
        print(f'  Root Nodes: {len(root_nodes)}')
        for n in root_nodes[:3]:
            sec = n.get('section_number', '?')
            title = n.get('title', '?')
            children = n.get('child_count', 0)
            print(f'    - {sec} {title} ({children} children)')
        results.append(('Get Cached Hierarchy', True, r.status_code))
    else:
        print(f'  Error: {r.text[:200]}')
        results.append(('Get Cached Hierarchy', False, r.status_code))

# TEST 5: Learn rules
print('\n=== TEST 5: Learn Rules from Document ===')
r = requests.post(f'{BASE_URL}/rules/learn', params={'spec_type': 'TS_103_989', 'max_depth': 4})
print(f'Status: {r.status_code}')
if r.status_code == 200:
    d = r.json()
    pack_id = d.get('rule_pack_id') or d.get('id')
    print(f'  Name: {d.get("name", "N/A")}')
    print(f'  ID: {pack_id}')
    print(f'  Doc Type: {d.get("document_type", "N/A")}')
    print(f'  Rules count: {d.get("extraction_rules_count", 0)}')
    results.append(('Learn Rules', True, r.status_code))
else:
    print(f'  Error: {r.text[:200]}')
    pack_id = None
    results.append(('Learn Rules', False, r.status_code))

# TEST 6: Get Rule Pack
if pack_id:
    print(f'\n=== TEST 6: Get Rule Pack ({pack_id[:8]}...) ===')
    r = requests.get(f'{BASE_URL}/rules/{pack_id}')
    print(f'Status: {r.status_code}')
    if r.status_code == 200:
        d = r.json()
        print(f'  Name: {d["name"]}')
        print(f'  Max Depth: {d["hierarchy_config"]["max_depth"]}')
        levels = d['hierarchy_config'].get('level_definitions', {})
        for lvl, name in sorted(levels.items()):
            print(f'    Level {lvl}: {name}')
        results.append(('Get Rule Pack', True, r.status_code))
    else:
        print(f'  Error: {r.text[:200]}')
        results.append(('Get Rule Pack', False, r.status_code))

# TEST 7: Apply Rule Pack
if pack_id:
    print(f'\n=== TEST 7: Apply Rule Pack ===')
    r = requests.post(f'{BASE_URL}/rules/{pack_id}/apply', params={'spec_type': 'TS_103_989'})
    print(f'Status: {r.status_code}')
    if r.status_code == 200:
        d = r.json()
        print(f'  Total Nodes: {d.get("total_nodes", 0)}')
        print(f'  Avg Confidence: {d.get("avg_confidence", 0):.2f}')
        results.append(('Apply Rule Pack', True, r.status_code))
    else:
        print(f'  Error: {r.text[:200]}')
        results.append(('Apply Rule Pack', False, r.status_code))

# TEST 8: List Catalogs
print('\n=== TEST 8: List Catalogs ===')
r = requests.get(f'{BASE_URL}/catalogs')
print(f'Status: {r.status_code}')
if r.status_code == 200:
    cats = r.json()
    print(f'  Catalogs: {len(cats)}')
    results.append(('List Catalogs', True, r.status_code))
else:
    print(f'  Error: {r.text[:200]}')
    results.append(('List Catalogs', False, r.status_code))

# TEST 9: Delete test rule pack
if pack_id:
    print(f'\n=== TEST 9: Delete Test Rule Pack ===')
    r = requests.delete(f'{BASE_URL}/rules/{pack_id}')
    print(f'Status: {r.status_code}')
    if r.status_code == 200:
        d = r.json()
        print(f'  Message: {d.get("message", "Deleted")}')
        results.append(('Delete Rule Pack', True, r.status_code))
    else:
        print(f'  Error: {r.text[:200]}')
        results.append(('Delete Rule Pack', False, r.status_code))

# Summary
print('\n' + '='*60)
print('TEST SUMMARY')
print('='*60)
passed = sum(1 for _, ok, _ in results if ok)
total = len(results)
for name, ok, status in results:
    icon = '✓' if ok else '✗'
    print(f'  {icon} {name} (HTTP {status})')
print(f'\n  {passed}/{total} tests passed')
if passed == total:
    print('\n  ALL TESTS PASSED! ✓')
else:
    print(f'\n  {total - passed} tests FAILED!')
