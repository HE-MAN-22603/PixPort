#!/usr/bin/env python3
"""
PixPort Deployment Verification Script
Checks all dependencies, files, and configurations before deployment
"""

import os
import sys
import subprocess
import importlib
from pathlib import Path

def print_status(message, status="info"):
    """Print colored status messages"""
    colors = {
        "success": "\033[92m✅",
        "error": "\033[91m❌",
        "warning": "\033[93m⚠️ ",
        "info": "\033[94mℹ️ "
    }
    reset = "\033[0m"
    print(f"{colors.get(status, colors['info'])} {message}{reset}")

def check_python_version():
    """Check Python version compatibility"""
    version = sys.version_info
    if version.major == 3 and version.minor >= 8:
        print_status(f"Python {version.major}.{version.minor}.{version.micro} - Compatible", "success")
        return True
    else:
        print_status(f"Python {version.major}.{version.minor}.{version.micro} - Needs Python 3.8+", "error")
        return False

def check_required_files():
    """Check if all required files exist"""
    required_files = {
        "Core App Files": [
            "app.py",
            "wsgi.py", 
            "requirements.txt",
            ".gitignore"
        ],
        "ISNet Tiny Service": [
            "app_isnet_tiny.py",
            "requirements-isnet-tiny.txt",
            "Dockerfile.isnet-tiny",
            "test_isnet_tiny.py",
            "README-isnet-tiny.md"
        ],
        "App Structure": [
            "app/__init__.py",
            "app/services/isnet_tiny_service.py",
            "app/api/bg_removal_api.py"
        ],
        "Deployment Config": [
            "railway.toml",
            "DEPLOYMENT_GUIDE.md"
        ]
    }
    
    all_good = True
    for category, files in required_files.items():
        print(f"\n📁 Checking {category}:")
        for file_path in files:
            if os.path.exists(file_path):
                print_status(f"{file_path}", "success")
            else:
                print_status(f"{file_path} - MISSING", "error")
                all_good = False
    
    return all_good

def check_dependencies(requirements_file="requirements.txt"):
    """Check if dependencies can be imported"""
    print(f"\n📦 Checking dependencies from {requirements_file}:")
    
    try:
        with open(requirements_file, 'r') as f:
            lines = f.readlines()
    except FileNotFoundError:
        print_status(f"{requirements_file} not found", "error")
        return False
    
    # Extract package names from requirements
    packages = []
    for line in lines:
        line = line.strip()
        if line and not line.startswith('#'):
            # Handle package>=version format
            package_name = line.split('>=')[0].split('==')[0].split('<')[0].split('~=')[0]
            # Map some package names to import names
            import_name_mapping = {
                'opencv-python-headless': 'cv2',
                'Pillow': 'PIL',
                'Flask-Limiter': 'flask_limiter',
                'python-dotenv': 'dotenv'
            }
            import_name = import_name_mapping.get(package_name, package_name)
            packages.append((package_name, import_name))
    
    all_imported = True
    for package_name, import_name in packages:
        try:
            importlib.import_module(import_name)
            print_status(f"{package_name}", "success")
        except ImportError:
            print_status(f"{package_name} - Not installed", "warning")
            all_imported = False
        except Exception as e:
            print_status(f"{package_name} - Error: {e}", "error")
            all_imported = False
    
    return all_imported

def check_isnet_service():
    """Check ISNet Tiny service specifically"""
    print("\n🔧 Checking ISNet Tiny Service:")
    
    try:
        # Add current directory to Python path
        sys.path.insert(0, os.getcwd())
        
        # Try to import the service
        from app.services.isnet_tiny_service import isnet_tiny_service
        print_status("ISNet service import successful", "success")
        
        # Check memory usage function
        memory_info = isnet_tiny_service.get_memory_usage()
        print_status(f"Memory check: {memory_info}", "success")
        
        return True
        
    except ImportError as e:
        print_status(f"Import error: {e}", "error")
        return False
    except Exception as e:
        print_status(f"Service error: {e}", "warning")
        return False

def check_flask_apps():
    """Check if Flask apps can be imported"""
    print("\n🌐 Checking Flask Applications:")
    
    # Check main app
    try:
        import app
        print_status("Main app.py import successful", "success")
    except Exception as e:
        print_status(f"Main app.py error: {e}", "error")
    
    # Check ISNet tiny app
    try:
        import app_isnet_tiny
        print_status("app_isnet_tiny.py import successful", "success")
    except Exception as e:
        print_status(f"app_isnet_tiny.py error: {e}", "error")

def check_directory_structure():
    """Check app directory structure"""
    print("\n📂 Checking Directory Structure:")
    
    required_dirs = [
        "app",
        "app/services",
        "app/api",
        "app/static",
        "app/templates"
    ]
    
    for directory in required_dirs:
        if os.path.exists(directory):
            print_status(f"{directory}/", "success")
        else:
            print_status(f"{directory}/ - Missing", "warning")

def check_git_status():
    """Check git status and cleanliness"""
    print("\n📝 Checking Git Status:")
    
    try:
        # Check if git repo
        result = subprocess.run(['git', 'status', '--porcelain'], 
                              capture_output=True, text=True, check=True)
        
        if result.stdout.strip():
            print_status("Uncommitted changes found", "warning")
            print("  Run 'git status' to see changes")
        else:
            print_status("Git working directory clean", "success")
            
    except subprocess.CalledProcessError:
        print_status("Not a git repository or git not available", "warning")
    except FileNotFoundError:
        print_status("Git not installed", "warning")

def deployment_readiness_summary():
    """Provide deployment readiness summary"""
    print("\n" + "="*60)
    print("🚀 DEPLOYMENT READINESS SUMMARY")
    print("="*60)
    
    checks = [
        ("Python Version", check_python_version()),
        ("Required Files", check_required_files()),
        ("Main Dependencies", check_dependencies("requirements.txt")),
        ("ISNet Dependencies", check_dependencies("requirements-isnet-tiny.txt") if os.path.exists("requirements-isnet-tiny.txt") else True),
    ]
    
    # Additional checks
    try:
        checks.append(("ISNet Service", check_isnet_service()))
    except:
        checks.append(("ISNet Service", False))
    
    passed = sum(1 for _, status in checks if status)
    total = len(checks)
    
    print(f"\n📊 Results: {passed}/{total} checks passed")
    
    if passed == total:
        print_status("🎉 Ready for deployment!", "success")
        print("\nQuick deployment commands:")
        print("  ISNet Tiny: railway up (edit railway.toml startCommand first)")
        print("  Full App:   railway up")
    elif passed >= total - 1:
        print_status("⚠️  Nearly ready - minor issues found", "warning")
    else:
        print_status("❌ Not ready - please fix issues above", "error")
    
    return passed == total

def main():
    """Main verification function"""
    print("🔍 PixPort Deployment Verification")
    print("=" * 40)
    
    # Change to script directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # Run all checks
    check_python_version()
    check_required_files()
    check_directory_structure()
    check_dependencies("requirements.txt")
    
    if os.path.exists("requirements-isnet-tiny.txt"):
        check_dependencies("requirements-isnet-tiny.txt")
    
    check_flask_apps()
    check_isnet_service()
    check_git_status()
    
    # Final summary
    deployment_readiness_summary()

if __name__ == "__main__":
    main()
