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
        # Connect to Database tables for users and logs
        self.users = users
        self.logs = logs

        # Logged out by default
        self.email = ""
        self.id = None
        self._set_actions()
        self._set_options()

    def register(self) -> None:
        if self._is_loggedin():
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

        print("\nYour account has been created.\n")
        self._send_activation_email(email=email)

    def login(self) -> None:
        if self._is_loggedin():
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

        self._loggedin(email=email, id=query["id"])

    def print_log(self) -> None:
        if not self._is_loggedin():
            raise InvalidAction("You must be logged in to check your log.")
        print("\nAccess time, Authentication success")
        for log in self.logs.read_log(self.id):
            print(log)

    def change_email(self) -> None:
        if not self._is_loggedin():
            raise InvalidAction("You must be logged in to change your email.")

        query = self.users.read_user(email=self.email)
        success = self._authenticate(query["password"])

        if success:
            try:
                newEmail = self._get_email()
                newQuery = self.users.read_user(email=newEmail)
                assert not newQuery, "Email already in use.\n"

                self.users.update_email(id=self.id, email=newEmail)
                self.email = newEmail

                print(f"\nYour email has been changed to {newEmail}.\n")
            except AssertionError as msg:
                print(msg)
        else:
            print("Wrong password.\n")

    def change_password(self) -> None:
        if not self._is_loggedin():
            raise InvalidAction("You must be logged in to change your password.")

        query = self.users.read_user(email=self.email)
        success = self._authenticate(query["password"])

        if success:
            try:
                hashedPassword = self._new_password()
                self.users.update_password(id=self.id, password=hashedPassword)

                print("\nYour password has been changed.\n")
            except AssertionError as msg:
                print(msg)
        else:
            print("Wrong password.\n")

    def logout(self) -> None:
        if not self._is_loggedin():
            raise InvalidAction("You must be logged in to log out.")
        self._loggedout()

    def delete_account(self) -> None:
        if not self._is_loggedin():
            raise InvalidAction("You must be logged in to delete your account.")

        query = self.users.read_user(email=self.email)
        success = self._authenticate(query["password"])

        if success:
            try:
                self.users.delete_user(id=self.id)
                self.logs.delete_userlog(user_id=self.id)
                print("\nYour account and related data have been deleted.\n")
            except AssertionError as msg:
                print(msg)
        else:
            print("Wrong password.\n")

        self.logout()

    def _new_password(self) -> str:
        password = getpass("\nPlease enter the new password: ")
        password_re = getpass("Please retype the new password: ")
        self.validate_password(password, password_re)
        return encrypt_password(password)

    def _get_email(self) -> str:
        email = input("\nPlease enter a valid email address: ")
        self.validate_email(email)
        return email

    def _authenticate(self, password: str) -> bool:
        input = getpass("Please enter your password: ")
        return check_password(input, password)

    def _generate_confirmation_token(self) -> None:
        """Generates confirmation token
        ideally within a web framework such as Django or Flask,
        or secrets.token_urlsafe() from the standard lib"""
        pass

    def _send_activation_email(self, email: str) -> None:
        """Sends email to specified address, with a generated confirmation token.
        Possible implementation using libraries smtplib, email
        """
        print("\n**Email with an activation link would have been sent now.**\n")

    def _is_loggedin(self) -> bool:
        return bool(self.email)

    def _loggedin(self, email: str, id: int) -> None:
        self.email = email
        self.id = id
        self._set_actions()
        self._set_options()
        print("You are logged in.\n")

    def _loggedout(self) -> None:
        self.email = ""
        self.id = None
        self._set_actions()
        self._set_options()
        print("You have been logged out.\n")

    def _set_options(self) -> None:
        if self._is_loggedin():
            self.options = {
                "1": "Print log",
                "2": "Change email",
                "3": "Change password",
                "4": "Log out",
                "5": "Delete account",
            }
        else:
            self.options = {"1": "Register", "2": "Login"}

    def _set_actions(self) -> None:
        if self._is_loggedin():
            self.actions = {
                "Print log": self.print_log,
                "Change email": self.change_email,
                "Change password": self.change_password,
                "Log out": self.logout,
                "Delete account": self.delete_account,
            }
        else:
            self.actions = {"Register": self.register, "Login": self.login}

    @classmethod
    def validate_email(cls, email: str) -> None:
        msg = "Invalid email address. Try x@x.x, where 'x' can be any alphanumeric char.\n"
        assert cls.EMAIL_REGEX.fullmatch(email), msg

    @classmethod
    def validate_password(cls, pw1: str, pw2: str) -> None:
        assert pw1 == pw2, "Passwords must match.\n"
