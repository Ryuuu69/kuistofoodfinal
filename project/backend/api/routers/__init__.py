from fastapi import APIRouter

from . import categories, products, options, choice_options, orders

api_router = APIRouter()

api_router.include_router(categories.router)
api_router.include_router(products.router)
api_router.include_router(options.router)
api_router.include_router(choice_options.router)
api_router.include_router(orders.router)


