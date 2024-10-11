from sqlite3 import Connection
from typing import Annotated

from fastapi import Depends

from app.core.db import get_db


SessionDep = Annotated[Connection, Depends(get_db)]
