#!/usr/bin/env python3
"""
Environment Setup Script for VAULT_APP v2.0 Authentic Testing Framework
Prepares real environment for integration testing with genuine dependencies
"""

import os
import sys
import subprocess
import json
from pathlib import Path
from typing import Dict, Any, List

def print_banner():
    """Print setup banner."""
    banner = """
╔══════════════════════════════════════════════════════════════════════════════╗
║                VAULT_APP v2.0 Authentic Testing Environment Setup           ║
║                                                                              ║
║  🔧 Preparing REAL environment for integration testing                      ║
║  📋 Validating dependencies and configurations                              ║
║  🚀 Ready for production-scale testing                                      ║
╚══════════════════════════════════════════════════════════════════════════════╝
    """
    print(banner)

def check_python_requirements() -> bool:
    """Check Python version and required packages."""
    print("\n🐍 Python Environment Check")
    print("-" * 40)
    
    # Check Python version
    python_version = sys.version_info
    if python_version < (3, 8):
        print(f"❌ Python {python_version.major}.{python_version.minor} detected. Python 3.8+ required.")
        return False
    else:
        print(f"✅ Python {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    # Check required packages
    required_packages = [
        'requests',
        'asyncio',
        'yaml', 
        'psutil',
        'aiofiles'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} (missing)")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n📦 Install missing packages:")
        print(f"   pip install {' '.join(missing_packages)}")
        return False
    
    return True

def check_optional_packages() -> Dict[str, bool]:
    """Check optional packages for enhanced functionality."""
    print("\n📦 Optional Packages Check")
    print("-" * 40)
    
    optional_packages = {
        'qdrant_client': 'Qdrant vector database integration',
        'websockets': 'WebSocket testing support',
        'aiohttp': 'Async HTTP client support',
        'structlog': 'Structured logging',
        'pytest': 'Advanced testing features'
    }
    
    package_status = {}
    for package, description in optional_packages.items():
        try:
            __import__(package)
            print(f"✅ {package} - {description}")
            package_status[package] = True
        except ImportError:
            print(f"⚠️ {package} - {description} (optional)")
            package_status[package] = False
    
    return package_status

def setup_configuration_files():
    """Setup configuration files from templates."""
    print("\n⚙️ Configuration Setup")
    print("-" * 40)
    
    config_dir = Path(__file__).parent.parent / "config"
    
    # Check for existing .env file
    env_file = config_dir / "prod_like.env"
    env_example = config_dir / "prod_like.env.example"
    
    if not env_file.exists() and env_example.exists():
        print(f"📝 Creating environment configuration...")
        
        # Copy example to actual file
        with open(env_example, 'r') as f:
            content = f.read()
        
        with open(env_file, 'w') as f:
            f.write(content)
        
        print(f"✅ Created {env_file}")
        print(f"⚠️ IMPORTANT: Edit {env_file} with your real API keys!")
    elif env_file.exists():
        print(f"✅ Environment file exists: {env_file}")
    else:
        print(f"❌ No environment template found")
        return False
    
    # Check test config
    test_config = config_dir / "test_config.yaml"
    if test_config.exists():
        print(f"✅ Test configuration: {test_config}")
    else:
        print(f"❌ Test configuration missing: {test_config}")
        return False
    
    return True

def create_directory_structure():
    """Create required directory structure."""
    print("\n📁 Directory Structure Setup")
    print("-" * 40)
    
    base_dir = Path(__file__).parent.parent
    required_dirs = [
        "data/documents",
        "data/conversations", 
        "data/user_scenarios",
        "results/reports",
        "results/metrics",
        "results/failures"
    ]
    
    for dir_path in required_dirs:
        full_path = base_dir / dir_path
        full_path.mkdir(parents=True, exist_ok=True)
        print(f"✅ {dir_path}")
    
    return True

def validate_backend_connectivity() -> bool:
    """Test connectivity to VAULT_APP backend."""
    print("\n🌐 Backend Connectivity Check")
    print("-" * 40)
    
    try:
        import requests
        
        # Try default backend URL
        backend_urls = [
            "http://localhost:8000",
            "http://127.0.0.1:8000"
        ]
        
        for url in backend_urls:
            try:
                response = requests.get(f"{url}/health", timeout=5)
                if response.status_code == 200:
                    print(f"✅ Backend accessible: {url}")
                    return True
                else:
                    print(f"⚠️ Backend unhealthy: {url} (status: {response.status_code})")
            except requests.RequestException:
                print(f"❌ Backend unreachable: {url}")
        
        print("\n🚀 Backend Setup Instructions:")
        print("   1. Navigate to cogit/backend directory")
        print("   2. Install dependencies: pip install -r requirements.txt")
        print("   3. Start server: uvicorn main:app --reload --port 8000")
        
        return False
        
    except ImportError:
        print("❌ requests package required for connectivity check")
        return False

def validate_database_connectivity() -> bool:
    """Test connectivity to Qdrant database."""
    print("\n🗄️ Database Connectivity Check")
    print("-" * 40)
    
    try:
        import requests
        
        # Try default Qdrant URLs
        qdrant_urls = [
            "http://localhost:6333",
            "http://127.0.0.1:6333"
        ]
        
        for url in qdrant_urls:
            try:
                response = requests.get(f"{url}/collections", timeout=5)
                if response.status_code in [200, 401, 404]:  # 401 means auth required (ok), 404 means no collections (ok)
                    print(f"✅ Qdrant accessible: {url}")
                    return True
                else:
                    print(f"⚠️ Qdrant response: {url} (status: {response.status_code})")
            except requests.RequestException:
                print(f"❌ Qdrant unreachable: {url}")
        
        print("\n🐳 Qdrant Setup Instructions:")
        print("   Option 1 - Docker:")
        print("   docker run -p 6333:6333 qdrant/qdrant")
        print("   ")
        print("   Option 2 - Cloud:")
        print("   Sign up at https://cloud.qdrant.io")
        
        return False
        
    except ImportError:
        print("❌ requests package required for connectivity check")
        return False

def generate_test_dependencies_report() -> Dict[str, Any]:
    """Generate comprehensive dependencies report."""
    print("\n📊 Dependencies Report")
    print("-" * 40)
    
    report = {
        "timestamp": str(Path(__file__).stat().st_mtime),
        "python": {
            "version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            "executable": sys.executable
        },
        "packages": {},
        "connectivity": {},
        "environment": {
            "platform": sys.platform,
            "cwd": str(Path.cwd())
        }
    }
    
    # Check package versions
    packages_to_check = [
        'requests', 'asyncio', 'yaml', 'psutil', 'aiofiles',
        'qdrant_client', 'websockets', 'aiohttp', 'structlog', 'pytest'
    ]
    
    for package in packages_to_check:
        try:
            module = __import__(package)
            version = getattr(module, '__version__', 'unknown')
            report["packages"][package] = {"available": True, "version": version}
        except ImportError:
            report["packages"][package] = {"available": False, "version": None}
    
    # Save report
    reports_dir = Path(__file__).parent.parent / "results" / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)
    
    report_file = reports_dir / "environment_setup_report.json"
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"✅ Dependencies report: {report_file}")
    return report

def main():
    """Main setup function."""
    print_banner()
    
    success = True
    
    # Check Python requirements
    if not check_python_requirements():
        success = False
    
    # Check optional packages
    optional_status = check_optional_packages()
    
    # Setup configuration
    if not setup_configuration_files():
        success = False
    
    # Create directories
    if not create_directory_structure():
        success = False
    
    # Test connectivity (warnings only, not failures)
    backend_ok = validate_backend_connectivity()
    database_ok = validate_database_connectivity()
    
    # Generate report
    report = generate_test_dependencies_report()
    
    # Print final status
    print("\n" + "=" * 80)
    print("🎯 ENVIRONMENT SETUP SUMMARY")
    print("=" * 80)
    
    if success:
        print("✅ Core requirements satisfied")
    else:
        print("❌ Core requirements missing - install dependencies first")
    
    if backend_ok:
        print("✅ Backend connectivity confirmed")
    else:
        print("⚠️ Backend not running - start VAULT_APP backend for testing")
    
    if database_ok:
        print("✅ Database connectivity confirmed")
    else:
        print("⚠️ Database not accessible - setup Qdrant for testing")
    
    # Recommendations
    print(f"\n📋 NEXT STEPS:")
    
    if not success:
        print(f"   1. Install missing Python packages")
    
    if not backend_ok:
        print(f"   2. Start VAULT_APP backend server")
    
    if not database_ok:
        print(f"   3. Setup Qdrant vector database")
    
    print(f"   4. Configure API keys in cogit/testing/config/prod_like.env")
    print(f"   5. Run tests: python scripts/run_all_tests.py --authentic")
    
    # Exit code
    exit_code = 0 if success else 1
    if not backend_ok or not database_ok:
        exit_code = 2  # Warnings
    
    print(f"\n🎯 Setup {'COMPLETE' if exit_code == 0 else 'INCOMPLETE' if exit_code == 1 else 'READY (with warnings)'}")
    
    return exit_code

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)