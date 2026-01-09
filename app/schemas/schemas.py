from typing import Optional
from pydantic import BaseModel,EmailStr
from uuid import UUID
from datetime import datetime
class UserBase(BaseModel):
    full_name:str | None = None # | None ka mtlab hai ye  optional hai 
    email:EmailStr # y EmailStr  check karega ki @ aur . shai hai ya nahi basically email formated  hai y nahi
class UserCreate(UserBase):# UserBase  se  inherit  ho kar  name email aa rahi hai bas maine  password  add  kar  diya  hai
    password:str 
class UserOut(UserBase):
    user_id:UUID
    class Config:
        from_attributes = True
class IssueBase(BaseModel):
    title:str 
    description:Optional[str]=None
    status:Optional[str]="backlog"
    priority:Optional[int]=0
    team_id:Optional[UUID]=None
    assignee_id:Optional[UUID]=None

class IssueCreate(IssueBase):
    pass

class IssueOut(IssueBase): # Ye response bhejte waqt kaam aayega
    id: UUID
    creator_id: UUID
    created_at: datetime
    class Config:
        from_attributes = True

class TeamCreate(BaseModel):
    name:str
    key:str
class TeamOut(BaseModel):
    id:UUID
    name:str
    key:str

    class Config:
        from_attributes=True