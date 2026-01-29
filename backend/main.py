from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from database import db
from models import RegisterRequest, LoginRequest, StandardResponse
from utils import base64_to_cv2, get_face_embedding, is_match, calculate_distance, find_best_match_in_db
from datetime import datetime

@asynccontextmanager
async def lifespan(app: FastAPI):
    await db.connect()
    yield
    await db.close()

app = FastAPI(lifespan=lifespan)

# Allow CORS for React
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, specify the frontend origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Face Auth API is running"}

@app.post("/register", response_model=StandardResponse)
async def register_user(request: RegisterRequest):
    # 1. Check if user already exists
    existing_user = await db.db.users.find_one({"user_id": request.user_id})
    if existing_user:
        raise HTTPException(status_code=400, detail="User ID already exists")

    # 2. Process Image
    img = base64_to_cv2(request.image)
    if img is None:
        raise HTTPException(status_code=400, detail="Invalid image data")

    # 3. Extract Embedding
    embedding = get_face_embedding(img)
    if embedding is None:
        raise HTTPException(status_code=400, detail="No face detected in the image")

    # 4. Check for duplicates (Face already registered?)
    # We broaden the scope here (0.60) to ensure we catch the same person 
    # even if lighting is slightly different.
    DUPLICATE_THRESHOLD = 0.60
    matched_user, dist = await find_best_match_in_db(embedding, db.db.users, threshold=DUPLICATE_THRESHOLD)
    
    if matched_user:
        raise HTTPException(
            status_code=400, 
            detail=f"Face already registered as user: {matched_user['user_id']} (Similarity: {dist:.4f})"
        )

    # 5. Save to DB
    user_doc = {
        "user_id": request.user_id,
        "face_embedding": embedding,
        "device_info": request.device_info,
        "created_at": datetime.utcnow()
    }
    await db.db.users.insert_one(user_doc)

    return StandardResponse(success=True, message=f"User registered successfully (Device: {request.device_info})")

@app.post("/verify", response_model=StandardResponse)
async def verify_user(request: LoginRequest):
    # 1. Process Image
    img = base64_to_cv2(request.image)
    if img is None:
        raise HTTPException(status_code=400, detail="Invalid image data")

    # 2. Extract Embedding
    embedding = get_face_embedding(img)
    if embedding is None:
        raise HTTPException(status_code=400, detail="No face detected")

    # 3. Compare with DB users (1:N search)
    # Relaxed threshold to 0.65 to make login significantly easier/broader scope
    THRESHOLD = 0.65
    
    best_match_user, min_distance = await find_best_match_in_db(embedding, db.db.users, threshold=THRESHOLD)
    
    if best_match_user and min_distance < THRESHOLD:
        return StandardResponse(
            success=True, 
            message="Login Successful", 
            data={
                "user_id": best_match_user["user_id"],
                "distance": float(min_distance)
            }
        )
    
    msg_distance = f"{min_distance:.4f}" if min_distance != float('inf') else "N/A"
    return StandardResponse(success=False, message=f"Face not recognized (Closest: {msg_distance})")
