import requests
import time

BASE_URL = 'http://localhost:8000/api/oran'

# Verify single rule pack
r = requests.get(f'{BASE_URL}/rules')
packs = r.json()
pack = packs[0]
pack_id = pack['id']
print(f'Rule Pack: {pack["name"]} (ID: {pack_id[:8]}...)')
print(f'Type: {pack["document_type"]}')

# Apply the rule pack directly
print()
print('Applying rule pack to TS_103_989...')
t0 = time.time()
r2 = requests.post(f'{BASE_URL}/rules/{pack_id}/apply', params={'spec_type': 'TS_103_989'})
elapsed = time.time() - t0
print(f'Status: {r2.status_code} (took {elapsed:.1f}s)')
if r2.status_code == 200:
    d = r2.json()
    print(f'  Total Nodes: {d.get("total_nodes", 0)}')
    print(f'  Avg Confidence: {d.get("avg_confidence", 0):.2f}')
    print(f'  Message: {d.get("message", "")}')
else:
    print(f'  Error: {r2.text[:300]}')

# Extract hierarchy via extract endpoint
print()
print('Extract hierarchy (rules=True)...')
r3 = requests.post(f'{BASE_URL}/hierarchy/extract', params={'spec_type': 'TS_103_989', 'use_rules': 'true'})
print(f'Status: {r3.status_code}')
if r3.status_code == 200:
    d3 = r3.json()
    print(f'  Method: {d3["extraction_method"]}')
    print(f'  Fallback Used: {d3["fallback_used"]}')
    print(f'  Quality: {d3["quality_score"]}')
    print(f'  Total Nodes: {d3["total_nodes"]}')
    tree = d3.get('hierarchy_tree')
    if tree and tree.get('root_nodes'):
        roots = tree['root_nodes']
        print(f'  Root Nodes: {len(roots)}')
        for n in roots[:3]:
            sec = n['section_number']
            title = n['title']
            children = n['child_count']
            print(f'    - {sec} {title} ({children} children)')
