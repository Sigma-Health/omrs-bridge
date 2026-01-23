#!/usr/bin/env python3
"""
Development Server Starter Script
This script helps you start the FastAPI development server with proper setup checks.
"""

import os
import sys
import subprocess
import platform
from pathlib import Path


def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 11):
        print("❌ Python 3.11 or higher is required")
        print(f"Current version: {sys.version}")
        return False
    print(f"✅ Python version: {sys.version.split()[0]}")
    return True


def check_virtual_environment():
    """Check if virtual environment is activated"""
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("✅ Virtual environment is activated")
        return True
    else:
        print("⚠️  Virtual environment is not activated")
        print("Please activate it first:")
        if platform.system() == "Windows":
            print("  venv\\Scripts\\activate")
        else:
            print("  source venv/bin/activate")
        return False


def check_dependencies():
    """Check if required packages are installed"""
    required_packages = [
        'fastapi', 'uvicorn', 'sqlalchemy', 'pymysql', 
        'pydantic', 'dotenv'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} - not installed")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\nMissing packages: {', '.join(missing_packages)}")
        print("Install them with: pip install -r requirements.txt")
        return False
    return True


def check_env_file():
    """Check if .env file exists"""
    env_file = Path('.env')
    if env_file.exists():
        print("✅ .env file found")
        return True
    else:
        print("⚠️  .env file not found")
        print("Create it by copying env.example:")
        print("  cp env.example .env")
        print("Then edit it with your database credentials")
        return False


def check_app_structure():
    """Check if app structure is correct"""
    required_files = [
        'app/main.py',
        'app/config.py',
        'app/database.py',
        'app/models.py',
        'app/schemas.py',
        'app/auth.py',
        'app/crud.py',
        'app/api/orders.py'
    ]
    
    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
    
    if missing_files:
        print(f"❌ Missing files: {', '.join(missing_files)}")
        return False
    
    print("✅ App structure is correct")
    return True


def start_server():
    """Start the development server"""
    print("\n🚀 Starting FastAPI development server...")
    print("=" * 50)
    
    try:
        # Start uvicorn server
        cmd = [
            sys.executable, '-m', 'uvicorn',
            'app.main:app',
            '--host', '0.0.0.0',
            '--port', '1221',
            '--reload'
        ]
        
        subprocess.run(cmd)
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
    except Exception as e:
        print(f"❌ Failed to start server: {e}")


def main():
    """Main function"""
    print("🔧 OpenMRS Bridge API - Development Server Setup")
    print("=" * 50)
    
    # Run checks
    checks = [
        ("Python Version", check_python_version),
        ("Virtual Environment", check_virtual_environment),
        ("Dependencies", check_dependencies),
        ("Environment File", check_env_file),
        ("App Structure", check_app_structure),
    ]
    
    all_passed = True
    for check_name, check_func in checks:
        print(f"\n🔍 Checking {check_name}...")
        if not check_func():
            all_passed = False
    
    print("\n" + "=" * 50)
    
    if all_passed:
        print("✅ All checks passed! Starting server...")
        start_server()
    else:
        print("❌ Some checks failed. Please fix the issues above before starting the server.")
        print("\n📖 For help, see the README.md file")
        sys.exit(1)


if __name__ == "__main__":
    main() 