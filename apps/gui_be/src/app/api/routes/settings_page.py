"""
/settings_page
"""
from fastapi import APIRouter, HTTPException,UploadFile
from pathlib import PurePath

from app.api.deps import SessionDep
from app.core.db import TABLE_GLOBAL_STATE
from app.core.config import settings
from app.base_logger import logger
import scipy.io

router = APIRouter()

@router.get("/skeleton")
def get_skeleton_route(conn: SessionDep):
  row = conn.execute(f"SELECT skeleton_file FROM {TABLE_GLOBAL_STATE} WHERE id=0").fetchone()
  row = dict(row)
  if row['skeleton_file']:
    return {'data' : row['skeleton_file']}
  else:
    return {"data" : None}

@router.delete("/skeleton")
def delete_skeleton_route(conn: SessionDep):

  conn.execute(f"UPDATE {TABLE_GLOBAL_STATE} SET skeleton_file=NULL WHERE id=0")
  conn.execute("COMMIT")

  settings.SKELETON_FILE.unlink()

@router.post('/skeleton')
def upload_skeleton_route(conn: SessionDep, file: UploadFile):
  # validate skeleton file

  orig_path = PurePath(file.filename)
  filename = file.filename
  suffix = orig_path.suffix
  if suffix != ".mat":
    raise HTTPException(400, "Must upload a valid .mat file")
  try:
    m = scipy.io.loadmat(file.file)
    assert 'joints_idx' in m
    assert 'joint_names' in m
  except Exception as e:
    raise HTTPException(400, "Unable to load .mat file")

  with open(settings.SKELETON_FILE, "wb") as f:
    file.file.seek(0)
    f.write(file.file.read())

  logger.warning(f"Setting skeleton path to: {filename}")
  conn.execute(
    f"""UPDATE {TABLE_GLOBAL_STATE} SET skeleton_file=? WHERE id=0""", (filename,)
  )
  conn.execute('commit')



