import jwt
from passlib.context import CryptContext
from models.database import sessionLocal
from models import userinfo

SECRET_KEY = "87f2c2be95c484df33a2a438a8a0284bd0cf79d8497d1b53e20f3ba9162b5e6e"


def get_db():
    db = sessionLocal()
    try:
        yield db
    finally:
        db.close()


def generate_token(emailid: str) -> str:
    payload = {"emailID": emailid}
    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
    return token


def get_hash(password: str):
    hash_pass = CryptContext(scheme=["bcrypt"], deprecated="auto").hash(password)
#     pwd_hashing = CryptContext(schemes=["bcrypt"], deprecated="auto")
#     hash_pass = pwd_hashing.hash(password)
    return hash_pass


def verify_hash(password: str, hash_password: str) -> bool:
    pass_hash = CryptContext(schemes=["bcrypt"])
    return pass_hash.verify(password, hash_password)


def authenticate_user(email: str, password: str) -> bool:
    db = sessionLocal()
    usermail = db.query(userinfo.User).filter(userinfo.User.email == email).first()
    db.close()
    if usermail and verify_hash(password, usermail.password):
        return True
    return False
