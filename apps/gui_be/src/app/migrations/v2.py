import sqlite3

from app.core.db import TABLE_VIDEO_FOLDER
from app.migrations.migration_util import Migration

# replace "None" entries with None/null value in video folder
def up(curr: sqlite3.Cursor):
    curr.execute(f"""
    UPDATE {TABLE_VIDEO_FOLDER}
    SET com_labels_file = null
    WHERE com_labels_file = 'None'
                 """)
    curr.execute(f"""
    UPDATE {TABLE_VIDEO_FOLDER}
    SET dannce_labels_file = null
    WHERE dannce_labels_file= 'None'
                 """)


def down(curr: sqlite3.Cursor):
    pass

v2 = Migration("v2", up, None)
