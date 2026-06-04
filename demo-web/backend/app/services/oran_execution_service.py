"""
ORAN Execution Service
Manages O-RAN test execution lifecycle via pytest
Extends ExecutionService with pytest-specific command building and parsing
"""

from typing import Dict, Optional
import asyncio
import subprocess
from pathlib import Path
from datetime import datetime
from app.models import ExecutionStatus
from app.models.oran import OranExecutionResult, OranTestCase, OranKpiMetrics
from app.config import settings
from app.websockets.demo_output import broadcast_output
from app.parsers.oran_parser import OranParser, PytestOutputParser
from app.services.execution_service import ExecutionService


class OranExecutionService(ExecutionService):
    """Service for executing O-RAN tests via pytest"""
    
    def __init__(self):
        super().__init__()
        self.oran_executions: Dict[str, OranExecutionResult] = {}
    
    async def execute_oran_test(
        self,
        execution_id: str,
        test_id: str,
        catalog_id: Optional[str] = None,
        config: Optional[Dict[str, str]] = None
    ):
        """
        Execute an O-RAN test asynchronously
        
        Args:
            execution_id: Unique execution identifier
            test_id: Test case identifier (matches generated pytest file name)
            catalog_id: Optional catalog identifier
            config: Optional test configuration parameters
        
        This method:
        1. Locates pytest test file
        2. Builds pytest command with parameters
        3. Spawns pytest process
        4. Streams output via WebSocket
        5. Monitors completion
        6. Parses pytest JSON report for statistics and KPIs
        """
        # Create execution result
        result = OranExecutionResult(
            execution_id=execution_id,
            test_id=test_id,
            catalog_id=catalog_id,
            status=ExecutionStatus.STARTING.value,
            started_at=datetime.utcnow()
        )
        self.oran_executions[execution_id] = result
        
        try:
            # Build pytest command
            command = self._build_pytest_command(test_id, config or {}, execution_id)
            
            # Broadcast status
            await broadcast_output(execution_id, "status", {
                "status": "starting",
                "command": command,
                "test_id": test_id
            })
            
            # Start pytest process
            result.status = ExecutionStatus.RUNNING.value
            await broadcast_output(execution_id, "status", {"status": "running"})
            
            # Run process and stream output
            await self._run_pytest_process(execution_id, command)
            
            # Parse pytest JSON report for final statistics and KPIs
            json_report_file = self._get_json_report_path(execution_id)
            if json_report_file.exists():
                result.pytest_json_report = str(json_report_file)
                
                # Parse statistics and KPIs
                parser = OranParser(json_report_file)
                
                stats = parser.parse_statistics()
                result.total_tests = stats['total_tests']
                result.passed = stats['passed']
                result.failed = stats['failed']
                result.skipped = stats['skipped']
                result.pass_rate = stats['pass_rate']
                
                # Parse ORAN-specific KPIs
                kpis = parser.parse_kpis()
                if kpis:
                    result.kpis = kpis
                
                # Broadcast summary
                summary = parser.get_test_summary()
                await broadcast_output(execution_id, "output", "\n" + summary)
            
            # Mark as completed
            result.status = ExecutionStatus.COMPLETED.value
            result.completed_at = datetime.utcnow()
            result.duration_seconds = (result.completed_at - result.started_at).total_seconds()
            
            await broadcast_output(execution_id, "complete", {
                "status": "completed",
                "statistics": {
                    "total_tests": result.total_tests,
                    "passed": result.passed,
                    "failed": result.failed,
                    "skipped": result.skipped,
                    "pass_rate": result.pass_rate
                },
                "kpis": result.kpis.dict() if result.kpis else None,
                "execution_time": result.duration_seconds
            })
        
        except Exception as e:
            result.status = ExecutionStatus.FAILED.value
            result.error_message = str(e)
            result.completed_at = datetime.utcnow()
            
            await broadcast_output(execution_id, "error", str(e))
            await broadcast_output(execution_id, "complete", {
                "status": "failed",
                "error": str(e)
            })
    
    async def _run_pytest_process(self, execution_id: str, command: str):
        """Run pytest process and stream output (similar to _run_jmeter_process)"""
        try:
            print(f"Executing pytest command: {command}")
            
            # Get working directory (where generated tests are)
            working_dir = settings.oran_generated_tests_path or (settings.tts_path / "generated_tests")
            print(f"Working directory: {working_dir}")
            
            # Ensure directory exists
            working_dir.mkdir(parents=True, exist_ok=True)
            
            # Use subprocess module in thread pool for Windows compatibility
            from concurrent.futures import ThreadPoolExecutor
            
            def run_process():
                """Run process in thread (Windows-compatible)"""
                process = subprocess.Popen(
                    command,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    stdin=subprocess.DEVNULL,
                    cwd=str(working_dir),
                    shell=True,
                    text=True,
                    bufsize=1,
                    universal_newlines=True
                )
                return process
            
            # Start process in thread pool
            loop = asyncio.get_event_loop()
            with ThreadPoolExecutor() as executor:
                process = await loop.run_in_executor(executor, run_process)
                self.processes[execution_id] = process
                
                # Stream output with pytest-specific parsing
                output_parser = PytestOutputParser()
                line_count = 0
                
                while True:
                    line = await loop.run_in_executor(executor, process.stdout.readline)
                    if not line:
                        break
                    
                    output = line.rstrip()
                    if output:
                        line_count += 1
                        print(f"pytest output [{line_count}]: {output[:100]}")
                        
                        # Broadcast output line
                        await broadcast_output(execution_id, "output", output)
                        
                        # Parse for test results
                        test_result = output_parser.parse_line(output)
                        if test_result:
                            await broadcast_output(execution_id, "test_result", test_result)
                
                # Wait for completion
                returncode = await loop.run_in_executor(executor, process.wait)
            
            print(f"pytest process completed with return code: {returncode}")
            
            # Clean up
            if execution_id in self.processes:
                del self.processes[execution_id]
            
            if returncode != 0:
                print(f"Warning: pytest process exited with code {returncode} (may have test failures)")
                # Note: pytest returns non-zero if tests fail, which is expected
        
        except Exception as e:
            print(f"Exception in _run_pytest_process: {type(e).__name__}: {str(e)}")
            import traceback
            traceback.print_exc()
            raise Exception(f"Error running pytest: {str(e)}")
    
    def _build_pytest_command(self, test_id: str, config: Dict[str, str], execution_id: str) -> str:
        """
        Build pytest command for O-RAN test execution
        
        Args:
            test_id: Test identifier (used to locate test file)
            config: Configuration parameters (converted to environment variables or CLI args)
            execution_id: Execution ID for output file naming
        
        Returns:
            Command string to execute pytest
        """
        # Get paths
        working_dir = settings.oran_generated_tests_path or (settings.tts_path / "generated_tests")
        test_file = working_dir / f"{test_id}.py"
        json_report = self._get_json_report_path(execution_id)
        
        # Ensure JSON report directory exists
        json_report.parent.mkdir(parents=True, exist_ok=True)
        
        # Build pytest command
        # Uses pytest-json-report plugin for structured output
        cmd_parts = [
            "pytest",
            f'"{test_file}"',
            "-v",  # Verbose output
            "--json-report",  # Enable JSON report plugin
            f"--json-report-file=\"{json_report}\"",
            "--json-report-indent=2",
            "--tb=short",  # Short traceback format
        ]
        
        # Add configuration as environment variables or pytest options
        for key, value in config.items():
            # Pass config as pytest options (can be accessed via pytest fixtures)
            cmd_parts.append(f"--{key}={value}")
        
        return " ".join(cmd_parts)
    
    def _get_json_report_path(self, execution_id: str) -> Path:
        """Get path for pytest JSON report file"""
        reports_dir = settings.oran_history_path or (settings.runs_directory / "oran_reports")
        reports_dir.mkdir(parents=True, exist_ok=True)
        return reports_dir / f"{execution_id}_report.json"
    
    async def get_oran_execution_result(self, execution_id: str) -> Optional[OranExecutionResult]:
        """Get ORAN execution result"""
        return self.oran_executions.get(execution_id)
    
    async def list_active_oran_executions(self) -> list:
        """List all active ORAN executions"""
        return [
            {
                "execution_id": exec_id,
                "test_id": result.test_id,
                "status": result.status,
                "started_at": result.started_at.isoformat() if result.started_at else None
            }
            for exec_id, result in self.oran_executions.items()
            if result.status in [ExecutionStatus.RUNNING.value, ExecutionStatus.STARTING.value]
        ]
