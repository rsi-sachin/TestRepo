-- Phase 3 Database Validation SQL Queries
-- Run these queries to validate database state after catalog generation

-- =====================================================
-- Basic Validation Queries
-- =====================================================

-- Query 1: Total test cases in database
SELECT COUNT(*) as total_test_cases FROM test_cases;

-- Query 2: Test cases by catalog
SELECT catalog_id, COUNT(*) as test_count, MIN(created_at) as created
FROM test_cases
GROUP BY catalog_id
ORDER BY created DESC;

-- Query 3: Test cases by source specification
SELECT source_spec, COUNT(*) as count
FROM test_cases
GROUP BY source_spec
ORDER BY count DESC;

-- Query 4: Test cases by HTTP method
SELECT http_method, COUNT(*) as count
FROM test_cases
GROUP BY http_method
ORDER BY count DESC;

-- Query 5: Test cases by complexity
SELECT complexity, COUNT(*) as count
FROM test_cases
GROUP BY complexity
ORDER BY count DESC;

-- =====================================================
-- Phase 3A Validation: Test Extraction Limit
-- =====================================================

-- Query 6: Latest catalog test distribution (should be 2 per spec for MVP)
SELECT source_spec, COUNT(*) as count
FROM test_cases
WHERE catalog_id = (
    SELECT catalog_id FROM test_cases ORDER BY created_at DESC LIMIT 1
)
GROUP BY source_spec;

-- Expected Result for Auto Mode:
-- TS_103_989 | 2
-- TS_103_987 | 2
-- TS_103_988 | 2
-- TS_103_983 | 2

-- Query 7: Verify exactly 8 tests in latest catalog (MVP mode)
SELECT 
    catalog_id,
    COUNT(*) as test_count,
    CASE 
        WHEN COUNT(*) = 8 THEN 'PASS - MVP Mode'
        ELSE 'FAIL - Expected 8 tests'
    END as validation
FROM test_cases
WHERE catalog_id = (
    SELECT catalog_id FROM test_cases ORDER BY created_at DESC LIMIT 1
)
GROUP BY catalog_id;

-- =====================================================
-- Phase 3B Validation: Database Save Fix
-- =====================================================

-- Query 8: Check for duplicate test_ids (should return no rows)
SELECT test_id, COUNT(*) as count
FROM test_cases
GROUP BY test_id
HAVING COUNT(*) > 1;

-- Expected Result: Empty (no duplicates)

-- Query 9: Check for NULL values in required fields
SELECT 
    COUNT(*) as total_rows,
    SUM(CASE WHEN test_id IS NULL THEN 1 ELSE 0 END) as null_test_id,
    SUM(CASE WHEN scenario IS NULL THEN 1 ELSE 0 END) as null_scenario,
    SUM(CASE WHEN source_spec IS NULL THEN 1 ELSE 0 END) as null_source_spec,
    SUM(CASE WHEN source_section IS NULL THEN 1 ELSE 0 END) as null_source_section,
    SUM(CASE WHEN http_method IS NULL THEN 1 ELSE 0 END) as null_http_method,
    SUM(CASE WHEN endpoint IS NULL THEN 1 ELSE 0 END) as null_endpoint,
    SUM(CASE WHEN expected_status IS NULL THEN 1 ELSE 0 END) as null_expected_status,
    SUM(CASE WHEN complexity IS NULL THEN 1 ELSE 0 END) as null_complexity
FROM test_cases;

-- Expected Result: All null counts should be 0

-- Query 10: Verify test_id format (should follow pattern: oran-a1-X-X-X)
SELECT 
    COUNT(*) as total,
    SUM(CASE WHEN test_id LIKE 'oran-a1-%' THEN 1 ELSE 0 END) as valid_format,
    SUM(CASE WHEN test_id NOT LIKE 'oran-a1-%' THEN 1 ELSE 0 END) as invalid_format
FROM test_cases;

-- Expected Result: invalid_format = 0

-- Query 11: Verify HTTP methods are valid
SELECT 
    http_method,
    COUNT(*) as count,
    CASE 
        WHEN http_method IN ('GET', 'POST', 'PUT', 'DELETE', 'PATCH') THEN 'Valid'
        ELSE 'Invalid'
    END as validation
FROM test_cases
GROUP BY http_method;

-- Expected Result: All methods should be Valid

-- Query 12: Verify expected status codes are reasonable
SELECT 
    expected_status,
    COUNT(*) as count,
    CASE 
        WHEN expected_status BETWEEN 200 AND 599 THEN 'Valid'
        ELSE 'Invalid'
    END as validation
FROM test_cases
GROUP BY expected_status
ORDER BY expected_status;

-- Expected Result: All status codes should be Valid

-- =====================================================
-- Phase 3C Validation: Section Selection
-- =====================================================

-- Query 13: Find catalogs with custom section counts (not 8)
SELECT 
    catalog_id,
    COUNT(*) as test_count,
    CASE 
        WHEN COUNT(*) = 8 THEN 'MVP Mode'
        WHEN COUNT(*) < 8 THEN 'Custom Selection (Partial)'
        WHEN COUNT(*) > 8 AND COUNT(*) < 100 THEN 'Custom Selection (Medium)'
        WHEN COUNT(*) >= 100 THEN 'Custom Selection (Large)'
        ELSE 'Unknown'
    END as mode
FROM test_cases
GROUP BY catalog_id
ORDER BY test_count;

-- Query 14: Most recent 5 catalogs with their test counts
SELECT 
    catalog_id,
    COUNT(*) as test_count,
    MIN(created_at) as created,
    MAX(updated_at) as updated
FROM test_cases
GROUP BY catalog_id
ORDER BY created DESC
LIMIT 5;

-- =====================================================
-- Detailed Test Case Inspection
-- =====================================================

-- Query 15: Sample test cases from latest catalog (first 10)
SELECT 
    test_id,
    scenario,
    source_spec,
    source_section,
    http_method,
    endpoint,
    expected_status,
    complexity
FROM test_cases
WHERE catalog_id = (
    SELECT catalog_id FROM test_cases ORDER BY created_at DESC LIMIT 1
)
ORDER BY source_spec, source_section
LIMIT 10;

-- Query 16: Test case enrichments (if any exist)
SELECT 
    tc.test_id,
    tc.scenario,
    COUNT(tce.id) as enrichment_count
FROM test_cases tc
LEFT JOIN test_case_enrichments tce ON tc.id = tce.test_case_id
WHERE tc.catalog_id = (
    SELECT catalog_id FROM test_cases ORDER BY created_at DESC LIMIT 1
)
GROUP BY tc.test_id, tc.scenario
ORDER BY enrichment_count DESC
LIMIT 10;

-- =====================================================
-- Performance and Statistics
-- =====================================================

-- Query 17: Database statistics
SELECT 
    COUNT(DISTINCT catalog_id) as total_catalogs,
    COUNT(*) as total_test_cases,
    COUNT(DISTINCT source_spec) as specs_used,
    COUNT(DISTINCT http_method) as methods_used,
    COUNT(DISTINCT complexity) as complexity_levels,
    MIN(created_at) as first_test,
    MAX(created_at) as latest_test
FROM test_cases;

-- Query 18: Average tests per catalog
SELECT 
    AVG(test_count) as avg_tests_per_catalog,
    MIN(test_count) as min_tests,
    MAX(test_count) as max_tests,
    COUNT(*) as total_catalogs
FROM (
    SELECT catalog_id, COUNT(*) as test_count
    FROM test_cases
    GROUP BY catalog_id
);

-- Query 19: Section number distribution (how many unique sections)
SELECT 
    source_spec,
    COUNT(DISTINCT source_section) as unique_sections
FROM test_cases
GROUP BY source_spec
ORDER BY unique_sections DESC;

-- Query 20: Endpoint popularity
SELECT 
    endpoint,
    COUNT(*) as usage_count,
    COUNT(DISTINCT catalog_id) as catalogs_used_in
FROM test_cases
GROUP BY endpoint
ORDER BY usage_count DESC
LIMIT 10;

-- =====================================================
-- Cleanup Queries (Use with caution!)
-- =====================================================

-- Query 21: Delete all test cases from specific catalog
-- CAUTION: Uncomment and replace <catalog-id> before running
-- DELETE FROM test_cases WHERE catalog_id = '<catalog-id>';

-- Query 22: Delete all test cases (complete reset)
-- CAUTION: Uncomment before running
-- DELETE FROM test_cases;

-- Query 23: Reset auto-increment counter
-- CAUTION: Uncomment before running
-- DELETE FROM sqlite_sequence WHERE name='test_cases';

-- =====================================================
-- Validation Summary Query
-- =====================================================

-- Query 24: Comprehensive validation report
SELECT 
    'Total Test Cases' as metric,
    CAST(COUNT(*) as TEXT) as value
FROM test_cases
UNION ALL
SELECT 
    'Unique Catalogs',
    CAST(COUNT(DISTINCT catalog_id) as TEXT)
FROM test_cases
UNION ALL
SELECT 
    'Duplicate Test IDs',
    CAST(COUNT(*) as TEXT)
FROM (
    SELECT test_id FROM test_cases GROUP BY test_id HAVING COUNT(*) > 1
)
UNION ALL
SELECT 
    'NULL Values in Required Fields',
    CAST(SUM(
        CASE WHEN test_id IS NULL OR scenario IS NULL OR source_spec IS NULL 
             OR source_section IS NULL OR http_method IS NULL OR endpoint IS NULL
             OR expected_status IS NULL OR complexity IS NULL 
        THEN 1 ELSE 0 END
    ) as TEXT)
FROM test_cases
UNION ALL
SELECT 
    'Invalid HTTP Methods',
    CAST(SUM(
        CASE WHEN http_method NOT IN ('GET', 'POST', 'PUT', 'DELETE', 'PATCH') 
        THEN 1 ELSE 0 END
    ) as TEXT)
FROM test_cases
UNION ALL
SELECT 
    'Invalid Status Codes',
    CAST(SUM(
        CASE WHEN expected_status NOT BETWEEN 200 AND 599 
        THEN 1 ELSE 0 END
    ) as TEXT)
FROM test_cases;

-- Expected Result: All validation metrics should show 0 for errors
