from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from database import db
from models import RegisterRequest, LoginRequest, StandardResponse
from utils import base64_to_cv2, get_face_embedding, is_match, calculate_distance
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

    # 4. Save to DB
    user_doc = {
        "user_id": request.user_id,
        "face_embedding": embedding,
        "created_at": datetime.utcnow()
    }
    await db.db.users.insert_one(user_doc)

    return StandardResponse(success=True, message="User registered successfully")

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
    # Ideally, perform vector search if using Atlas Vector Search or similar.
    # Here we iterate (okay for small dataset).
    
    best_match_user = None
    min_distance = float("inf")
    
    cursor = db.db.users.find({})
    async for user in cursor:
        stored_embedding = user["face_embedding"]
        dist = calculate_distance(embedding, stored_embedding)
        
        if dist < min_distance:
            min_distance = dist
            best_match_user = user

    # 4. Check Threshold
    # Using 0.55 as a balanced threshold (VGG-Face L2)
    THRESHOLD = 0.55
    
    if best_match_user and min_distance < THRESHOLD:
        return StandardResponse(
            success=True, 
            message="Login Successful", 
            data={
                "user_id": best_match_user["user_id"],
                "distance": float(min_distance)
            }
        )
    
    return StandardResponse(success=False, message="Face not recognized")
