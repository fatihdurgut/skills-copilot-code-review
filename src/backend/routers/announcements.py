"""
Announcement endpoints for the High School Management System API
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field
from ..database import announcements_collection
from ..routers.auth import get_current_user

router = APIRouter(
    prefix="/announcements",
    tags=["announcements"]
)

class Announcement(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    message: str
    start_date: Optional[datetime] = None
    expiration_date: datetime

@router.get("/", response_model=List[Announcement])
def list_announcements():
    """List all announcements (not expired)"""
    now = datetime.utcnow()
    query = {"expiration_date": {"$gte": now}}
    return list(announcements_collection.find(query))

@router.post("/", response_model=Announcement)
def create_announcement(announcement: Announcement, user=Depends(get_current_user)):
    """Create a new announcement (auth required)"""
    data = announcement.dict(by_alias=True, exclude_unset=True)
    result = announcements_collection.insert_one(data)
    data["_id"] = str(result.inserted_id)
    return data

@router.put("/{announcement_id}", response_model=Announcement)
def update_announcement(announcement_id: str, announcement: Announcement, user=Depends(get_current_user)):
    """Update an announcement (auth required)"""
    data = announcement.dict(by_alias=True, exclude_unset=True)
    result = announcements_collection.update_one({"_id": announcement_id}, {"$set": data})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Announcement not found")
    return announcements_collection.find_one({"_id": announcement_id})

@router.delete("/{announcement_id}")
def delete_announcement(announcement_id: str, user=Depends(get_current_user)):
    """Delete an announcement (auth required)"""
    result = announcements_collection.delete_one({"_id": announcement_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Announcement not found")
    return {"success": True}
