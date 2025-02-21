from fastapi import APIRouter

base_router = APIRouter()

@base_router.get("/")
async def read_root():
    return {"message": "Welcome to the FastAPI router"}

@base_router.get("/items/{item_id}")
async def read_item(item_id: int):
    return {"item_id": item_id, "name": f"Item {item_id}"}