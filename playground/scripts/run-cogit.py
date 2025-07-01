#!/usr/bin/env python3
"""
Runner script for the Cogit application.
This script properly sets up the path and runs the Cogit app from its new location.
"""

import sys
import os
from pathlib import Path

def setup_environment():
    """Setup the Python path to include necessary directories."""
    # Add the workspace root to the Python path
    workspace_root = Path(__file__).parent.parent.parent
    sys.path.insert(0, str(workspace_root))
    
    # Change to workspace root directory
    os.chdir(workspace_root)
    
    print(f"📁 Working directory: {os.getcwd()}")
    print(f"🐍 Python path includes: {workspace_root}")

def run_cogit():
    """Run the Cogit application."""
    try:
        # Import and run the Cogit app
        import importlib.util
        
        spec = importlib.util.spec_from_file_location(
            "cogit_app", 
            "Cogit/app-cogit.py"
        )
        
        if spec is None or spec.loader is None:
            print("❌ Could not load Cogit app specification")
            return
            
        cogit_module = importlib.util.module_from_spec(spec)
        
        print("🚀 Starting Cogit application...")
        spec.loader.exec_module(cogit_module)
        
        # Run the main function
        if hasattr(cogit_module, 'main'):
            cogit_module.main()
        else:
            print("❌ No main function found in Cogit app")
            
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("💡 Make sure all dependencies are installed")
    except Exception as e:
        print(f"❌ Error running Cogit: {e}")

def main():
    """Main function."""
    print("🎯 Cogit Application Runner")
    print("=" * 40)
    
    setup_environment()
    run_cogit()

if __name__ == "__main__":
    main()