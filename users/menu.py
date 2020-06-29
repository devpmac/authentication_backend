import re
from getpass import getpass

from users import check_password, encrypt_password, Users, Logs


class InvalidAction(Exception):
    pass


class MaxTries(Exception):
    pass


class Interface:
    EMAIL_REGEX = re.compile(r"[^@]+@[^@]+\.[^@]+")
    NUM_TRIES = 3

    def __init__(self, users: Users, logs: Logs) -> None:
        self.users = users
        self.logs = logs

        self.email = ""  # logged out by default
        self.set_actions()
        self.set_options()

    def register(self) -> None:
        if self.is_loggedin():
            raise InvalidAction("A logged in user can not register.")

        for _ in range(self.NUM_TRIES):
            try:
                email = self._get_email()

                # DB validation
                query = self.users.read_user(email=email)
                assert not query, "Email already in use.\n"

                hashedPassword = self._new_password()

                self.users.create_user(email=email, password=hashedPassword)

                break

            except AssertionError as msg:
                print(msg)

        else:
            raise MaxTries("Max attempts exceeded, please try again later.\n")

        # TODO: WRITE EMAIL
        # TODO: GENERATE LINK
        print("\nYour account has been created.\n")

    def login(self) -> None:
        if self.is_loggedin():
            raise InvalidAction("Already logged in.")

        for _ in range(self.NUM_TRIES):
            try:
                email = self._get_email()

                # DB email validation
                query = self.users.read_user(email=email)
                assert query, "Email address not found.\n"

                # Check if account is blocked
                assert not self.users.is_locked(
                    email
                ), "\nThe account is blocked for now.\n"

                # Check if password matches
                success = self._authenticate(query["password"])
                # Register in logs database
                self.logs.create_log(success, query["id"])

                if success:
                    break
                else:
                    print("Wrong password.\n")
                    if self.logs.failed_attempts(query["id"]) > 4:
                        "\nThe account will be blocked for 30 minutes.\n"
                        self.users.lock_user(email=email)

            except AssertionError as msg:
                print(msg)

        else:
            raise MaxTries("Max attempts exceeded. Try again later.\n")

        self.loggedin(email)

    def logout(self) -> None:
        if not self.is_loggedin():
            raise InvalidAction("You must be logged in to log out.")
        self.loggedout()

    def _new_password(self) -> str:
        password = getpass("Please enter the new password: ")
        password_re = getpass("Please retype the new password: ")
        self.validate_password(password, password_re)
        return encrypt_password(password)

    def _get_email(self) -> str:
        email = input("Please enter a valid email address: ")
        self.validate_email(email)
        return email

    def _authenticate(self, password: str) -> bool:
        input = getpass("Please enter your password: ")
        return check_password(input, password)

    def is_loggedin(self) -> bool:
        return bool(self.email)

    def loggedin(self, email: str) -> None:
        self.email = email
        self.set_actions()
        self.set_options()
        print("You are logged in.\n")

    def loggedout(self) -> None:
        self.email = ""
        self.set_actions()
        self.set_options()
        print("You have been logged out.\n")

    def set_options(self) -> None:
        if self.is_loggedin():
            self.options = {"1": "Change password", "2": "Check log", "3": "Log out"}
        else:
            self.options = {"1": "Register", "2": "Login"}

    def set_actions(self) -> None:
        if self.is_loggedin():
            self.actions = {
                "Change password": "FIXME",
                "Check log": "FIXME",
                "Log out": self.logout,
            }
        else:
            self.actions = {"Register": self.register, "Login": self.login}
        return self.actions

    @classmethod
    def validate_email(cls, email: str) -> None:
        assert cls.EMAIL_REGEX.fullmatch(email), "Invalid email address.\n"

    @classmethod
    def validate_password(cls, pw1: str, pw2: str) -> None:
        assert pw1 == pw2, "Passwords do not match.\n"
