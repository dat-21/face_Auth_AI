from pydantic import BaseModel

class RegisterRequest(BaseModel):
    user_id: str
    image: str  # Base64 encoded image
    device_info: str | None = None # Optional: Camera/Device details for calibration

class LoginRequest(BaseModel):
    image: str  # Base64 encoded image

class StandardResponse(BaseModel):
    success: bool
    message: str
    data: dict | None = None
