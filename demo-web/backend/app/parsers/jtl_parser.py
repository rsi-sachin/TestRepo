"""
JTL Parser - Extracts messages from JMeter JTL files
Supports real-time tailing and SIP message extraction
"""

from pathlib import Path
from typing import List, Dict, Optional, Callable
import csv
import re
from datetime import datetime


class JtlParser:
    """Parser for JMeter JTL (Java Test Log) files"""
    
    def __init__(self, jtl_file: Path):
        self.jtl_file = jtl_file
        self.last_position = 0
        
    def parse_statistics(self) -> Dict[str, any]:
        """
        Parse JTL file for basic statistics
        Returns: dict with total_attempts, successful, failed, success_rate
        """
        try:
            total_attempts = 0
            successful = 0
            failed = 0
            response_times = []
            
            with open(self.jtl_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                
                for row in reader:
                    total_attempts += 1
                    
                    # Check success column
                    success_flag = row.get('success', '').strip().lower()
                    if success_flag == 'true':
                        successful += 1
                    else:
                        failed += 1
                    
                    # Collect response times
                    try:
                        elapsed = int(row.get('elapsed', 0))
                        response_times.append(elapsed)
                    except:
                        pass
            
            success_rate = (successful / total_attempts * 100) if total_attempts > 0 else 0.0
            avg_response = sum(response_times) / len(response_times) if response_times else 0
            
            return {
                "total_attempts": total_attempts,
                "successful": successful,
                "failed": failed,
                "success_rate": round(success_rate, 2),
                "avg_response_time": round(avg_response, 2)
            }
        
        except Exception as e:
            print(f"Error parsing JTL statistics: {e}")
            return {
                "total_attempts": 0,
                "successful": 0,
                "failed": 0,
                "success_rate": 0.0,
                "avg_response_time": 0
            }
    
    def parse_sip_messages(self) -> List[Dict]:
        """
        Extract SIP messages from JTL file
        Returns list of SIP message dictionaries
        """
        sip_messages = []
        
        try:
            with open(self.jtl_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                
                for row in reader:
                    # Extract response data which may contain SIP messages
                    response_data = row.get('responseData', '') or row.get('responseMessage', '')
                    label = row.get('label', '')
                    timestamp = row.get('timeStamp', '')
                    
                    # Check if this is a SIP sampler
                    if 'SIP' in label or 'sip' in label.lower():
                        sip_msg = self._extract_sip_message(response_data, label, timestamp)
                        if sip_msg:
                            sip_messages.append(sip_msg)
            
            return sip_messages
        
        except Exception as e:
            print(f"Error parsing SIP messages: {e}")
            return []
    
    def _extract_sip_message(self, data: str, label: str, timestamp: str) -> Optional[Dict]:
        """
        Extract SIP message details from response data
        """
        if not data:
            return None
        
        try:
            # Parse SIP request/response line
            lines = data.split('\n')
            if not lines:
                return None
            
            first_line = lines[0].strip()
            
            # Determine if request or response
            if first_line.startswith('SIP/'):
                # Response: SIP/2.0 200 OK
                parts = first_line.split(' ', 2)
                if len(parts) >= 2:
                    response_code = parts[1]
                    response_text = parts[2] if len(parts) > 2 else ''
                    
                    return {
                        'timestamp': timestamp,
                        'type': 'response',
                        'method': None,
                        'response_code': response_code,
                        'response_text': response_text,
                        'from_actor': self._extract_from_header(data),
                        'to_actor': self._extract_to_header(data),
                        'call_id': self._extract_call_id(data),
                        'label': label
                    }
            else:
                # Request: INVITE sip:user@domain SIP/2.0
                parts = first_line.split(' ')
                if len(parts) >= 1:
                    method = parts[0]
                    
                    return {
                        'timestamp': timestamp,
                        'type': 'request',
                        'method': method,
                        'response_code': None,
                        'response_text': None,
                        'from_actor': self._extract_from_header(data),
                        'to_actor': self._extract_to_header(data),
                        'call_id': self._extract_call_id(data),
                        'label': label
                    }
        
        except Exception as e:
            print(f"Error extracting SIP message: {e}")
        
        return None
    
    def _extract_from_header(self, data: str) -> str:
        """Extract From header to determine source actor"""
        match = re.search(r'From:\s*.*?<sip:([^@>]+)', data, re.IGNORECASE)
        if match:
            return match.group(1)
        return "Unknown"
    
    def _extract_to_header(self, data: str) -> str:
        """Extract To header to determine destination actor"""
        match = re.search(r'To:\s*.*?<sip:([^@>]+)', data, re.IGNORECASE)
        if match:
            return match.group(1)
        return "Unknown"
    
    def _extract_call_id(self, data: str) -> str:
        """Extract Call-ID header"""
        match = re.search(r'Call-ID:\s*(.+)', data, re.IGNORECASE)
        if match:
            return match.group(1).strip()
        return ""
    
    def tail_new_lines(self, callback: Callable[[str], None]):
        """
        Tail JTL file for new lines (like 'tail -f')
        Calls callback for each new line
        """
        try:
            with open(self.jtl_file, 'r', encoding='utf-8') as f:
                # Seek to last known position
                f.seek(self.last_position)
                
                # Read new lines
                for line in f:
                    callback(line.rstrip())
                
                # Update position
                self.last_position = f.tell()
        
        except Exception as e:
            print(f"Error tailing JTL file: {e}")


class SipMessageSequencer:
    """
    Builds sequential representation of SIP call flows
    Tracks actors and message ordering for diagram generation
    """
    
    def __init__(self):
        self.messages = []
        self.actors = set()
        self.call_flows = {}  # Group by call_id
    
    def add_message(self, message: Dict):
        """Add a SIP message to the sequence"""
        self.messages.append(message)
        
        # Track actors
        if message.get('from_actor'):
            self.actors.add(message['from_actor'])
        if message.get('to_actor'):
            self.actors.add(message['to_actor'])
        
        # Group by call_id
        call_id = message.get('call_id', 'default')
        if call_id not in self.call_flows:
            self.call_flows[call_id] = []
        self.call_flows[call_id].append(message)
    
    def get_mermaid_diagram(self, call_id: Optional[str] = None) -> str:
        """
        Generate Mermaid.js sequence diagram syntax
        
        Args:
            call_id: Specific call ID, or None for all messages
        
        Returns:
            Mermaid diagram as string
        """
        messages = self.messages if call_id is None else self.call_flows.get(call_id, [])
        
        if not messages:
            return ""
        
        # Build Mermaid diagram
        lines = ["sequenceDiagram"]
        
        # Add participants (actors)
        actors = sorted(self.actors)
        for actor in actors:
            lines.append(f"    participant {actor}")
        
        # Add messages
        for msg in messages:
            from_actor = msg.get('from_actor', 'Unknown')
            to_actor = msg.get('to_actor', 'Unknown')
            
            if msg['type'] == 'request':
                method = msg.get('method', 'UNKNOWN')
                lines.append(f"    {from_actor}->>{to_actor}: {method}")
            else:
                code = msg.get('response_code', '???')
                text = msg.get('response_text', '')
                lines.append(f"    {to_actor}-->>{from_actor}: {code} {text}")
        
        return '\n'.join(lines)
