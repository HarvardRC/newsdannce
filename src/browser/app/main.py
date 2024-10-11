from fastapi import FastAPI, Body, Response, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import os

# from fastapi.routing import APIRoute
# from pydantic import BaseModel
from starlette.middleware.cors import CORSMiddleware

from app.utils import get_info_from_df_path

# from app.api.main import api_router

# from app.core.db import SessionLocal
# from typing import Annotated
nodelist = os.environ["SLURM_NODELIST"]

print(
    "\BROWSER URL IS:",
    f"https://rcood.rc.fas.harvard.edu/rnode/{nodelist}.rc.fas.harvard.edu/8001",
    "\n",
)

app = FastAPI(title="DANNCE Browser")

app.mount("/static", StaticFiles(directory="static"), name="static")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/ping")
def route_ping():
    return {"message": "pong"}


templates = Jinja2Templates(directory="templates")


@app.get("/datafolder/", response_class=HTMLResponse)
async def read_item(request: Request):
    return templates.TemplateResponse(request=request, name="datafolder.html")


class DfInfoBody(BaseModel):
    path: str


@app.post("/api/df-info")
def list_dir(df_info: DfInfoBody):
    response = get_info_from_df_path(df_info.path)
    return {"response": response}


@app.get("/", response_class=HTMLResponse)
async def index_page(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")
