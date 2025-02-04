from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi import Request
from app.core.setup_db import update_local_runtime
from app.core.setup_instancedata import setup_instancedata
from app.core.config import settings
from app.migrations.all import do_migrations_prestart

from starlette.middleware.cors import CORSMiddleware

from app.api.main import api_router
from app.base_logger import logger

from jinja2 import BaseLoader, Environment
import os


app = FastAPI(title="DANNCE GUI")

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
    do_migrations_prestart()
    update_local_runtime()


initialize_state()

app.include_router(api_router, prefix="/v1")

app.mount("/static", StaticFiles(directory=settings.STATIC_TMP_FOLDER), name="static")

# Serve frontend unless disabled (e.g. for devleopment)
if not os.environ.get('NO_SERVE_FE', False):
    logger.info("Mounting frontend")
    @app.get("/app/index.html", response_class=HTMLResponse)
    async def get_app_index(request: Request):
        """Template the app index to inject API_BASE_URL"""
        with open(settings.REACT_APP_DIST_FOLDER.joinpath("index.html")) as f:
            template_str = f.read()
        template = Environment(loader=BaseLoader()).from_string(template_str)
        logger.info(f"USING API BASE URL: {settings.API_BASE_URL}")
        html_str = template.render(API_URL_INJECTED=settings.API_BASE_URL)
        return html_str


    app.mount("/app", StaticFiles(directory=settings.REACT_APP_DIST_FOLDER), name="gui_fe")
else:
    logger.info("NOT MOUTNING FRONTEND")
