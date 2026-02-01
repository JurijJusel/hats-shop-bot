import sqlite3
import logging

logger = logging.getLogger(__name__)


def db_execute(query: str, params: tuple = (), fetch: str = None, db_name: str = None):
    """
    Universali DB funkcija.

    Args:
        query: SQL užklausa
        params: Parametrai užklausai (tuple)
        fetch: 'one' | 'all' | None (jei INSERT/UPDATE/DELETE)
        db_name: DB failo pavadinimas (pvz: DB_BANNED_USERS)
    Returns:
        - fetch='one': vieną rezultatą arba None
        - fetch='all': visus rezultatus (list)
        - fetch=None: True jei sėkminga, False jei klaida
    Pavyzdžiai:
        result = db_execute("SELECT * FROM users WHERE id=?", (123,), fetch='one', db_name=DB_BANNED_USERS)
        success = db_execute("INSERT INTO blacklist VALUES (?, ?)", (user_id, admin_id), db_name=DB_BANNED_USERS)
    """
    if db_name is None:
        logger.error("db_execute: db_name negali būti None!")
        return False if fetch is None else None

    try:
        with sqlite3.connect(db_name) as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)

            if fetch == 'one':
                return cursor.fetchone()
            elif fetch == 'all':
                return cursor.fetchall()
            elif fetch == 'lastrowid':
                conn.commit()
                return cursor.lastrowid
            else:
                conn.commit()
                return True
    except sqlite3.Error as e:
        logger.error(f"DB klaida ({db_name}): {e}")
        return False if fetch is None else None
