import base64
import numpy as np
import cv2
from deepface import DeepFace
# Suppress heavy logs
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

def base64_to_cv2(base64_str: str):
    """
    Convert base64 image string to OpenCV image (numpy array).
    """
    try:
        if "base64," in base64_str:
            base64_str = base64_str.split("base64,")[1]
        
        img_data = base64.b64decode(base64_str)
        nparr = np.frombuffer(img_data, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        return img
    except Exception as e:
        print(f"Error decoding image: {e}")
        return None

def get_face_embedding(img_bgr) -> list[float]:
    """
    Extract face embedding using DeepFace (VGG-Face by default).
    Returns the first face found.
    """
    try:
        # DeepFace.represent returns a list of dicts: [{'embedding': [], 'facial_area': {}}]
        # enforce_detection=True throws error if no face found.
        # We handle it by catching exception or setting False.
        # For security, we MUST detect a face.
        embedding_objs = DeepFace.represent(
            img_path=img_bgr,
            model_name="VGG-Face",
            enforce_detection=True,
            detector_backend="opencv" # Use opencv for speed, or 'retinaface' for accuracy
        )
        if not embedding_objs:
            return None
        
        return embedding_objs[0]["embedding"]
    except Exception as e:
        print(f"Face extraction error: {e}")
        return None

def calculate_distance(embedding1: list[float], embedding2: list[float]) -> float:
    """
    Calculate Euclidean (L2) distance between two embeddings.
    """
    a = np.array(embedding1)
    b = np.array(embedding2)
    return np.linalg.norm(a - b)

def is_match(embedding1, embedding2, threshold=0.40) -> bool:
    """
    Verify if two embeddings match.
    Threshold for VGG-Face with L2 distance is typically around 0.40.
    """
    distance = calculate_distance(embedding1, embedding2)
    # print(f"Distance: {distance}, Threshold: {threshold}")
    return distance <= threshold

async def find_best_match_in_db(input_embedding: list[float], db_collection, threshold: float = 0.55):
    """
    Search through the database to find the closest face embedding.
    Returns: (user_doc, min_distance) or (None, infinity)
    """
    best_match_user = None
    min_distance = float("inf")
    
    # Ideally use Vector Search here. For now, we iterate.
    cursor = db_collection.find({})
    count = 0
    async for user in cursor:
        count += 1
        if "face_embedding" not in user:
            continue
            
        stored_embedding = user["face_embedding"]
        dist = calculate_distance(input_embedding, stored_embedding)
        
        if dist < min_distance:
            min_distance = dist
            best_match_user = user

    print(f"[DEBUG] Checked {count} users in DB. Closest match distance: {min_distance} (Threshold: {threshold})")

    if min_distance < threshold:
        return best_match_user, min_distance
    
    return None, min_distance
