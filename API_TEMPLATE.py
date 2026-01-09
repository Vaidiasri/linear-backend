"""
API Endpoint Template
Copy this template when creating a new API endpoint
Follow the structure and patterns defined here
"""

from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID
from .. import schemas, model, oauth2
from ..lib.database import get_db

# Router declaration
router = APIRouter(prefix="/resource", tags=["Resource"])


# GET ALL - List all resources
@router.get("/", status_code=status.HTTP_200_OK, response_model=list[schemas.ResourceOut])
async def get_resources(
    db: AsyncSession = Depends(get_db),
    current_user: model.User = Depends(oauth2.get_current_user)
):
    """
    Get all resources for the current user
    """
    query = select(model.Resource).where(model.Resource.creator_id == current_user.id)
    result = await db.execute(query)
    resources = result.scalars().all()
    
    return resources


# GET ONE - Get single resource by ID
@router.get("/{id}", status_code=status.HTTP_200_OK, response_model=schemas.ResourceOut)
async def get_resource(
    id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: model.User = Depends(oauth2.get_current_user)
):
    """
    Get a specific resource by ID
    """
    query = select(model.Resource).where(
        model.Resource.id == id,
        model.Resource.creator_id == current_user.id
    )
    result = await db.execute(query)
    resource = result.scalars().first()
    
    if not resource:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resource not found"
        )
    
    return resource


# POST - Create new resource
@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.ResourceOut)
async def create_resource(
    resource: schemas.ResourceCreate,
    db: AsyncSession = Depends(get_db),
    current_user: model.User = Depends(oauth2.get_current_user)
):
    """
    Create a new resource
    """
    # Optional: Check if resource with same unique field already exists
    # query = select(model.Resource).where(model.Resource.field == resource.field)
    # result = await db.execute(query)
    # existing = result.scalars().first()
    # if existing:
    #     raise HTTPException(
    #         status_code=status.HTTP_400_BAD_REQUEST,
    #         detail="Resource already exists"
    #     )
    
    # Create new resource
    new_resource = model.Resource(
        **resource.model_dump(),
        creator_id=current_user.id
    )
    db.add(new_resource)
    await db.commit()
    await db.refresh(new_resource)
    
    return new_resource


# PUT - Update entire resource
@router.put("/{id}", status_code=status.HTTP_200_OK, response_model=schemas.ResourceOut)
async def update_resource(
    id: UUID,
    updated_resource: schemas.ResourceCreate,  # or ResourceUpdate if you have separate schema
    db: AsyncSession = Depends(get_db),
    current_user: model.User = Depends(oauth2.get_current_user)
):
    """
    Update a resource by ID
    """
    # Check if resource exists and user is owner
    query = select(model.Resource).where(
        model.Resource.id == id,
        model.Resource.creator_id == current_user.id
    )
    result = await db.execute(query)
    resource = result.scalars().first()
    
    if not resource:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resource not found or you are not the owner"
        )
    
    # Update resource data
    for key, value in updated_resource.model_dump().items():
        setattr(resource, key, value)
    
    await db.commit()
    await db.refresh(resource)
    
    return resource


# DELETE - Delete resource
@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_resource(
    id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: model.User = Depends(oauth2.get_current_user)
):
    """
    Delete a resource by ID
    """
    # Check if resource exists and user is owner
    query = select(model.Resource).where(
        model.Resource.id == id,
        model.Resource.creator_id == current_user.id
    )
    result = await db.execute(query)
    resource = result.scalars().first()
    
    if not resource:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resource not found or you are not the owner"
        )
    
    await db.delete(resource)
    await db.commit()
    
    return None

