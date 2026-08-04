from typing import cast

from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")


class PasswordService:
    def hash(self, password: str) -> str:
        return cast(str, pwd_context.hash(password))

    def verify(self, password: str, password_hash: str) -> bool:
        return cast(bool, pwd_context.verify(password, password_hash))
