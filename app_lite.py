"""
Lightweight Flask Backend for PythonAnywhere
Uses psycopg2 instead of Prisma to save disk space (~5MB vs ~200MB)
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import psycopg2
from psycopg2.extras import RealDictCursor
import firebase_admin
from firebase_admin import credentials, auth
from functools import wraps
import os
from datetime import datetime
from pathlib import Path
import uuid
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()

# Initialize Flask
app = Flask(__name__)

# CORS configuration
CORS(app, resources={
    r"/api/*": {
        "origins": ["http://localhost:5173", "http://localhost:3000", "*"],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

# Database connection
def get_db_connection():
    """Create a database connection"""
    try:
        conn = psycopg2.connect(os.getenv("DATABASE_URL"))
        return conn
    except Exception as e:
        print(f"Database connection error: {e}")
        return None

# Initialize Firebase Admin
firebase_creds_path = os.getenv("FIREBASE_CREDENTIALS_PATH", "./firebase-credentials.json")
firebase_initialized = False
if os.path.exists(firebase_creds_path):
    try:
        cred = credentials.Certificate(firebase_creds_path)
        firebase_admin.initialize_app(cred)
        firebase_initialized = True
        print("✅ Firebase Admin initialized successfully")
    except Exception as e:
        print(f"⚠️  Warning: Could not initialize Firebase Admin: {e}")
else:
    print("⚠️  Warning: Firebase credentials file not found")

# Upload directory
UPLOAD_DIR = Path(os.getenv("UPLOAD_DIR", "./uploads"))
UPLOAD_DIR.mkdir(exist_ok=True)

# Allowed file extensions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Decorator to verify Firebase token
def require_auth(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not firebase_initialized:
            return jsonify({
                "error": "Firebase authentication not configured",
                "detail": "Please add valid Firebase credentials"
            }), 503
        
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({"error": "Missing or invalid authorization header"}), 401
        
        try:
            token = auth_header.split('Bearer ')[1]
            decoded_token = auth.verify_id_token(token)
            request.user_id = decoded_token['uid']
            return f(*args, **kwargs)
        except Exception as e:
            return jsonify({"error": "Invalid authentication credentials", "detail": str(e)}), 401
    
    return decorated_function

# Root endpoint
@app.route('/')
def root():
    return jsonify({"message": "Personal Diary API (Lightweight)", "status": "running"})

# Create diary entry
@app.route('/api/diary/entries', methods=['POST'])
@require_auth
def create_diary_entry():
    """Create a new diary entry with optional image"""
    try:
        content = request.form.get('content')
        title = request.form.get('title')
        user_id = request.user_id
        
        if not content:
            return jsonify({"error": "Content is required"}), 400
        
        image_url = None
        
        # Handle image upload
        if 'image' in request.files:
            image = request.files['image']
            if image and image.filename and allowed_file(image.filename):
                file_extension = os.path.splitext(secure_filename(image.filename))[1]
                unique_filename = f"{user_id}_{uuid.uuid4()}{file_extension}"
                file_path = UPLOAD_DIR / unique_filename
                image.save(str(file_path))
                image_url = f"/uploads/{unique_filename}"
        
        # Insert into database
        conn = get_db_connection()
        if not conn:
            return jsonify({"error": "Database connection failed"}), 500
        
        try:
            cur = conn.cursor(cursor_factory=RealDictCursor)
            cur.execute(
                """
                INSERT INTO "DiaryEntry" ("id", "userId", "title", "content", "imageUrl", "createdAt", "updatedAt")
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                RETURNING *
                """,
                (str(uuid.uuid4()), user_id, title, content, image_url, datetime.utcnow(), datetime.utcnow())
            )
            entry = cur.fetchone()
            conn.commit()
            cur.close()
            conn.close()
            
            return jsonify({
                "id": entry['id'],
                "userId": entry['userId'],
                "title": entry['title'],
                "content": entry['content'],
                "imageUrl": entry['imageUrl'],
                "createdAt": entry['createdAt'].isoformat(),
                "updatedAt": entry['updatedAt'].isoformat()
            }), 201
        except Exception as e:
            conn.rollback()
            conn.close()
            return jsonify({"error": "Failed to create entry", "detail": str(e)}), 500
    
    except Exception as e:
        return jsonify({"error": "Failed to create diary entry", "detail": str(e)}), 500

# Get all diary entries for authenticated user
@app.route('/api/diary/entries', methods=['GET'])
@require_auth
def get_user_diary_entries():
    """Get all diary entries for the authenticated user"""
    try:
        user_id = request.user_id
        conn = get_db_connection()
        if not conn:
            return jsonify({"error": "Database connection failed"}), 500

        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute(
            """
            SELECT * FROM "DiaryEntry"
            WHERE "userId" = %s
            ORDER BY "createdAt" DESC
            """,
            (user_id,)
        )
        entries = cur.fetchall()
        cur.close()
        conn.close()

        return jsonify([{
            "id": entry['id'],
            "userId": entry['userId'],
            "title": entry['title'],
            "content": entry['content'],
            "imageUrl": entry['imageUrl'],
            "createdAt": entry['createdAt'].isoformat(),
            "updatedAt": entry['updatedAt'].isoformat()
        } for entry in entries]), 200

    except Exception as e:
        return jsonify({"error": "Failed to fetch entries", "detail": str(e)}), 500

# Get specific diary entry
@app.route('/api/diary/entries/<entry_id>', methods=['GET'])
@require_auth
def get_diary_entry(entry_id):
    """Get a specific diary entry"""
    try:
        user_id = request.user_id
        conn = get_db_connection()
        if not conn:
            return jsonify({"error": "Database connection failed"}), 500

        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute(
            """
            SELECT * FROM "DiaryEntry"
            WHERE "id" = %s
            """,
            (entry_id,)
        )
        entry = cur.fetchone()
        cur.close()
        conn.close()

        if not entry:
            return jsonify({"error": "Diary entry not found"}), 404

        if entry['userId'] != user_id:
            return jsonify({"error": "Access denied"}), 403

        return jsonify({
            "id": entry['id'],
            "userId": entry['userId'],
            "title": entry['title'],
            "content": entry['content'],
            "imageUrl": entry['imageUrl'],
            "createdAt": entry['createdAt'].isoformat(),
            "updatedAt": entry['updatedAt'].isoformat()
        }), 200

    except Exception as e:
        return jsonify({"error": "Failed to fetch entry", "detail": str(e)}), 500

# Delete diary entry
@app.route('/api/diary/entries/<entry_id>', methods=['DELETE'])
@require_auth
def delete_diary_entry(entry_id):
    """Delete a diary entry"""
    try:
        user_id = request.user_id
        conn = get_db_connection()
        if not conn:
            return jsonify({"error": "Database connection failed"}), 500

        # First check if entry exists and belongs to user
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute(
            """
            SELECT * FROM "DiaryEntry"
            WHERE "id" = %s
            """,
            (entry_id,)
        )
        entry = cur.fetchone()

        if not entry:
            cur.close()
            conn.close()
            return jsonify({"error": "Diary entry not found"}), 404

        if entry['userId'] != user_id:
            cur.close()
            conn.close()
            return jsonify({"error": "Access denied"}), 403

        # Delete associated image if exists
        if entry['imageUrl']:
            image_path = UPLOAD_DIR / entry['imageUrl'].split("/")[-1]
            if image_path.exists():
                image_path.unlink()

        # Delete from database
        cur.execute(
            """
            DELETE FROM "DiaryEntry"
            WHERE "id" = %s
            """,
            (entry_id,)
        )
        conn.commit()
        cur.close()
        conn.close()

        return jsonify({"message": "Diary entry deleted successfully"}), 200

    except Exception as e:
        return jsonify({"error": "Failed to delete entry", "detail": str(e)}), 500

# Serve uploaded files
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(str(UPLOAD_DIR), filename)

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500

# For local development
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)

