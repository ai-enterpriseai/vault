"""
Authentic Application Testing Framework for VAULT_APP v2.0
Real environment integration testing with genuine dependencies
"""

from .base_tester import AuthenticTester, TestResult
from .auth_client import AuthenticatedClient
from .data_manager import RealDataManager
from .performance import PerformanceMonitor

__version__ = "1.0.0"
__all__ = [
    "AuthenticTester",
    "TestResult", 
    "AuthenticatedClient",
    "RealDataManager",
    "PerformanceMonitor"
]