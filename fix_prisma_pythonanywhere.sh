#!/bin/bash
# Fix Prisma on PythonAnywhere - Bypass checksum verification
# This is needed because PythonAnywhere blocks some Prisma CDN requests

echo "🔧 Fixing Prisma for PythonAnywhere..."

# Set environment variable to ignore missing checksums
export PRISMA_ENGINES_CHECKSUM_IGNORE_MISSING=1

# Also add it to your shell profile for future sessions
echo 'export PRISMA_ENGINES_CHECKSUM_IGNORE_MISSING=1' >> ~/.bashrc

echo "✅ Environment variable set"

# Generate Prisma client
echo "📦 Generating Prisma client..."
python -m prisma generate

if [ $? -eq 0 ]; then
    echo "✅ Prisma client generated successfully!"
    
    # Push database schema
    echo "📊 Pushing database schema..."
    python -m prisma db push
    
    if [ $? -eq 0 ]; then
        echo "✅ Database schema pushed successfully!"
        echo ""
        echo "🎉 All done! Your Prisma setup is complete."
        echo ""
        echo "📝 Next steps:"
        echo "1. Configure your WSGI file"
        echo "2. Add your .env file with DATABASE_URL"
        echo "3. Add firebase-credentials.json"
        echo "4. Reload your web app"
    else
        echo "❌ Failed to push database schema"
        echo "Make sure your DATABASE_URL is correct in .env file"
    fi
else
    echo "❌ Failed to generate Prisma client"
    echo "Please check the error messages above"
fi

