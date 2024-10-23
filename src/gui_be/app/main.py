from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.core.setup_instancedata import setup_instancedata
from app.core.config import settings

from starlette.middleware.cors import CORSMiddleware

from app.api.main import api_router


print(f"\nRunning on {settings.API_BASE_URL}")

app = FastAPI(title="DANNCE GUI API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/v1")
app.mount("/static", StaticFiles(directory=settings.STATIC_TMP_FOLDER), name="static")

setup_instancedata()
