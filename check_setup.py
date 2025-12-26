"""
Setup verification script for Personal Diary Backend
Run this to check if everything is configured correctly
"""

import os
import sys
from pathlib import Path

def check_file_exists(filepath, description):
    """Check if a file exists"""
    if os.path.exists(filepath):
        print(f"✅ {description}: Found")
        return True
    else:
        print(f"❌ {description}: NOT FOUND")
        print(f"   Expected at: {filepath}")
        return False

def check_env_variable(var_name):
    """Check if environment variable is set"""
    value = os.getenv(var_name)
    if value and value != f"your_{var_name.lower()}_here":
        print(f"✅ {var_name}: Set")
        return True
    else:
        print(f"❌ {var_name}: NOT SET or using example value")
        return False

def main():
    print("=" * 60)
    print("Personal Diary Backend - Setup Verification")
    print("=" * 60)
    print()
    
    all_good = True
    
    # Check Python version
    print("📋 Checking Python Version...")
    python_version = sys.version_info
    if python_version.major >= 3 and python_version.minor >= 9:
        print(f"✅ Python {python_version.major}.{python_version.minor}.{python_version.micro}")
    else:
        print(f"❌ Python version too old: {python_version.major}.{python_version.minor}")
        print("   Need Python 3.9 or higher")
        all_good = False
    print()
    
    # Check required files
    print("📁 Checking Required Files...")
    all_good &= check_file_exists("requirements.txt", "requirements.txt")
    all_good &= check_file_exists("schema.prisma", "schema.prisma")
    all_good &= check_file_exists("main.py", "main.py")
    all_good &= check_file_exists(".env", ".env file")
    all_good &= check_file_exists("firebase-credentials.json", "Firebase credentials")
    print()
    
    # Check if uploads directory exists or can be created
    print("📂 Checking Uploads Directory...")
    uploads_dir = Path("./uploads")
    if uploads_dir.exists():
        print("✅ Uploads directory exists")
    else:
        try:
            uploads_dir.mkdir(exist_ok=True)
            print("✅ Uploads directory created")
        except Exception as e:
            print(f"❌ Could not create uploads directory: {e}")
            all_good = False
    print()
    
    # Load .env file
    print("🔧 Checking Environment Variables...")
    try:
        from dotenv import load_dotenv
        load_dotenv()
        print("✅ .env file loaded")
    except ImportError:
        print("❌ python-dotenv not installed")
        print("   Run: pip install python-dotenv")
        all_good = False
    except Exception as e:
        print(f"❌ Error loading .env: {e}")
        all_good = False
    
    all_good &= check_env_variable("DATABASE_URL")
    print()
    
    # Check if required packages are installed
    print("📦 Checking Required Packages...")
    required_packages = [
        "fastapi",
        "uvicorn",
        "prisma",
        "firebase_admin",
        "python_dotenv",
        "aiofiles"
    ]
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package}: Installed")
        except ImportError:
            print(f"❌ {package}: NOT INSTALLED")
            all_good = False
    print()
    
    # Check Prisma
    print("🔍 Checking Prisma Setup...")
    prisma_client = Path("./prisma")
    if prisma_client.exists():
        print("✅ Prisma client directory exists")
    else:
        print("⚠️  Prisma client not generated")
        print("   Run: prisma generate")
        all_good = False
    print()
    
    # Final summary
    print("=" * 60)
    if all_good:
        print("🎉 All checks passed! You're ready to run the backend!")
        print()
        print("Next steps:")
        print("1. Make sure your NeonDB database is accessible")
        print("2. Run: prisma db push (if not done already)")
        print("3. Run: uvicorn main:app --reload --port 8000")
    else:
        print("⚠️  Some checks failed. Please fix the issues above.")
        print()
        print("Common fixes:")
        print("1. Install dependencies: pip install -r requirements.txt")
        print("2. Create .env file: copy .env.example .env")
        print("3. Add your Firebase credentials JSON file")
        print("4. Generate Prisma client: prisma generate")
    print("=" * 60)

if __name__ == "__main__":
    main()

