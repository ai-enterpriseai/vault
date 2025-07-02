"""
Base testing framework for authentic application testing
Provides core functionality for testing with real environments and genuine dependencies
"""

import os
import sys
import time
import json
import psutil
import traceback
from typing import Dict, Any, List, Optional, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from pathlib import Path

# Add the backend to the path for imports
sys.path.append(str(Path(__file__).parent.parent.parent / "backend"))

try:
    import requests
    import asyncio
    import aiofiles
    import yaml
    ASYNC_AVAILABLE = True
except ImportError:
    ASYNC_AVAILABLE = False


@dataclass
class TestResult:
    """Container for test execution results with real metrics."""
    
    test_name: str
    success: bool
    execution_time: float
    start_time: str
    end_time: str
    environment: Dict[str, Any]
    data_characteristics: Dict[str, Any]
    performance_metrics: Dict[str, Any]
    error_details: Optional[str] = None
    warnings: List[str] = None
    artifacts: List[str] = None
    
    def __post_init__(self):
        if self.warnings is None:
            self.warnings = []
        if self.artifacts is None:
            self.artifacts = []
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)
    
    def save_to_file(self, filepath: Path) -> None:
        """Save test result to JSON file."""
        filepath.parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, 'w') as f:
            json.dump(self.to_dict(), f, indent=2, default=str)


class AuthenticTester:
    """
    Base class for authentic application testing with real environments.
    
    Provides infrastructure for testing against live dependencies with
    genuine data and authentic system conditions.
    """
    
    def __init__(self, config_path: Optional[Path] = None):
        """
        Initialize the authentic tester.
        
        Args:
            config_path: Path to configuration file with real environment settings
        """
        self.config_path = config_path or Path(__file__).parent.parent / "config" / "test_config.yaml"
        self.config: Dict[str, Any] = {}
        self.results: List[TestResult] = []
        self.session_id = f"test_session_{int(time.time())}"
        self.start_time = datetime.utcnow()
        
        # System monitoring
        self.process = psutil.Process()
        self.initial_memory = self.process.memory_info().rss
        self.initial_cpu_count = psutil.cpu_count()
        
        # Load real configuration
        self._load_authentic_config()
        
        # Validate real environment
        self._validate_real_environment()
    
    def _load_authentic_config(self) -> None:
        """Load configuration from real environment sources."""
        # Load from YAML config
        if self.config_path.exists():
            with open(self.config_path, 'r') as f:
                self.config = yaml.safe_load(f)
        
        # Override with environment variables (real production pattern)
        env_overrides = {
            'QDRANT_URL': os.getenv('QDRANT_URL'),
            'QDRANT_API_KEY': os.getenv('QDRANT_API_KEY'),
            'QDRANT_COLLECTION_NAME': os.getenv('QDRANT_COLLECTION_NAME'),
            'OPENAI_API_KEY': os.getenv('OPENAI_API_KEY'),
            'ANTHROPIC_API_KEY': os.getenv('ANTHROPIC_API_KEY'),
            'TOGETHER_API_KEY': os.getenv('TOGETHER_API_KEY'),
            'COHERE_API_KEY': os.getenv('COHERE_API_KEY'),
            'BACKEND_URL': os.getenv('BACKEND_URL', 'http://localhost:8000'),
            'TEST_DATA_PATH': os.getenv('TEST_DATA_PATH')
        }
        
        # Apply non-None environment overrides
        for key, value in env_overrides.items():
            if value is not None:
                self.config[key.lower()] = value
    
    def _validate_real_environment(self) -> None:
        """Validate that real dependencies are accessible."""
        validation_errors = []
        
        # Check required API keys
        required_keys = ['QDRANT_API_KEY', 'QDRANT_URL']
        for key in required_keys:
            if not self.config.get(key.lower()):
                validation_errors.append(f"Missing required configuration: {key}")
        
        # Check at least one AI model API key
        ai_keys = ['OPENAI_API_KEY', 'ANTHROPIC_API_KEY', 'TOGETHER_API_KEY']
        if not any(self.config.get(key.lower()) for key in ai_keys):
            validation_errors.append("At least one AI model API key is required")
        
        # Test network connectivity to real services
        if self.config.get('qdrant_url'):
            try:
                response = requests.get(f"{self.config['qdrant_url']}/collections", 
                                      timeout=5,
                                      headers={'api-key': self.config.get('qdrant_api_key', '')})
                if response.status_code == 401:
                    validation_errors.append("Qdrant API key authentication failed")
                elif response.status_code not in [200, 404]:
                    validation_errors.append(f"Qdrant service unreachable: {response.status_code}")
            except requests.RequestException as e:
                validation_errors.append(f"Cannot connect to Qdrant: {e}")
        
        if validation_errors:
            raise RuntimeError(f"Environment validation failed: {'; '.join(validation_errors)}")
    
    def capture_environment_state(self) -> Dict[str, Any]:
        """Capture current system state for test documentation."""
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "system": {
                "platform": sys.platform,
                "python_version": sys.version,
                "working_directory": str(Path.cwd()),
                "process_id": os.getpid()
            },
            "resources": {
                "cpu_count": psutil.cpu_count(),
                "memory_total": psutil.virtual_memory().total,
                "memory_available": psutil.virtual_memory().available,
                "disk_usage": psutil.disk_usage('/').percent if os.path.exists('/') else None
            },
            "network": {
                "hostname": os.getenv('HOSTNAME', 'unknown'),
                "external_ip": self._get_external_ip()
            },
            "configuration": {
                "backend_url": self.config.get('backend_url'),
                "qdrant_url": self.config.get('qdrant_url'),
                "test_data_path": self.config.get('test_data_path'),
                "session_id": self.session_id
            }
        }
    
    def _get_external_ip(self) -> Optional[str]:
        """Get external IP address for network condition documentation."""
        try:
            response = requests.get('https://api.ipify.org?format=text', timeout=5)
            return response.text.strip() if response.status_code == 200 else None
        except:
            return None
    
    def capture_performance_metrics(self) -> Dict[str, Any]:
        """Capture real system performance metrics."""
        current_memory = self.process.memory_info().rss
        cpu_percent = self.process.cpu_percent()
        
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "memory": {
                "current_rss": current_memory,
                "initial_rss": self.initial_memory,
                "delta_bytes": current_memory - self.initial_memory,
                "system_available": psutil.virtual_memory().available
            },
            "cpu": {
                "process_percent": cpu_percent,
                "system_percent": psutil.cpu_percent(),
                "load_average": os.getloadavg() if hasattr(os, 'getloadavg') else None
            },
            "io": {
                "read_count": self.process.io_counters().read_count if hasattr(self.process, 'io_counters') else None,
                "write_count": self.process.io_counters().write_count if hasattr(self.process, 'io_counters') else None
            }
        }
    
    async def execute_test(self, test_name: str, test_func: callable, 
                          test_data: Dict[str, Any] = None) -> TestResult:
        """
        Execute a single test with full monitoring and documentation.
        
        Args:
            test_name: Name of the test being executed
            test_func: Test function to execute (can be async or sync)
            test_data: Real test data to use
            
        Returns:
            TestResult with complete execution details
        """
        start_time = datetime.utcnow()
        start_timestamp = start_time.isoformat()
        
        # Capture initial state
        initial_env = self.capture_environment_state()
        initial_perf = self.capture_performance_metrics()
        
        try:
            # Execute test function
            if asyncio.iscoroutinefunction(test_func):
                await test_func(test_data or {})
            else:
                test_func(test_data or {})
            
            # Test completed successfully
            end_time = datetime.utcnow()
            execution_time = (end_time - start_time).total_seconds()
            final_perf = self.capture_performance_metrics()
            
            result = TestResult(
                test_name=test_name,
                success=True,
                execution_time=execution_time,
                start_time=start_timestamp,
                end_time=end_time.isoformat(),
                environment=initial_env,
                data_characteristics=self._analyze_test_data(test_data or {}),
                performance_metrics={
                    "initial": initial_perf,
                    "final": final_perf,
                    "execution_time_seconds": execution_time
                }
            )
            
        except Exception as e:
            # Test failed - capture failure details
            end_time = datetime.utcnow()
            execution_time = (end_time - start_time).total_seconds()
            final_perf = self.capture_performance_metrics()
            
            result = TestResult(
                test_name=test_name,
                success=False,
                execution_time=execution_time,
                start_time=start_timestamp,
                end_time=end_time.isoformat(),
                environment=initial_env,
                data_characteristics=self._analyze_test_data(test_data or {}),
                performance_metrics={
                    "initial": initial_perf,
                    "final": final_perf,
                    "execution_time_seconds": execution_time
                },
                error_details=f"{type(e).__name__}: {str(e)}\n{traceback.format_exc()}"
            )
        
        self.results.append(result)
        return result
    
    def _analyze_test_data(self, test_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze characteristics of test data for documentation."""
        analysis = {
            "data_type": type(test_data).__name__,
            "size_bytes": len(str(test_data).encode('utf-8')),
            "key_count": len(test_data) if isinstance(test_data, dict) else 0,
            "complexity": "simple" if len(test_data) < 10 else "complex"
        }
        
        # Analyze specific data types
        if isinstance(test_data, dict):
            for key, value in test_data.items():
                if key.endswith('_file') and isinstance(value, (str, Path)):
                    try:
                        file_path = Path(value)
                        if file_path.exists():
                            analysis[f"{key}_size"] = file_path.stat().st_size
                            analysis[f"{key}_type"] = file_path.suffix
                    except:
                        pass
        
        return analysis
    
    def generate_session_report(self) -> Dict[str, Any]:
        """Generate comprehensive report for the test session."""
        end_time = datetime.utcnow()
        session_duration = (end_time - self.start_time).total_seconds()
        
        # Calculate summary statistics
        total_tests = len(self.results)
        successful_tests = sum(1 for r in self.results if r.success)
        failed_tests = total_tests - successful_tests
        
        avg_execution_time = sum(r.execution_time for r in self.results) / total_tests if total_tests > 0 else 0
        
        return {
            "session_info": {
                "session_id": self.session_id,
                "start_time": self.start_time.isoformat(),
                "end_time": end_time.isoformat(),
                "duration_seconds": session_duration
            },
            "test_summary": {
                "total_tests": total_tests,
                "successful_tests": successful_tests,
                "failed_tests": failed_tests,
                "success_rate": successful_tests / total_tests if total_tests > 0 else 0,
                "average_execution_time": avg_execution_time
            },
            "environment": self.capture_environment_state(),
            "performance_summary": self.capture_performance_metrics(),
            "test_results": [result.to_dict() for result in self.results]
        }
    
    def save_session_report(self, output_dir: Path) -> Path:
        """Save comprehensive session report to file."""
        output_dir.mkdir(parents=True, exist_ok=True)
        
        report_file = output_dir / f"test_report_{self.session_id}.json"
        report_data = self.generate_session_report()
        
        with open(report_file, 'w') as f:
            json.dump(report_data, f, indent=2, default=str)
        
        return report_file