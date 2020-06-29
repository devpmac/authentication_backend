import functools
import re
import sqlite3
from typing import Any, Callable
from getpass import getpass

from users import check_password, DB_PATH, encrypt_password, Users, Logs


class Menu:
    EMAIL_REGEX = re.compile(r"[^@]+@[^@]+\.[^@]+")
    NUM_TRIES = 3

    def __init__(self, users: Users, logs: Logs) -> None:
        self.users = users
        self.logs = logs

    def register(self) -> None:
        for _ in range(self.NUM_TRIES):
            try:
                email = self.get_email()

                # DB validation
                query = self.users.read_user(db_path=DB_PATH, email=email)
                assert not query, "Email already in use.\n"

                hashedPassword = self.new_password()

                self.users.create_user(
                    db_path=DB_PATH, email=email, password=hashedPassword
                )

                break

            except AssertionError as msg:
                print(msg)

        else:
            raise Exception("Max attempts exceeded, please try again later.\n")

        # TODO: WRITE EMAIL
        # TODO: GENERATE LINK
        print("Your account has been created.\n")

    def login(self) -> None:
        for _ in range(self.NUM_TRIES):
            try:
                email = self.get_email()

                # DB email validation
                query = self.users.read_user(db_path=DB_PATH, email=email)
                assert query, "Email Address not found.\n"

                # TODO: assert last 10 minutes counts success = 0 < 5, "5 unsuccessful attempts in the last 10 minutes, try again later."

                success = self.authenticate(query["password"])
                self.logs.create_log(success, query["id"])

                if success:
                    break
                else:
                    print("Wrong password.\n")

            except AssertionError as msg:
                print(msg)

        else:
            # TODO: LOCK ACCOUNT
            raise Exception("Max attempts exceeded, please try again later.\n")

        print("You are logged in.\n")

    def get_email(self) -> str:
        email = input("Please enter a valid email address: ")
        self.validate_email(email)
        return email

    def authenticate(self, password: str) -> bool:
        input = getpass("Please enter your password: ")
        return check_password(input, password)

    def new_password(self) -> str:
        password = getpass("Please enter your password: ")
        password_re = getpass("Please retype your password: ")
        self.validate_password(password, password_re)
        return encrypt_password(password)

    @classmethod
    def validate_email(cls, email: str) -> None:
        assert cls.EMAIL_REGEX.fullmatch(email), "Invalid email address.\n"

    @classmethod
    def validate_password(cls, pw1: str, pw2: str) -> None:
        assert pw1 == pw2, "Passwords do not match.\n"
