from typing import Optional
from pydantic import BaseModel,EmailStr
from uuid import UUID
class UserBase(BaseModel):
    full_name:str | None = None # | None ka mtlab hai ye  optional hai 
    email:EmailStr # y EmailStr  check karega ki @ aur . shai hai ya nahi basically email formated  hai y nahi
class UserCreate(UserBase):# UserBase  se  inherit  ho kar  name email aa rahi hai bas maine  password  add  kar  diya  hai
    password:str 
class UserOut(UserBase):
    user_id:UUID
    class Config:
        from_attributes = True
class IssueCreate(BaseModel):
    title:str 
    description:Optional[str]=None
    status:Optional[str]="backlog"
    priority:Optional[int]=0
    team_id:Optional[UUID]=None
    assignee_id:Optional[UUID]=None # bhai tip humesah check karna ki syntex error na ho thik  hai 
