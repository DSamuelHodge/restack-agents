"""
Development helper script
Run this to check if everything is set up correctly
"""
import sys
import subprocess
from pathlib import Path


def check_python_version():
    """Check Python version"""
    version = sys.version_info
    if version.major == 3 and version.minor >= 10:
        print(f"✓ Python {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print(f"✗ Python {version.major}.{version.minor} (need 3.10+)")
        return False


def check_docker():
    """Check if Docker is running"""
    try:
        result = subprocess.run(
            ["docker", "ps"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            print("✓ Docker is running")
            return True
        else:
            print("✗ Docker is not running")
            return False
    except Exception as e:
        print(f"✗ Docker not found: {e}")
        return False


def check_restack_container():
    """Check if Restack container is running"""
    try:
        result = subprocess.run(
            ["docker", "ps", "--filter", "name=restack", "--format", "{{.Names}}"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if "restack" in result.stdout:
            print("✓ Restack container is running")
            return True
        else:
            print("✗ Restack container not found")
            print("  Run: docker run -d --pull always --name restack -p 5233:5233 -p 6233:6233 ghcr.io/restackio/restack:main")
            return False
    except Exception as e:
        print(f"✗ Cannot check Restack: {e}")
        return False


def check_env_file():
    """Check if .env file exists"""
    env_file = Path(".env")
    if env_file.exists():
        print("✓ .env file exists")
        return True
    else:
        print("✗ .env file not found")
        print("  Run: cp .env.example .env")
        return False


def check_dependencies():
    """Check if dependencies are installed"""
    try:
        import restack_ai
        print("✓ restack-ai installed")
        return True
    except ImportError:
        print("✗ Dependencies not installed")
        print("  Run: pip install -e .")
        return False


def check_structure():
    """Check project structure"""
    required_dirs = [
        "src/agents",
        "src/workflows",
        "src/functions",
        "src/models",
        "tests",
        "examples",
    ]
    
    all_exist = True
    for dir_path in required_dirs:
        if Path(dir_path).exists():
            print(f"✓ {dir_path}/")
        else:
            print(f"✗ {dir_path}/ missing")
            all_exist = False
    
    return all_exist


def main():
    """Run all checks"""
    print("="*60)
    print("BaseModel Agent - Environment Check")
    print("="*60)
    print()
    
    checks = {
        "Python version": check_python_version(),
        "Docker": check_docker(),
        "Restack container": check_restack_container(),
        "Environment file": check_env_file(),
        "Dependencies": check_dependencies(),
        "Project structure": check_structure(),
    }
    
    print()
    print("="*60)
    print("Summary")
    print("="*60)
    
    passed = sum(checks.values())
    total = len(checks)
    
    for check, result in checks.items():
        status = "PASS" if result else "FAIL"
        print(f"  {check:.<40} {status}")
    
    print()
    print(f"Result: {passed}/{total} checks passed")
    
    if passed == total:
        print()
        print("✓ All checks passed! You're ready to go.")
        print()
        print("Next steps:")
        print("  1. Terminal 1: python src/service.py")
        print("  2. Terminal 2: python src/schedule.py")
        print("  3. Browser: http://localhost:5233")
    else:
        print()
        print("⚠ Some checks failed. Please fix the issues above.")
        sys.exit(1)


if __name__ == "__main__":
    main()
