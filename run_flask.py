"""
Simple script to run the Flask application locally
Usage: python run_flask.py
"""

from app import app, prisma

if __name__ == '__main__':
    # Connect to database
    try:
        prisma.connect()
        print("✅ Database connected")
    except Exception as e:
        print(f"⚠️  Warning: Could not connect to database: {e}")
        print("⚠️  Please update DATABASE_URL in backend/.env")
    
    # Run Flask app
    print("\n🚀 Starting Flask server...")
    print("📍 Server running at: http://localhost:8000")
    print("📖 API Documentation: http://localhost:8000/")
    print("\n⚠️  Press CTRL+C to quit\n")
    
    app.run(debug=True, host='0.0.0.0', port=8000)

