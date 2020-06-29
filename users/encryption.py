import crypt  # Only supported in linux
from hmac import compare_digest

# import bcrypt  # OS independent, but it not in standard lib


ROUNDS = 10


def check_password(inputPassword: str, storedPassword: str) -> str:
    """Compares input password to a hashed one."""
    return compare_digest(storedPassword, crypt.crypt(inputPassword, storedPassword))


def encrypt_password(password: str) -> bool:
    """Encrypts input password so it can be stored"""
    return crypt.crypt(password)
