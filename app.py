from fastapi import FastAPI

from APIModules.APIs.base_router import base_router
import uvicorn

app = FastAPI()

app.include_router(base_router)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

    