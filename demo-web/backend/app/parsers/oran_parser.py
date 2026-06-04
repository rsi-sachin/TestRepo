"""
ORAN Parser - Extracts test results and KPIs from pytest JSON reports
Parses pytest-json-report plugin output for O-RAN test execution
"""

from pathlib import Path
from typing import Dict, List, Optional
import json
from datetime import datetime
from ..models.oran import OranKpiMetrics


class OranParser:
    """Parser for pytest JSON report files (from pytest-json-report plugin)"""
    
    def __init__(self, json_report_file: Path):
        """
        Initialize parser with pytest JSON report file
        
        Args:
            json_report_file: Path to pytest JSON report (e.g., report.json)
        """
        self.json_report_file = json_report_file
        self.report_data: Optional[Dict] = None
        
    def load_report(self) -> bool:
        """
        Load and parse JSON report file
        
        Returns:
            bool: True if loaded successfully, False otherwise
        """
        try:
            with open(self.json_report_file, 'r', encoding='utf-8') as f:
                self.report_data = json.load(f)
            return True
        except Exception as e:
            print(f"Error loading pytest JSON report: {e}")
            return False
    
    def parse_statistics(self) -> Dict[str, any]:
        """
        Parse pytest report for basic test statistics
        
        Returns:
            dict with total_tests, passed, failed, skipped, pass_rate, duration
        """
        if not self.report_data:
            if not self.load_report():
                return self._empty_statistics()
        
        try:
            # Get summary section
            summary = self.report_data.get('summary', {})
            
            total_tests = summary.get('total', 0)
            passed = summary.get('passed', 0)
            failed = summary.get('failed', 0)
            skipped = summary.get('skipped', 0)
            
            # Calculate pass rate
            pass_rate = (passed / total_tests * 100) if total_tests > 0 else 0.0
            
            # Get total duration
            duration = self.report_data.get('duration', 0.0)
            
            return {
                "total_tests": total_tests,
                "passed": passed,
                "failed": failed,
                "skipped": skipped,
                "pass_rate": round(pass_rate, 2),
                "duration_seconds": round(duration, 2)
            }
        
        except Exception as e:
            print(f"Error parsing pytest statistics: {e}")
            return self._empty_statistics()
    
    def parse_kpis(self) -> Optional[OranKpiMetrics]:
        """
        Extract O-RAN specific KPI metrics from pytest report
        
        Assumes tests capture custom metrics in test metadata or via fixtures
        
        Returns:
            OranKpiMetrics object or None if no KPIs found
        """
        if not self.report_data:
            if not self.load_report():
                return None
        
        try:
            # Extract latency metrics from test durations
            tests = self.report_data.get('tests', [])
            if not tests:
                return None
            
            durations = []
            for test in tests:
                # Get call duration (main test execution time)
                call_info = test.get('call', {})
                duration = call_info.get('duration', 0)
                if duration > 0:
                    durations.append(duration * 1000)  # Convert to milliseconds
            
            if not durations:
                return None
            
            # Calculate latency statistics
            durations.sort()
            avg_latency = sum(durations) / len(durations)
            
            # Calculate percentiles
            p95_index = int(len(durations) * 0.95)
            p99_index = int(len(durations) * 0.99)
            p95_latency = durations[p95_index] if p95_index < len(durations) else durations[-1]
            p99_latency = durations[p99_index] if p99_index < len(durations) else durations[-1]
            
            # Calculate throughput
            total_duration = self.report_data.get('duration', 1.0)
            total_tests = len(tests)
            requests_per_second = total_tests / total_duration if total_duration > 0 else 0
            
            # Calculate successful request rate
            passed = self.report_data.get('summary', {}).get('passed', 0)
            successful_rps = passed / total_duration if total_duration > 0 else 0
            
            # Conformance rate (same as pass rate)
            conformance_rate = (passed / total_tests * 100) if total_tests > 0 else 0.0
            
            # Check for custom KPIs in test metadata
            schema_validation_count = 0
            schema_validation_passed = 0
            
            for test in tests:
                # Look for custom properties/metadata
                user_properties = test.get('user_properties', {})
                if 'schema_validation' in user_properties:
                    schema_validation_count += 1
                    if user_properties['schema_validation'] == 'passed':
                        schema_validation_passed += 1
            
            schema_validation_rate = (schema_validation_passed / schema_validation_count * 100) if schema_validation_count > 0 else 100.0
            
            return OranKpiMetrics(
                avg_latency_ms=round(avg_latency, 2),
                p95_latency_ms=round(p95_latency, 2),
                p99_latency_ms=round(p99_latency, 2),
                requests_per_second=round(requests_per_second, 2),
                successful_requests_per_second=round(successful_rps, 2),
                conformance_rate=round(conformance_rate, 2),
                schema_validation_rate=round(schema_validation_rate, 2)
            )
        
        except Exception as e:
            print(f"Error parsing ORAN KPIs: {e}")
            return None
    
    def get_failed_tests(self) -> List[Dict]:
        """
        Extract details of failed tests for debugging
        
        Returns:
            List of failed test dictionaries with test name, error, and traceback
        """
        if not self.report_data:
            if not self.load_report():
                return []
        
        failed_tests = []
        
        try:
            tests = self.report_data.get('tests', [])
            
            for test in tests:
                if test.get('outcome') == 'failed':
                    call_info = test.get('call', {})
                    
                    failed_test = {
                        "test_id": test.get('nodeid', 'unknown'),
                        "error_message": call_info.get('longrepr', 'No error message'),
                        "duration": call_info.get('duration', 0),
                        "crash": call_info.get('crash', None)
                    }
                    failed_tests.append(failed_test)
            
            return failed_tests
        
        except Exception as e:
            print(f"Error extracting failed tests: {e}")
            return []
    
    def get_test_summary(self) -> str:
        """
        Generate human-readable test execution summary
        
        Returns:
            Formatted string summary
        """
        stats = self.parse_statistics()
        kpis = self.parse_kpis()
        
        summary_lines = [
            "=== ORAN TEST EXECUTION SUMMARY ===",
            f"Total Tests: {stats['total_tests']}",
            f"Passed: {stats['passed']}",
            f"Failed: {stats['failed']}",
            f"Skipped: {stats['skipped']}",
            f"Pass Rate: {stats['pass_rate']}%",
            f"Duration: {stats['duration_seconds']}s",
        ]
        
        if kpis:
            summary_lines.extend([
                "",
                "=== PERFORMANCE METRICS ===",
                f"Avg Latency: {kpis.avg_latency_ms}ms",
                f"P95 Latency: {kpis.p95_latency_ms}ms",
                f"P99 Latency: {kpis.p99_latency_ms}ms",
                f"Throughput: {kpis.requests_per_second} req/s",
                f"Conformance Rate: {kpis.conformance_rate}%",
            ])
        
        # Add failed test details if any
        failed_tests = self.get_failed_tests()
        if failed_tests:
            summary_lines.extend([
                "",
                "=== FAILED TESTS ===",
            ])
            for ft in failed_tests:
                summary_lines.append(f"  - {ft['test_id']}")
                summary_lines.append(f"    Error: {ft['error_message'][:100]}")
        
        return "\n".join(summary_lines)
    
    def _empty_statistics(self) -> Dict[str, any]:
        """Return empty statistics structure"""
        return {
            "total_tests": 0,
            "passed": 0,
            "failed": 0,
            "skipped": 0,
            "pass_rate": 0.0,
            "duration_seconds": 0.0
        }


class PytestOutputParser:
    """Parser for real-time pytest console output (text streaming)"""
    
    def __init__(self):
        self.test_results = []
        
    def parse_line(self, line: str) -> Optional[Dict]:
        """
        Parse a single line of pytest output for test result
        
        Args:
            line: Single line of pytest console output
        
        Returns:
            Dict with test info if line contains test result, None otherwise
        """
        # Match pytest test result lines like:
        # test_file.py::test_name PASSED
        # test_file.py::test_name FAILED
        import re
        
        match = re.match(r'^(.+?\.py::[\w_]+)\s+(PASSED|FAILED|SKIPPED)', line)
        if match:
            test_id = match.group(1)
            outcome = match.group(2).lower()
            
            return {
                "test_id": test_id,
                "outcome": outcome,
                "line": line
            }
        
        return None
    
    def is_summary_line(self, line: str) -> bool:
        """Check if line is pytest summary line (e.g., '=== 5 passed, 1 failed in 10.5s ===')"""
        return '===' in line and (' passed' in line or ' failed' in line)
