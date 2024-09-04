from datetime import datetime, timedelta
from fastapi.security import HTTPBasic, OAuth2PasswordBearer
import jwt
from passlib.context import CryptContext
from app.setting.setting import settings

secret = settings.get_secret()
pwd_context = CryptContext(schemes=secret['hash'], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="admin/login")

security = HTTPBasic()

def create_access_token(data: dict, expires_delta: timedelta = None):
    if expires_delta:
        expire = datetime.now() + expires_delta
    else:
        expire = datetime.now() + timedelta(minutes=secret['token_expire'])

    payload = {"exp": expire, **data}
    encoded_jwt = jwt.encode(payload, secret['secret_key'], algorithm=secret['algorithm'])
    return encoded_jwt

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def decode_token(token):
    try:
        payload = jwt.decode(token, secret['secret_key'], algorithms=[secret['algorithm']])
        return payload
    except jwt.exceptions.PyJWTError:
        return {}