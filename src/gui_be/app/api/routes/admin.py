"""Admin operations E.g. create database, set fake data"""

from fastapi import APIRouter
from app.core.db import (
    init_db,
    populate_db,
    populate_real_data,
)
# import caldannce


router = APIRouter()


@router.post("/init-db")
def route_init_db():
    init_db()
    return {"message": "done"}


@router.post("/populate-db")
def route_populate_db():
    init_db()
    populate_db()
    return {"message": "done"}


@router.post("/load-real-data")
def route_load_real_data():
    # init_db()
    populate_real_data()
    return {"message": "done"}


@router.post("/test")
def test_route():
    return {"message": "done"}
