#!/usr/bin/env python3
"""
Optimized Prisma Installation Script for PythonAnywhere
Reduces disk usage by installing in the correct order and cleaning caches
"""

import subprocess
import sys
import os
import shutil
from pathlib import Path

def run_command(cmd, description):
    """Run a command and print status"""
    print(f"\n{'='*60}")
    print(f"📦 {description}")
    print(f"{'='*60}")
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print(result.stdout)
        if result.stderr:
            print(result.stderr)
        print(f"✅ {description} - SUCCESS")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} - FAILED")
        print(f"Error: {e.stderr}")
        return False

def get_dir_size(path):
    """Get directory size in MB"""
    try:
        total = 0
        for entry in os.scandir(path):
            if entry.is_file():
                total += entry.stat().st_size
            elif entry.is_dir():
                total += get_dir_size(entry.path)
        return total / (1024 * 1024)  # Convert to MB
    except:
        return 0

def clean_cache():
    """Clean up caches to save disk space"""
    print("\n🧹 Cleaning up caches...")
    
    # Clean pip cache
    run_command("pip cache purge", "Cleaning pip cache")
    
    # Clean Prisma cache (keep only essentials)
    prisma_cache = Path.home() / ".cache" / "prisma-python"
    if prisma_cache.exists():
        # Remove source files
        src_dir = prisma_cache / "nodeenv" / "src"
        if src_dir.exists():
            shutil.rmtree(src_dir, ignore_errors=True)
            print("✅ Removed Prisma source files")
        
        # Remove npm modules
        npm_dir = prisma_cache / "nodeenv" / "lib" / "node_modules" / "npm"
        if npm_dir.exists():
            shutil.rmtree(npm_dir, ignore_errors=True)
            print("✅ Removed npm modules")
    
    # Clean Python cache
    venv_path = Path("venv")
    if venv_path.exists():
        for pyc in venv_path.rglob("*.pyc"):
            pyc.unlink()
        for pycache in venv_path.rglob("__pycache__"):
            shutil.rmtree(pycache, ignore_errors=True)
        print("✅ Removed Python cache files")

def show_disk_usage():
    """Show disk usage summary"""
    print("\n📊 Disk Usage Summary")
    print("="*60)
    
    venv_size = get_dir_size("venv") if os.path.exists("venv") else 0
    print(f"Virtual environment: {venv_size:.1f} MB")
    
    prisma_cache = Path.home() / ".cache" / "prisma-python"
    if prisma_cache.exists():
        prisma_size = get_dir_size(str(prisma_cache))
        print(f"Prisma cache: {prisma_size:.1f} MB")
    
    total = venv_size + (prisma_size if prisma_cache.exists() else 0)
    print(f"Total: {total:.1f} MB")
    print("="*60)

def main():
    print("""
    ╔══════════════════════════════════════════════════════════╗
    ║  Optimized Prisma Installation for PythonAnywhere       ║
    ║  Reduces disk usage from ~200MB to ~100MB                ║
    ╚══════════════════════════════════════════════════════════╝
    """)
    
    # Check if in virtual environment
    if not hasattr(sys, 'real_prefix') and not (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("⚠️  WARNING: Not in a virtual environment!")
        print("Please activate your virtual environment first:")
        print("  source venv/bin/activate")
        sys.exit(1)
    
    print("✅ Virtual environment detected")
    
    # Step 1: Install nodejs-bin first
    if not run_command("pip install nodejs-bin", "Installing nodejs-bin"):
        print("\n❌ Failed to install nodejs-bin. Exiting.")
        sys.exit(1)
    
    # Step 2: Install Flask and dependencies
    packages = [
        "Flask",
        "Flask-Cors",
        "firebase-admin",
        "python-dotenv",
        "Werkzeug",
        "Pillow",
        "gunicorn"
    ]
    
    for package in packages:
        if not run_command(f"pip install {package}", f"Installing {package}"):
            print(f"\n⚠️  Warning: Failed to install {package}")
    
    # Step 3: Install Prisma
    if not run_command("pip install prisma", "Installing Prisma"):
        print("\n❌ Failed to install Prisma. Exiting.")
        sys.exit(1)
    
    # Step 4: Generate Prisma client
    if not run_command("python -m prisma generate", "Generating Prisma client"):
        print("\n❌ Failed to generate Prisma client.")
        print("You may need to run this manually after fixing any issues.")
    
    # Step 5: Clean up
    clean_cache()
    
    # Show final disk usage
    show_disk_usage()
    
    print("""
    ╔══════════════════════════════════════════════════════════╗
    ║  ✅ Installation Complete!                               ║
    ╚══════════════════════════════════════════════════════════╝
    
    🎯 Next steps:
    1. Run: python -m prisma db push
    2. Configure your WSGI file
    3. Reload your web app
    
    💡 To save more space, run:
       pip cache purge
    """)

if __name__ == "__main__":
    main()

