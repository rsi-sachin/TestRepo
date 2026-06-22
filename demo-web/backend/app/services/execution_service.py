"""
Execution Service
Manages demo execution lifecycle via JMeter
Reuses logic from Java DemoRunner but adapted for Python async
"""

from typing import Dict, Optional, Callable
import asyncio
import subprocess
from pathlib import Path
from datetime import datetime
import sys
from app.models import ExecutionResult, ExecutionStatus, SipMessage
from app.config import settings
from app.services.demo_service import DemoService
from app.websockets.demo_output import broadcast_output
from app.parsers.jtl_parser import JtlParser, SipMessageSequencer


class ExecutionService:
    """Service for executing demos via JMeter"""
    
    def __init__(self):
        self.demo_service = DemoService()
        self.active_executions: Dict[str, ExecutionResult] = {}
        self.processes: Dict[str, subprocess.Popen] = {}
    
    async def execute_demo(self, execution_id: str, demo_id: str, parameters: Dict[str, str]):
        """
        Execute a demo asynchronously
        
        This method:
        1. Retrieves demo definition
        2. Builds JMeter command with parameters
        3. Spawns JMeter process
        4. Streams output via WebSocket
        5. Monitors completion
        6. Parses JTL file for statistics
        """
        # Get demo
        demo = await self.demo_service.get_demo_by_id(demo_id)
        if not demo:
            await broadcast_output(execution_id, "error", f"Demo {demo_id} not found")
            return
        
        # Create execution result
        result = ExecutionResult(
            execution_id=execution_id,
            demo_id=demo_id,
            status=ExecutionStatus.STARTING,
            started_at=datetime.utcnow()
        )
        self.active_executions[execution_id] = result
        
        try:
            # Merge default params with provided params
            all_params = {**demo.default_params, **parameters}
            
            # Build JMeter command
            command = self._build_jmeter_command(demo, all_params, execution_id)
            
            # Broadcast status
            await broadcast_output(execution_id, "status", {"status": "starting", "command": command})
            
            # Start JMeter process
            result.status = ExecutionStatus.RUNNING
            await broadcast_output(execution_id, "status", {"status": "running"})
            
            # Run process and stream output
            await self._run_jmeter_process(execution_id, command)
            
            # Parse JTL file for final statistics and SIP messages
            jtl_file = settings.runs_directory / f"{execution_id}.jtl"
            if jtl_file.exists():
                result.jtl_file = str(jtl_file)
                
                # Parse statistics
                parser = JtlParser(jtl_file)
                stats = parser.parse_statistics()
                result.statistics = stats
                
                # Parse and broadcast SIP messages for visualization
                await self._parse_and_broadcast_sip_messages(execution_id, jtl_file)
            
            # Mark as completed
            result.status = ExecutionStatus.COMPLETED
            result.completed_at = datetime.utcnow()
            
            await broadcast_output(execution_id, "complete", {
                "status": "completed",
                "statistics": result.statistics,
                "execution_time": (result.completed_at - result.started_at).total_seconds()
            })
        
        except Exception as e:
            result.status = ExecutionStatus.FAILED
            result.error_message = str(e)
            result.completed_at = datetime.utcnow()
            
            await broadcast_output(execution_id, "error", str(e))
            await broadcast_output(execution_id, "complete", {
                "status": "failed",
                "error": str(e)
            })
    
    async def _run_jmeter_process(self, execution_id: str, command: str):
        """Run JMeter process and stream output"""
        try:
            print(f"Executing JMeter command: {command}")
            print(f"Working directory: {settings.tts_path}")
            
            # Use subprocess module in thread pool for Windows compatibility
            import subprocess
            from concurrent.futures import ThreadPoolExecutor
            
            def run_process():
                """Run process in thread (Windows-compatible)"""
                process = subprocess.Popen(
                    command,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    stdin=subprocess.DEVNULL,  # Bypass pause commands
                    cwd=str(settings.tts_path),
                    shell=True,
                    text=True,
                    bufsize=1,
                    universal_newlines=True
                )
                return process
            
            # Start process in thread pool
            loop = asyncio.get_running_loop()
            with ThreadPoolExecutor() as executor:
                process = await loop.run_in_executor(executor, run_process)
                self.processes[execution_id] = process
                
                # Stream output
                line_count = 0
                while True:
                    line = await loop.run_in_executor(executor, process.stdout.readline)
                    if not line:
                        break
                    
                    output = line.rstrip()
                    if output:
                        line_count += 1
                        print(f"JMeter output [{line_count}]: {output[:100]}")
                        await broadcast_output(execution_id, "output", output)
                
                # Wait for completion
                returncode = await loop.run_in_executor(executor, process.wait)
            
            print(f"JMeter process completed with return code: {returncode}")
            
            # Clean up
            if execution_id in self.processes:
                del self.processes[execution_id]
            
            if returncode != 0:
                raise Exception(f"JMeter process exited with code {returncode}")
        
        except Exception as e:
            print(f"Exception in _run_jmeter_process: {type(e).__name__}: {str(e)}")
            import traceback
            traceback.print_exc()
            raise Exception(f"Error running JMeter: {str(e)}")
    
    async def _parse_and_broadcast_sip_messages(self, execution_id: str, jtl_file: Path):
        """Parse SIP messages from JTL and broadcast for visualization"""
        try:
            parser = JtlParser(jtl_file)
            sip_messages = parser.parse_sip_messages()
            
            if sip_messages:
                # Build Mermaid diagram
                sequencer = SipMessageSequencer()
                for msg in sip_messages:
                    sequencer.add_message(msg)
                
                mermaid_diagram = sequencer.get_mermaid_diagram()
                
                # Broadcast messages one by one for real-time effect
                for msg in sip_messages:
                    await broadcast_output(execution_id, "sip_message", msg)
                    await asyncio.sleep(0.1)  # Small delay for visual effect
                
                # Send complete diagram
                await broadcast_output(execution_id, "call_flow_diagram", {
                    "mermaid": mermaid_diagram,
                    "message_count": len(sip_messages)
                })
                
                print(f"Broadcasted {len(sip_messages)} SIP messages for execution {execution_id}")
        
        except Exception as e:
            print(f"Error parsing/broadcasting SIP messages: {e}")
            import traceback
            traceback.print_exc()
    
    async def _parse_jtl_statistics(self, jtl_file: Path) -> Dict[str, any]:
        """Parse JTL file for basic statistics"""
        try:
            total_attempts = 0
            successful = 0
            failed = 0
            
            with open(jtl_file, 'r', encoding='utf-8') as f:
                # Skip header line
                header = f.readline()
                
                # Count success/failure
                for line in f:
                    if line.strip():
                        total_attempts += 1
                        # JTL format: success column is typically 8th column (index 7)
                        parts = line.split(',')
                        if len(parts) > 7:
                            success_flag = parts[7].strip().lower()
                            if success_flag == 'true':
                                successful += 1
                            else:
                                failed += 1
            
            success_rate = (successful / total_attempts * 100) if total_attempts > 0 else 0.0
            
            return {
                "total_attempts": total_attempts,
                "successful": successful,
                "failed": failed,
                "success_rate": round(success_rate, 2)
            }
        
        except Exception as e:
            print(f"Error parsing JTL file: {e}")
            return {
                "total_attempts": 0,
                "successful": 0,
                "failed": 0,
                "success_rate": 0.0
            }
    
    def _build_jmeter_command(self, demo, parameters: Dict[str, str], execution_id: str) -> str:
        """Build JMeter command using Java JAR directly to avoid batch file issues"""
        # Use Java to run JMeter JAR directly - bypasses problematic jmeter.bat
        java_exe = str(settings.java_home / "bin" / "java.exe")
        jmeter_jar = str(settings.jmeter_jar)
        jmeter_home = str(settings.tts_path)
        jmx_file = demo.jmx_path
        jtl_file = str(settings.runs_directory / f"{execution_id}.jtl")
        
        # Ensure runs directory exists
        settings.runs_directory.mkdir(parents=True, exist_ok=True)
        
        # Base Java command with JMeter properties
        cmd_parts = [
            f'"{java_exe}"',
            '-Xms512m -Xmx512m',  # Heap settings
            f'-Djava.util.logging.config.file="{jmeter_home}/bin/log.properties"',
            '-jar',
            f'"{jmeter_jar}"',
            '-n',  # Non-GUI mode
            '-t', f'"{jmx_file}"',  # Test plan
            '-l', f'"{jtl_file}"',  # Results file
        ]
        
        # Add parameters as -J properties
        for key, value in parameters.items():
            cmd_parts.append(f"-J{key}={value}")
        
        return " ".join(cmd_parts)
    
    async def get_execution_result(self, execution_id: str) -> Optional[ExecutionResult]:
        """Get execution result"""
        return self.active_executions.get(execution_id)
    
    async def cancel_execution(self, execution_id: str) -> bool:
        """Cancel running execution"""
        if execution_id not in self.processes:
            return False
        
        process = self.processes[execution_id]
        process.terminate()
        
        result = self.active_executions.get(execution_id)
        if result:
            result.status = ExecutionStatus.CANCELLED
            result.completed_at = datetime.utcnow()
        
        return True
    
    async def get_active_executions(self) -> Dict[str, ExecutionResult]:
        """Get all active executions"""
        return {
            eid: result for eid, result in self.active_executions.items()
            if result.status in [ExecutionStatus.QUEUED, ExecutionStatus.STARTING, ExecutionStatus.RUNNING]
        }
