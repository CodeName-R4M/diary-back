#!/bin/bash
# Optimized Prisma Setup for PythonAnywhere
# This script reduces disk usage by using nodejs-bin and cleaning caches

echo "🚀 Starting optimized Prisma setup for PythonAnywhere..."

# Step 1: Install nodejs-bin first (more reliable and smaller)
echo "📦 Installing nodejs-bin..."
pip install nodejs-bin

# Step 2: Install other dependencies
echo "📦 Installing Flask and other dependencies..."
pip install Flask Flask-Cors firebase-admin python-dotenv Werkzeug Pillow gunicorn

# Step 3: Install Prisma with nodejs-bin
echo "📦 Installing Prisma..."
pip install prisma

# Step 4: Generate Prisma client
echo "🔧 Generating Prisma client..."
python -m prisma generate

# Step 5: Clean up to save space
echo "🧹 Cleaning up to save disk space..."

# Remove pip cache
pip cache purge

# Remove Prisma cache (keep only generated client)
rm -rf ~/.cache/prisma-python/nodeenv/src
rm -rf ~/.cache/prisma-python/nodeenv/lib/node_modules/npm

# Remove unnecessary files from venv
find venv -type f -name "*.pyc" -delete
find venv -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null

echo "✅ Setup complete!"
echo ""
echo "📊 Disk usage summary:"
du -sh venv
du -sh ~/.cache/prisma-python
echo ""
echo "🎯 Next steps:"
echo "1. Run: python -m prisma db push"
echo "2. Configure your WSGI file"
echo "3. Reload your web app"

