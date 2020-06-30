import os
import sqlite3
from typing import List, Union


def ensure_path(full_path: str) -> None:
    dirname = os.path.dirname(full_path)
    if not os.path.exists(dirname):
        os.makedirs(dirname)


class Users:
    def __init__(self, db_path: str) -> None:
        self.db_path = db_path
        ensure_path(db_path)

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

        # TODO: extra fields for:
        # activated_account, bool
        # activated_on, datetime

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

    def update_email(self, id: int, email: str) -> None:
        with sqlite3.connect(self.db_path) as db:
            cursor = db.cursor()
        updateEmail = """UPDATE users SET email = ? WHERE id = ?"""
        cursor.execute(updateEmail, (email, id))
        db.commit()

    def update_password(self, id: int, password: str) -> None:
        with sqlite3.connect(self.db_path) as db:
            cursor = db.cursor()
        updatePassword = """UPDATE users SET password = ? WHERE id = ?"""
        cursor.execute(updatePassword, (password, id))
        db.commit()

    def delete_user(self, id: int) -> None:
        with sqlite3.connect(self.db_path) as db:
            cursor = db.cursor()
        deleteUser = """DELETE FROM users WHERE id = ?"""
        cursor.execute(deleteUser, (id,))
        db.commit()

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
        ensure_path(db_path)

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

    def read_log(self, user_id: int) -> int:
        with sqlite3.connect(self.db_path) as db:
            cursor = db.cursor()
        readData = """SELECT timestamp, success FROM logs WHERE user_id = (?)"""
        cursor.execute(readData, (user_id,))
        return cursor.fetchall()

    def delete_userlog(self, user_id: int) -> None:
        with sqlite3.connect(self.db_path) as db:
            cursor = db.cursor()
        deleteUserlog = """DELETE FROM logs WHERE user_id = ?"""
        cursor.execute(deleteUserlog, (user_id,))
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
