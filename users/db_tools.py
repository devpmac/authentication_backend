import sqlite3
from typing import List, Union


class Users:
    def __init__(self, db_path: str) -> None:
        self.db_path = db_path

        with sqlite3.connect(db_path) as db:
            cursor = db.cursor()

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS users(
                id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
                email VARCHAR NOT NULL UNIQUE,
                password VARCHAR NOT NULL,
                registered_on DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
                locked_until DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL);"""
        )

    def create_user(self, email: str, password: str) -> None:
        with sqlite3.connect(self.db_path) as db:
            cursor = db.cursor()
        insertData = """INSERT INTO users(email, password) VALUES(?, ?)"""
        cursor.execute(insertData, (email, password))
        db.commit()

    def read_user(self, email: str) -> Union[sqlite3.Row, None]:
        with sqlite3.connect(self.db_path) as db:
            db.row_factory = sqlite3.Row
            cursor = db.cursor()
        find_user = "SELECT * FROM users WHERE email = ? LIMIT 1"
        cursor.execute(find_user, (email,))
        return cursor.fetchone()

    def lock_user(self, email: str) -> None:
        with sqlite3.connect(self.db_path) as db:
            cursor = db.cursor()
        lockUser = """UPDATE users SET locked_until = Datetime('now', '+30 minutes') WHERE email = ?"""
        cursor.execute(lockUser, (email,))
        db.commit()

    def is_locked(self, email: str) -> bool:
        with sqlite3.connect(self.db_path) as db:
            db.row_factory = sqlite3.Row
            cursor = db.cursor()
        isLocked = """SELECT * FROM users WHERE email = ? AND locked_until > Datetime('now') LIMIT 1"""
        cursor.execute(isLocked, (email,))
        return bool(cursor.fetchone())

    def read_all(self) -> List:
        with sqlite3.connect(self.db_path) as db:
            cursor = db.cursor()
        cursor.execute("SELECT * FROM users")
        return cursor.fetchall()


class Logs:
    def __init__(self, db_path: str) -> None:
        self.db_path = db_path

        with sqlite3.connect(db_path) as db:
            cursor = db.cursor()

        cursor.execute(
            """
        CREATE TABLE IF NOT EXISTS logs(
            id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
            success BOOLEAN NOT NULL CHECK (success IN (0,1)),
            user_id INTEGER NOT NULL REFERENCES users(id),
            FOREIGN KEY (user_id)
                REFERENCES users (id));"""
        )

    def create_log(self, success: bool, user_id: int) -> None:
        with sqlite3.connect(self.db_path) as db:
            cursor = db.cursor()
        insertData = """INSERT INTO logs(success, user_id) VALUES(?, ?)"""
        cursor.execute(insertData, (int(success), user_id))
        db.commit()

    def failed_attempts(self, user_id: int) -> int:
        with sqlite3.connect(self.db_path) as db:
            cursor = db.cursor()
        # FIXME: Hardcoded 10 minute window
        readData = """SELECT COUNT(*) FROM logs WHERE user_id = (?) AND success = 0 AND timestamp >= Datetime('now', '-10 minutes')"""
        cursor.execute(readData, (user_id,))
        return cursor.fetchone()[0]

    def read_all(self) -> List:
        with sqlite3.connect(self.db_path) as db:
            cursor = db.cursor()
        cursor.execute("SELECT * FROM logs")
        return cursor.fetchall()
