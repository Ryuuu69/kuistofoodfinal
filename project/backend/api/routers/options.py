from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from api.deps import get_db, get_admin_token
from schemas.schemas import OptionCreate, OptionUpdate, OptionResponse
from crud.crud_operations import option_crud, product_crud

router = APIRouter(prefix="/options", tags=["Options"])

# ----------- ROUTES CRUD ---------------

@router.post("/", response_model=OptionResponse, status_code=status.HTTP_201_CREATED)
async def create_option(
    option_in: OptionCreate,
    db: AsyncSession = Depends(get_db),
    admin_token: str = Depends(get_admin_token) # Admin protected
):
    return await option_crud.create(db, obj_in=option_in)

@router.get("/", response_model=List[OptionResponse])
async def read_options(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    return await option_crud.get_multi_with_relations(db, skip=skip, limit=limit)

@router.get("/{option_id}", response_model=OptionResponse)
async def read_option(
    option_id: int,
    db: AsyncSession = Depends(get_db)
):
    option = await option_crud.get_with_relations(db, id=option_id)
    if not option:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Option not found")
    return option

@router.put("/{option_id}", response_model=OptionResponse)
async def update_option(
    option_id: int,
    option_in: OptionUpdate,
    db: AsyncSession = Depends(get_db),
    admin_token: str = Depends(get_admin_token) # Admin protected
):
    option = await option_crud.get(db, id=option_id)
    if not option:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Option not found")
    return await option_crud.update(db, db_obj=option, obj_in=option_in)

@router.delete("/{option_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_option(
    option_id: int,
    db: AsyncSession = Depends(get_db),
    admin_token: str = Depends(get_admin_token) # Admin protected
):
    option = await option_crud.remove(db, id=option_id)
    if not option:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Option not found")
    return {"message": "Option deleted successfully"}

# ----------- ROUTE PIVOT : lier Option <-> Produit ---------------

@router.post("/{option_id}/products/{product_id}", status_code=204)
async def link_option_to_product(
    option_id: int,
    product_id: int,
    db: AsyncSession = Depends(get_db),
    admin_token: str = Depends(get_admin_token)
):
    # On charge le produit avec ses options en avance (PRÉCHARGEMENT OBLIGATOIRE EN ASYNC !)
    result = await db.execute(
        select(product_crud.model).options(selectinload(product_crud.model.options)).where(product_crud.model.id == product_id)
    )
    product = result.scalar_one_or_none()
    option = await option_crud.get(db, id=option_id)
    if not product or not option:
        raise HTTPException(status_code=404, detail="Product or Option not found")
    if any(opt.id == option.id for opt in product.options):
        return  # Déjà lié, ne fait rien
    product.options.append(option)
    await db.commit()
    return {"message": "Option linked to Product"}
@router.delete("/{option_id}/products/{product_id}", status_code=204)
async def unlink_option_from_product(
    option_id: int,
    product_id: int,
    db: AsyncSession = Depends(get_db),
    admin_token: str = Depends(get_admin_token)
):
    product = await product_crud.get(db, id=product_id)
    option  = await option_crud.get(db, id=option_id)
    if not product or not option:
        raise HTTPException(status_code=404, detail="Product or Option not found")
    # Si le lien existe, on l'enlève
    if option in product.options:
        product.options.remove(option)
        await db.commit()
    return {"message": "Option unlinked from Product"}
