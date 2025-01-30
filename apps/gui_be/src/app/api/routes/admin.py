"""Admin operations E.g. create database, set fake data
/admin
"""

from fastapi import APIRouter

router = APIRouter()


@router.post("/test")
def test_route():
    return {"message": "tested"}
