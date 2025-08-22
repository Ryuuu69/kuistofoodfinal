from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.deps import get_db, get_admin_token
from schemas.schemas import CategoryCreate, CategoryUpdate, CategoryResponse
from crud.crud_operations import category_crud

router = APIRouter(prefix="/categories", tags=["Categories"])

@router.post("/", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_category(
    category_in: CategoryCreate,
    db: AsyncSession = Depends(get_db),
    admin_token: str = Depends(get_admin_token) # Admin protected
):
    return await category_crud.create(db, obj_in=category_in)

@router.get("/", response_model=List[CategoryResponse])
async def read_categories(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    return await category_crud.get_multi(db, skip=skip, limit=limit)

@router.get("/{category_id}", response_model=CategoryResponse)
async def read_category(
    category_id: int,
    db: AsyncSession = Depends(get_db)
):
    category = await category_crud.get(db, id=category_id)
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
    return category

@router.put("/{category_id}", response_model=CategoryResponse)
async def update_category(
    category_id: int,
    category_in: CategoryUpdate,
    db: AsyncSession = Depends(get_db),
    admin_token: str = Depends(get_admin_token) # Admin protected
):
    category = await category_crud.get(db, id=category_id)
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
    return await category_crud.update(db, db_obj=category, obj_in=category_in)

@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(
    category_id: int,
    db: AsyncSession = Depends(get_db),
    admin_token: str = Depends(get_admin_token) # Admin protected
):
    category = await category_crud.remove(db, id=category_id)
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
    return {"message": "Category deleted successfully"}