# API Development Guidelines & Best Practices

## 🎯 Core Principles - Har API me yeh rules follow karo:

### 1. **HTTP Methods (RESTful)**
```
✅ POST   → Create new resource   (status: 201 Created)
✅ GET    → Read/Fetch resource   (status: 200 OK)
✅ PUT    → Update entire resource (status: 200 OK)
✅ PATCH  → Partial update        (status: 200 OK)
✅ DELETE → Delete resource       (status: 204 No Content)
```

### 2. **Status Codes Consistency**
```
✅ 200 OK              → GET, PUT successful
✅ 201 Created         → POST successful (resource created)
✅ 204 No Content      → DELETE successful (no body)
✅ 400 Bad Request     → Invalid input/data
✅ 401 Unauthorized    → Authentication failed
✅ 403 Forbidden       → No permission
✅ 404 Not Found       → Resource not found
✅ 422 Unprocessable   → Validation error
✅ 500 Server Error    → Internal server error
```

### 3. **Response Models - Hamesha define karo!**
```python
# ✅ GOOD - Always specify response_model
@router.get("/", response_model=list[schemas.UserOut])
@router.post("/", response_model=schemas.UserOut, status_code=201)

# ❌ BAD - No response_model
@router.get("/")
@router.post("/")
```

### 4. **Naming Conventions**
```python
# ✅ Function names - snake_case
async def get_users()
async def create_user()
async def update_user()
async def delete_user()

# ✅ Route paths - kebab-case/plural
GET    /users
POST   /users
GET    /users/{id}
PUT    /users/{id}
DELETE /users/{id}
```

### 5. **Code Structure Template**
```python
# 1. IMPORTS (standard order)
from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID
from .. import schemas, model, oauth2
from ..lib.database import get_db

# 2. ROUTER DECLARATION
router = APIRouter(prefix="/resource", tags=["Resource"])

# 3. ENDPOINTS (in this order: GET all, GET one, POST, PUT, DELETE)
@router.get("/", status_code=status.HTTP_200_OK, response_model=list[schemas.ResourceOut])
async def get_resources(
    db: AsyncSession = Depends(get_db),
    current_user: model.User = Depends(oauth2.get_current_user)
):
    # Query
    query = select(model.Resource)
    result = await db.execute(query)
    resources = result.scalars().all()
    
    return resources

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.ResourceOut)
async def create_resource(
    resource: schemas.ResourceCreate,
    db: AsyncSession = Depends(get_db),
    current_user: model.User = Depends(oauth2.get_current_user)
):
    # Validation & Create logic
    new_resource = model.Resource(**resource.model_dump())
    db.add(new_resource)
    await db.commit()
    await db.refresh(new_resource)
    
    return new_resource
```

### 6. **Error Handling Pattern**
```python
# ✅ Always use HTTPException with proper status codes
if not resource:
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Resource not found"
    )

# ✅ Use status.HTTP_XXX constants, not numbers
# ❌ BAD: status_code=400
# ✅ GOOD: status_code=status.HTTP_400_BAD_REQUEST
```

### 7. **Database Operations Pattern**
```python
# 1. Query
query = select(model.Resource).where(condition)
result = await db.execute(query)
resource = result.scalars().first()

# 2. Validation
if not resource:
    raise HTTPException(...)

# 3. Operation (for POST/PUT)
db.add(new_resource)  # or db.delete(resource)
await db.commit()
await db.refresh(new_resource)  # Only for create/update

# 4. Return
return resource
```

### 8. **Authentication & Authorization**
```python
# ✅ Always add authentication for protected endpoints
current_user: model.User = Depends(oauth2.get_current_user)

# ✅ Check ownership for update/delete
if resource.creator_id != current_user.id:
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="You don't have permission"
    )
```

### 9. **Request/Response Schema Naming**
```python
# ✅ Consistent naming pattern
ResourceCreate   → POST request body
ResourceUpdate   → PUT/PATCH request body
ResourceOut      → GET response
ResourceBase     → Shared fields (optional)
```

### 10. **Code Formatting Standards**
```python
# ✅ Proper spacing
query = select(model.Resource)  # Not: query=select...
result = await db.execute(query)  # Not: result=await db...

# ✅ Type hints - Always specify
async def get_resource(
    id: UUID,
    db: AsyncSession = Depends(get_db)
):

# ✅ Comments - Clear & helpful (in English for consistency)
# Get all resources
# Create new resource
# Update resource by ID
```

### 11. **Validation Checklist**
```python
# Before creating:
✅ Check if resource already exists (unique fields)
✅ Validate input data (Pydantic handles this, but add custom if needed)
✅ Check permissions/ownership

# Before updating:
✅ Check if resource exists
✅ Check if user is owner
✅ Validate updated data

# Before deleting:
✅ Check if resource exists
✅ Check if user is owner
```

### 12. **Import Order (Standard)**
```python
# 1. FastAPI imports
from fastapi import ...

# 2. SQLAlchemy imports
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

# 3. Python standard library
from uuid import UUID
from datetime import datetime

# 4. Local imports
from .. import schemas, model, oauth2
from ..lib.database import get_db
```

---

## 📋 Quick Checklist - Har API likhne se pehle:

- [ ] Proper HTTP method used (POST/GET/PUT/DELETE)
- [ ] Status code specified (201 for POST, 200 for GET/PUT, 204 for DELETE)
- [ ] Response model defined (`response_model=schemas.XxxOut`)
- [ ] Authentication added if needed (`Depends(oauth2.get_current_user)`)
- [ ] Error handling with HTTPException and proper status codes
- [ ] Type hints on all function parameters
- [ ] Consistent naming (snake_case for functions, kebab-case for routes)
- [ ] Database operations: commit() and refresh() after create/update
- [ ] Validation checks (exists, ownership, etc.)
- [ ] Clean code formatting with proper spacing

---

## 🎯 Golden Rule (Yaad rakhna):

**"Har API endpoint same pattern follow kare, same structure ho, aur same way me error handle kare"**

Agar sab APIs me yeh pattern follow ho, to:
- ✅ Code maintainable hoga
- ✅ Team members easily samajh payenge
- ✅ Bug finding easy hogi
- ✅ Testing simple hogi
- ✅ Documentation automatic ho jayegi

