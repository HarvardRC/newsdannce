from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from app.core.setup_db import update_local_runtime
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


def initialize_state():
    setup_instancedata()
    update_local_runtime()


initialize_state()


app.include_router(api_router, prefix="/v1")
app.mount("/static", StaticFiles(directory=settings.STATIC_TMP_FOLDER), name="static")
app.mount("/app/", StaticFiles(directory='../dannce_gui_fe/dist'), name="gui_fe")

# https://rcood.rc.fas.harvard.edu/rnode/holy7c18105.rc.fas.harvard.edu/8000/app -> index.html inside ../dannce_gui_fe/dist

# https://rcood.rc.fas.harvard.edu/rnode/holy7c18105.rc.fas.harvard.edu/home INSTEAD OF
# https://rcood.rc.fas.harvard.edu/rnode/holy7c18105.rc.fas.harvard.edu/8000/app/home -> index.html

# COULD USE /node (vs /rnode) and specify base URL!

# check out OOD session -> baseURL -> internal Ref's relative to baseURL