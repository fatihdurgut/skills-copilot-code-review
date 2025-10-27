"""
Authentication endpoints for the High School Management System API
"""

from fastapi import APIRouter, HTTPException, Depends, Request
from typing import Dict, Any

from ..database import teachers_collection, verify_password

def get_current_user(request: Request):
    # For demo: get username from query or header (replace with real session/cookie in production)
    username = request.query_params.get("username") or request.headers.get("X-Username")
    if not username:
        raise HTTPException(status_code=401, detail="Not authenticated")
    teacher = teachers_collection.find_one({"_id": username})
    if not teacher:
        raise HTTPException(status_code=401, detail="Invalid user")
    return teacher

router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)


@router.post("/login")
def login(username: str, password: str) -> Dict[str, Any]:
    """Login a teacher account"""
    # Find the teacher in the database
    teacher = teachers_collection.find_one({"_id": username})

    # Verify password using Argon2 verifier from database.py
    if not teacher or not verify_password(teacher.get("password", ""), password):
        raise HTTPException(
            status_code=401, detail="Invalid username or password")

    # Return teacher information (excluding password)
    return {
        "username": teacher["username"],
        "display_name": teacher["display_name"],
        "role": teacher["role"]
    }


@router.get("/check-session")
def check_session(username: str) -> Dict[str, Any]:
    """Check if a session is valid by username"""
    teacher = teachers_collection.find_one({"_id": username})

    if not teacher:
        raise HTTPException(status_code=404, detail="Teacher not found")

    return {
        "username": teacher["username"],
        "display_name": teacher["display_name"],
        "role": teacher["role"]
    }
