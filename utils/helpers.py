from database.db import get_db

def get_cursor():
    db = get_db()
    cur = db.cursor()
    return db, cur
