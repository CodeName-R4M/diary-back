from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from prisma import Prisma
import firebase_admin
from firebase_admin import credentials, auth
from pydantic import BaseModel
from typing import Optional, List
import os
from datetime import datetime
import aiofiles
from pathlib import Path
import uuid

# Initialize FastAPI
app = FastAPI(title="Personal Diary API")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000","https://diary-app-mu-azure.vercel.app/"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Prisma
prisma = Prisma()

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
        print("⚠️  Please update backend/firebase-credentials.json with valid credentials")
else:
    print("⚠️  Warning: Firebase credentials file not found")
    print("⚠️  Please create backend/firebase-credentials.json with valid credentials")

# Upload directory
UPLOAD_DIR = Path(os.getenv("UPLOAD_DIR", "./uploads"))
UPLOAD_DIR.mkdir(exist_ok=True)

# Security
security = HTTPBearer()

# Models
class DiaryEntryCreate(BaseModel):
    content: str
    title: Optional[str] = None

class DiaryEntryResponse(BaseModel):
    id: str
    userId: str
    title: Optional[str]
    content: str
    imageUrl: Optional[str]
    createdAt: datetime
    updatedAt: datetime

# Dependency to verify Firebase token
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    if not firebase_initialized:
        raise HTTPException(
            status_code=503,
            detail="Firebase authentication not configured. Please add valid Firebase credentials to backend/firebase-credentials.json"
        )
    try:
        token = credentials.credentials
        decoded_token = auth.verify_id_token(token)
        return decoded_token['uid']
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Invalid authentication credentials: {str(e)}")

@app.on_event("startup")
async def startup():
    try:
        await prisma.connect()
        print("✅ Database connected")
    except Exception as e:
        print(f"⚠️  Warning: Could not connect to database: {e}")
        print("⚠️  Please update DATABASE_URL in backend/.env with valid NeonDB credentials")

@app.on_event("shutdown")
async def shutdown():
    await prisma.disconnect()
    print("❌ Database disconnected")

@app.get("/")
async def root():
    return {"message": "Personal Diary API", "status": "running"}

@app.post("/api/diary/entries", response_model=DiaryEntryResponse)
async def create_diary_entry(
    content: str = Form(...),
    title: Optional[str] = Form(None),
    image: Optional[UploadFile] = File(None),
    user_id: str = Depends(get_current_user)
):
    """Create a new diary entry with optional image"""
    image_url = None
    
    if image:
        # Generate unique filename
        file_extension = os.path.splitext(image.filename)[1]
        unique_filename = f"{user_id}_{uuid.uuid4()}{file_extension}"
        file_path = UPLOAD_DIR / unique_filename
        
        # Save file
        async with aiofiles.open(file_path, 'wb') as f:
            content_bytes = await image.read()
            await f.write(content_bytes)
        
        image_url = f"/uploads/{unique_filename}"
    
    # Create diary entry in database
    entry = await prisma.diaryentry.create(
        data={
            "userId": user_id,
            "title": title,
            "content": content,
            "imageUrl": image_url
        }
    )
    
    return entry

@app.get("/api/diary/entries", response_model=List[DiaryEntryResponse])
async def get_user_diary_entries(user_id: str = Depends(get_current_user)):
    """Get all diary entries for the authenticated user ONLY"""
    entries = await prisma.diaryentry.find_many(
        where={"userId": user_id},
        order={"createdAt": "desc"}
    )
    return entries

@app.get("/api/diary/entries/{entry_id}", response_model=DiaryEntryResponse)
async def get_diary_entry(entry_id: str, user_id: str = Depends(get_current_user)):
    """Get a specific diary entry - only if it belongs to the authenticated user"""
    entry = await prisma.diaryentry.find_unique(where={"id": entry_id})
    
    if not entry:
        raise HTTPException(status_code=404, detail="Diary entry not found")
    
    # STRICT: Ensure user can only access their own entries
    if entry.userId != user_id:
        raise HTTPException(status_code=403, detail="Access denied: You can only view your own diary entries")
    
    return entry

@app.delete("/api/diary/entries/{entry_id}")
async def delete_diary_entry(entry_id: str, user_id: str = Depends(get_current_user)):
    """Delete a diary entry - only if it belongs to the authenticated user"""
    entry = await prisma.diaryentry.find_unique(where={"id": entry_id})
    
    if not entry:
        raise HTTPException(status_code=404, detail="Diary entry not found")
    
    # STRICT: Ensure user can only delete their own entries
    if entry.userId != user_id:
        raise HTTPException(status_code=403, detail="Access denied: You can only delete your own diary entries")
    
    # Delete associated image if exists
    if entry.imageUrl:
        image_path = UPLOAD_DIR / entry.imageUrl.split("/")[-1]
        if image_path.exists():
            image_path.unlink()
    
    await prisma.diaryentry.delete(where={"id": entry_id})
    return {"message": "Diary entry deleted successfully"}

# Mount uploads directory
app.mount("/uploads", StaticFiles(directory=str(UPLOAD_DIR)), name="uploads")

