"""
Application Configuration
Environment variables and settings
"""

from pydantic_settings import BaseSettings
from pathlib import Path
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment or defaults"""
    
    # Application
    app_name: str = "TTS Demo Tool Web"
    app_version: str = "2.0.0"
    debug: bool = True
    
    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    
    # TTS Installation (read-only reference)
    tts_path: Path = Path("C:/TTS")
    jmeter_command: Path = Path("C:/TTS/bin/jmeter.bat")
    jmeter_jar: Path = Path("C:/TTS/bin/ApacheJMeter.jar")
    java_home: Path = Path("C:/jdk-11.0.30")  # Java for JMeter
    
    # Demo Catalog
    demo_catalog_path: Path = Path("../../demo-tool/src/main/resources/data/demos.json")
    
    # Data Directories
    runs_directory: Path = Path("../../demo-tool/runs")
    logs_directory: Path = Path("./logs")
    
    # WebSocket
    ws_ping_interval: int = 20
    ws_ping_timeout: int = 20
    
    # CORS
    cors_origins: list[str] = ["http://localhost:8000", "http://localhost:3000"]
    
    # Execution
    max_concurrent_demos: int = 3
    demo_timeout_seconds: int = 600
    
    # ORAN Configuration
    oran_install_path: Optional[Path] = None
    oran_cli_path: Optional[Path] = None
    oran_ric_endpoint: str = "http://localhost:8080"
    oran_du_simulation: bool = True
    oran_catalogs_path: Optional[Path] = None  # Defaults to runs_directory/oran_catalogs
    oran_generated_tests_path: Optional[Path] = None  # Defaults to tts_path/generated_tests
    oran_history_path: Optional[Path] = None  # Defaults to runs_directory/oran_history
    
    # ORAN test extraction limits (MVP constraint)
    max_tests_per_spec: int = 2  # Maximum tests to extract per specification (MVP: 2 tests x 4 docs = 8 total)

    # ORAN docs folder — searched first before requiring manual upload
    # Defaults to ORAN/docs relative to the repo root (3 levels up from backend/)
    oran_docs_path: Optional[Path] = None  # Falls back to Path('../../ORAN/docs') at runtime
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Global settings instance
settings = Settings()


def validate_installation() -> bool:
    """Validate TTS/JMeter installation"""
    if not settings.jmeter_command.exists():
        print(f"Warning: JMeter not found at {settings.jmeter_command}")
        return False
    return True


def validate_demo_catalog() -> bool:
    """Validate demo catalog file exists"""
    if not settings.demo_catalog_path.exists():
        print(f"Warning: Demo catalog not found at {settings.demo_catalog_path}")
        return False
    return True
