from pydantic import BaseModel,EmailStr
from uuid import UUID
class UserBase(BaseModel):
    full_name:str | None=None # | None ka mtlab hai ye  optional hai 
    email:EmailStr # y EmailStr  check karega ki @ aur . shai hai ya nahi basically email formated  hai y nahi
class UserCreate(UserBase):# UserBase  se  inherit  ho kar  name email aa rahi hai bas maine  password  add  kar  diya  hai
    password:str 
class UserOut(UserBase):
    user_id:UUID
    class Config:
        from_attributes = True

