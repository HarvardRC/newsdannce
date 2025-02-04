import sqlite3

from app.core.db import TABLE_PREDICTION, TABLE_WEIGHTS
from app.migrations.migration_util import Migration
from app.core.config import settings
from pathlib import Path

from app.utils.predictions import get_prediction_filename
from app.utils.weights import get_latest_checkpoint_filename


def up(curr: sqlite3.Cursor):
    curr.execute(
        f"""
ALTER TABLE {TABLE_PREDICTION}
ADD COLUMN filename TEXT"""
    )
    curr.execute(f"""
ALTER TABLE {TABLE_WEIGHTS}
ADD COLUMN filename TEXT;""")

    # add filename to all completed PREDICTIONs

    rows = curr.execute(f"SELECT id,path,mode FROM {TABLE_PREDICTION} WHERE filename IS NULL AND status = 'COMPLETED'")
    rows = [dict(row) for row in rows]
    pred_filename_pairs = []
    for pred_row in rows:
        id = pred_row['id']
        filename = get_prediction_filename(pred_row['mode'], pred_row['path'])
        pred_filename_pairs.append((filename,id))

    curr.executemany(
        f"""
UPDATE {TABLE_PREDICTION} SET filename = ? WHERE id = ?
""", pred_filename_pairs
    )

    # add filename to all completed WEIGHTSs

    rows = curr.execute(f"SELECT id,path,mode FROM {TABLE_WEIGHTS} WHERE filename IS NULL AND status = 'COMPLETED'")
    rows = [dict(row) for row in rows]
    wts_filename_pairs = []
    for wt_row in rows:
        id = wt_row['id']
        latest_filename = get_latest_checkpoint_filename(wt_row['path'])
        wts_filename_pairs.append((latest_filename, id))

    curr.executemany(
        f"""
UPDATE {TABLE_WEIGHTS} SET filename = ? WHERE id = ?
""", wts_filename_pairs
    )


def down(curr: sqlite3.Cursor):
    curr.execute(
        f"""
ALTER TABLE {TABLE_PREDICTION}
ADD COLUMN filename TEXT"""
    )

    curr.execute(
        f"""
ALTER TABLE {TABLE_WEIGHTS}
ADD COLUMN filename TEXT;
""")


v1 = Migration("v1", up, None)
