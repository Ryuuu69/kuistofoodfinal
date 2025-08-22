from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.deps import get_db, get_admin_token
from schemas.schemas import ChoiceOptionCreate, ChoiceOptionUpdate, ChoiceOptionResponse
from crud.crud_operations import choice_option_crud

router = APIRouter(prefix="/choice-options", tags=["Choice Options"])

@router.post("/", response_model=ChoiceOptionResponse, status_code=status.HTTP_201_CREATED)
async def create_choice_option(
    choice_option_in: ChoiceOptionCreate,
    db: AsyncSession = Depends(get_db),
    admin_token: str = Depends(get_admin_token) # Admin protected
):
    return await choice_option_crud.create(db, obj_in=choice_option_in)

@router.get("/", response_model=List[ChoiceOptionResponse])
async def read_choice_options(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    return await choice_option_crud.get_multi(db, skip=skip, limit=limit)

@router.get("/{choice_option_id}", response_model=ChoiceOptionResponse)
async def read_choice_option(
    choice_option_id: int,
    db: AsyncSession = Depends(get_db)
):
    choice_option = await choice_option_crud.get(db, id=choice_option_id)
    if not choice_option:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Choice option not found")
    return choice_option

@router.put("/{choice_option_id}", response_model=ChoiceOptionResponse)
async def update_choice_option(
    choice_option_id: int,
    choice_option_in: ChoiceOptionUpdate,
    db: AsyncSession = Depends(get_db),
    admin_token: str = Depends(get_admin_token) # Admin protected
):
    choice_option = await choice_option_crud.get(db, id=choice_option_id)
    if not choice_option:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Choice option not found")
    return await choice_option_crud.update(db, db_obj=choice_option, obj_in=choice_option_in)

@router.delete("/{choice_option_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_choice_option(
    choice_option_id: int,
    db: AsyncSession = Depends(get_db),
    admin_token: str = Depends(get_admin_token) # Admin protected
):
    choice_option = await choice_option_crud.remove(db, id=choice_option_id)
    if not choice_option:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Choice option not found")
    return {"message": "Choice option deleted successfully"}
