#!/usr/bin/env python
"""
Phase A Conformance Suite Execution Script

Runs all Non-RT RIC + A1 conformance suites with minimal twin profile (a1_minimal_twin_v1).
Captures evidence artifacts: junit XML, protocol messages, execution matrix.

Usage:
    python run_phase_a_conformance.py [--twin-profile a1_minimal_twin_v1] [--output-dir ORAN/docs/coverage/evidence]
"""

import sys
import json
import subprocess
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple


logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


class PhaseAConformanceSuiteRunner:
    """Execute Phase A conformance test suites with evidence capture."""
    
    # Conformance test families for Phase A
    PHASE_A_TEST_SUITES = [
        # TS 103 989 section 4.2.1 (A1-P conformance)
        ("TS_103_989_4_2_1", "demo-web/backend/tests/conformance/test_a1_policy_conformance_4_2_1.py"),
        
        # TS 103 989 section 4.2.2 (A1-EI conformance)
        ("TS_103_989_4_2_2", "demo-web/backend/tests/conformance/test_a1_policy_conformance_4_2_2.py"),
        
        # TS 103 989 section 7 (A1-P and A1-EI interoperability)
        ("TS_103_989_7", "demo-web/backend/tests/conformance/test_interoperability_clause7_suites.py"),
        
        # TS 103 987 section 6 and Annex A (API contract)
        ("TS_103_987_API", "demo-web/backend/tests/conformance/test_simulator_capabilities.py"),
        
        # TS 103 988 sections 5-9 (A1 data model)
        ("TS_103_988_5", "demo-web/backend/tests/conformance/test_ts103988_section5_common_types.py"),
        
        # Non-RT RIC readiness assessment
        ("Non_RT_RIC_DUT", "demo-web/backend/tests/conformance/test_non_rt_ric_dut_readiness.py"),
        
        # TS 103 983 section 4/5 (principles and A1 functions)
        ("TS_103_983_4_5", "demo-web/backend/tests/conformance/test_ts103983_section4_principles.py"),
        
        # EI job operations
        ("EI_Job_Ops", "demo-web/backend/tests/conformance/test_ei_job_operations.py"),
        
        # Execution evidence
        ("Exec_Evidence", "demo-web/backend/tests/conformance/test_execution_evidence.py"),
    ]
    
    def __init__(self, twin_profile: str = "a1_minimal_twin_v1", output_dir: str = None):
        """
        Initialize runner with configuration.
        
        Args:
            twin_profile: Twin profile ID to use
            output_dir: Output directory for evidence artifacts
        """
        self.twin_profile = twin_profile
        self.output_dir = Path(output_dir or "ORAN/docs/coverage/evidence")
        self.timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        self.run_id = f"phase_a_{self.timestamp}"
        self.run_dir = self.output_dir / self.run_id
        self.run_dir.mkdir(parents=True, exist_ok=True)
        
        self.execution_matrix = []
        self.summary = {
            "run_id": self.run_id,
            "timestamp": datetime.utcnow().isoformat(),
            "twin_profile": twin_profile,
            "test_suites": {},
            "totals": {
                "suites_executed": 0,
                "suites_passed": 0,
                "suites_failed": 0,
                "total_tests": 0,
                "total_passed": 0,
                "total_failed": 0,
            }
        }
    
    def run_test_suite(self, suite_name: str, test_file: str) -> Tuple[bool, Dict[str, any]]:
        """
        Run a single test suite and capture results.
        
        Args:
            suite_name: Human-readable suite name
            test_file: Path to test file
            
        Returns:
            (success, result_dict) tuple
        """
        logger.info(f"Running suite: {suite_name} ({test_file})")
        
        # Generate junit XML output file
        junit_file = self.run_dir / f"{suite_name}_junit.xml"
        
        # Run pytest with json-report plugin
        cmd = [
            sys.executable, "-m", "pytest",
            test_file,
            "-v",
            "--tb=short",
            f"--json-report",
            f"--json-report-file={self.run_dir / f'{suite_name}_report.json'}",
            f"--junit-xml={junit_file}",
            "-o", "addopts=",
        ]
        
        try:
            result = subprocess.run(
                cmd,
                cwd=Path("C:/TestRepo/demo-web/backend"),
                capture_output=True,
                text=True,
                timeout=300
            )
            
            # Parse results
            success = result.returncode == 0
            
            # Extract test count from output
            output_lines = result.stdout.split("\n")
            test_summary_line = next(
                (line for line in output_lines if "passed" in line or "failed" in line),
                None
            )
            
            result_dict = {
                "suite_name": suite_name,
                "test_file": test_file,
                "success": success,
                "return_code": result.returncode,
                "junit_file": str(junit_file.relative_to(self.output_dir)),
                "test_summary": test_summary_line or "",
                "executed_at": datetime.utcnow().isoformat(),
            }
            
            if success:
                logger.info(f"✅ Suite {suite_name} PASSED")
            else:
                logger.error(f"❌ Suite {suite_name} FAILED")
                logger.error(f"  Output: {result.stdout[-500:]}")
                if result.stderr:
                    logger.error(f"  Error: {result.stderr[-500:]}")
            
            return success, result_dict
        
        except subprocess.TimeoutExpired:
            logger.error(f"❌ Suite {suite_name} TIMEOUT (>300s)")
            return False, {
                "suite_name": suite_name,
                "test_file": test_file,
                "success": False,
                "error": "TIMEOUT",
                "executed_at": datetime.utcnow().isoformat(),
            }
        except Exception as e:
            logger.error(f"❌ Suite {suite_name} ERROR: {e}")
            return False, {
                "suite_name": suite_name,
                "test_file": test_file,
                "success": False,
                "error": str(e),
                "executed_at": datetime.utcnow().isoformat(),
            }
    
    def run_all_suites(self) -> Dict[str, any]:
        """
        Execute all Phase A test suites.
        
        Returns:
            Summary of execution results
        """
        logger.info(f"Starting Phase A conformance suite execution")
        logger.info(f"Twin profile: {self.twin_profile}")
        logger.info(f"Run ID: {self.run_id}")
        logger.info(f"Output: {self.run_dir}")
        
        for suite_name, test_file in self.PHASE_A_TEST_SUITES:
            success, result = self.run_test_suite(suite_name, test_file)
            
            # Update execution matrix
            self.execution_matrix.append({
                "suite_id": suite_name,
                "suite_name": suite_name,
                "verdict": "PASS" if success else "FAIL",
                **result
            })
            
            # Update summary
            self.summary["test_suites"][suite_name] = result
            self.summary["totals"]["suites_executed"] += 1
            
            if success:
                self.summary["totals"]["suites_passed"] += 1
            else:
                self.summary["totals"]["suites_failed"] += 1
        
        # Write execution matrix
        matrix_file = self.run_dir / "execution_matrix.json"
        with open(matrix_file, "w") as f:
            json.dump(self.execution_matrix, f, indent=2)
        logger.info(f"Execution matrix saved to {matrix_file}")
        
        # Write summary
        summary_file = self.run_dir / "execution_summary.json"
        with open(summary_file, "w") as f:
            json.dump(self.summary, f, indent=2)
        logger.info(f"Summary saved to {summary_file}")
        
        return self.summary
    
    def print_report(self):
        """Print execution report to console."""
        logger.info("\n" + "=" * 80)
        logger.info("PHASE A CONFORMANCE SUITE EXECUTION REPORT")
        logger.info("=" * 80)
        logger.info(f"Run ID:       {self.run_id}")
        logger.info(f"Twin Profile: {self.twin_profile}")
        logger.info(f"Timestamp:    {self.summary['timestamp']}")
        logger.info(f"\nResults:")
        logger.info(f"  Suites Executed: {self.summary['totals']['suites_executed']}")
        logger.info(f"  Suites Passed:   {self.summary['totals']['suites_passed']}")
        logger.info(f"  Suites Failed:   {self.summary['totals']['suites_failed']}")
        logger.info(f"\nArtifact Location: {self.run_dir}")
        logger.info("=" * 80 + "\n")


if __name__ == "__main__":
    runner = PhaseAConformanceSuiteRunner()
    runner.run_all_suites()
    runner.print_report()
