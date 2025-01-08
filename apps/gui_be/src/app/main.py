from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi import Request
from app.core.setup_db import update_local_runtime
from app.core.setup_instancedata import setup_instancedata
from app.core.config import settings

from starlette.middleware.cors import CORSMiddleware

from app.api.main import api_router
from app.base_logger import logger

from jinja2 import BaseLoader, Environment

app = FastAPI(title="DANNCE GUI API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def initialize_state():
    logger.info("INIT'ING STATE")
    setup_instancedata()
    update_local_runtime()


initialize_state()

app.include_router(api_router, prefix="/v1")


@app.get("/app/index.html", response_class=HTMLResponse)
async def get_app_index(request: Request):
    """Template the app index to inject API_BASE_URL"""
    with open(settings.REACT_APP_DIST_FOLDER.joinpath("index.html")) as f:
        template_str = f.read()
    template = Environment(loader=BaseLoader()).from_string(template_str)
    html_str = template.render(API_URL_INJECTED=settings.API_BASE_URL)
    return html_str


app.mount("/static", StaticFiles(directory=settings.STATIC_TMP_FOLDER), name="static")
app.mount("/app", StaticFiles(directory=settings.REACT_APP_DIST_FOLDER), name="gui_fe")

# https://rcood.rc.fas.harvard.edu/rnode/holy7c18105.rc.fas.harvard.edu/8000/app -> index.html inside ../gui_fe/dist

# https://rcood.rc.fas.harvard.edu/rnode/holy7c18105.rc.fas.harvard.edu/home INSTEAD OF
# https://rcood.rc.fas.harvard.edu/rnode/holy7c18105.rc.fas.harvard.edu/8000/app/home -> index.html

# COULD USE /node (vs /rnode) and specify base URL!

# check out OOD session -> baseURL -> internal Ref's relative to baseURL
