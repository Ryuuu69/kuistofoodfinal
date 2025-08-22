from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.deps import get_db, get_admin_token
from schemas.schemas import MenuCreate, MenuUpdate, MenuResponse
from crud.crud_operations import menu_crud

router = APIRouter(prefix="/menus", tags=["Menus"])

@router.post("/", response_model=MenuResponse, status_code=status.HTTP_201_CREATED)
async def create_menu(
    menu_in: MenuCreate,
    db: AsyncSession = Depends(get_db),
    admin_token: str = Depends(get_admin_token) # Admin protected
):
    # Crée le menu et gère les associations products/options
    return await menu_crud.create_with_relations(db, obj_in=menu_in)

@router.get("/", response_model=List[MenuResponse])
async def read_menus(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    # Renvoie chaque menu AVEC ses produits/choix et options imbriquées
    return await menu_crud.get_multi_with_relations(db, skip=skip, limit=limit)

@router.get("/{menu_id}", response_model=MenuResponse)
async def read_menu(
    menu_id: int,
    db: AsyncSession = Depends(get_db)
):
    menu = await menu_crud.get_with_relations(db, id=menu_id)
    if not menu:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Menu not found")
    return menu

@router.put("/{menu_id}", response_model=MenuResponse)
async def update_menu(
    menu_id: int,
    menu_in: MenuUpdate,
    db: AsyncSession = Depends(get_db),
    admin_token: str = Depends(get_admin_token)
):
    menu = await menu_crud.get(db, id=menu_id)
    if not menu:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Menu not found")
    return await menu_crud.update_with_relations(db, db_obj=menu, obj_in=menu_in)

@router.delete("/{menu_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_menu(
    menu_id: int,
    db: AsyncSession = Depends(get_db),
    admin_token: str = Depends(get_admin_token)
):
    menu = await menu_crud.remove(db, id=menu_id)
    if not menu:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Menu not found")
    return {"message": "Menu deleted successfully"}
