"""
Demo Service
Manages demo catalog loading and filtering
"""

from typing import List, Optional
from pathlib import Path
import json
from app.models import Demo
from app.config import settings


class DemoService:
    """Service for managing demo scenarios"""
    
    def __init__(self):
        self.demos: List[Demo] = []
        self._load_catalog()
    
    def _load_catalog(self):
        """Load demo catalog from JSON file"""
        try:
            # Build absolute path to demos.json in Java project
            if settings.demo_catalog_path.is_absolute():
                catalog_path = settings.demo_catalog_path
            else:
                # Resolve relative to backend directory (where run.py is located)
                backend_dir = Path(__file__).parent.parent.parent
                catalog_path = (backend_dir / settings.demo_catalog_path).resolve()
            
            print(f"Attempting to load demo catalog from: {catalog_path}")
            
            if not catalog_path.exists():
                print(f"Warning: Demo catalog not found at {catalog_path}")
                return
            
            with open(catalog_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                demos_data = data.get('demos', [])
                
                # Parse each demo with Pydantic (handles camelCase -> snake_case)
                self.demos = []
                for demo_data in demos_data:
                    try:
                        demo = Demo(**demo_data)
                        self.demos.append(demo)
                    except Exception as e:
                        print(f"Warning: Failed to parse demo {demo_data.get('id', 'unknown')}: {e}")
            
            print(f"Loaded {len(self.demos)} demos from catalog")
        
        except Exception as e:
            print(f"Error loading demo catalog: {e}")
            import traceback
            traceback.print_exc()
            self.demos = []
    
    async def get_all_demos(self) -> List[Demo]:
        """Get all demos"""
        return self.demos
    
    async def get_demo_by_id(self, demo_id: str) -> Optional[Demo]:
        """Get demo by ID"""
        return next((d for d in self.demos if d.id == demo_id), None)
    
    async def get_protocols(self) -> List[str]:
        """Get unique protocols"""
        return sorted(list(set(d.protocol for d in self.demos)))
    
    async def get_complexity_levels(self) -> List[str]:
        """Get unique complexity levels"""
        return sorted(list(set(d.complexity for d in self.demos)))
    
    async def filter_demos(self, protocol: Optional[str] = None, complexity: Optional[str] = None, search: Optional[str] = None) -> List[Demo]:
        """Filter demos by protocol, complexity, and search text"""
        filtered = self.demos
        
        if protocol:
            filtered = [d for d in filtered if d.protocol.upper() == protocol.upper()]
        
        if complexity:
            filtered = [d for d in filtered if d.complexity.upper() == complexity.upper()]
        
        if search:
            search_lower = search.lower()
            filtered = [
                d for d in filtered 
                if search_lower in d.title.lower() or search_lower in d.description.lower()
            ]
        
        return filtered
