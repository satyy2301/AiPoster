from supabase import create_client, Client
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
import os
from pydantic import BaseModel
from cryptography.fernet import Fernet

# Supabase setup
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Security setup
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# User model
class User(BaseModel):
    username: str
    email: str
    disabled: bool = False

class UserInDB(User):
    hashed_password: str
    api_keys: dict = {}

# Database functions
def get_user(username: str):
    res = supabase.table("users").select("*").eq("username", username).execute()
    return res.data[0] if res.data else None

def create_user(username: str, email: str, password: str):
    hashed_password = pwd_context.hash(password)
    user_data = {
        "username": username,
        "email": email,
        "hashed_password": hashed_password,
        "api_keys": {}
    }
    return supabase.table("users").insert(user_data).execute()

# Auth functions
def authenticate_user(username: str, password: str):
    user = get_user(username)
    if not user or not pwd_context.verify(password, user["hashed_password"]):
        return False
    return user

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def encrypt_data(data: str, key: str) -> str:
    fernet = Fernet(key)
    return fernet.encrypt(data.encode()).decode()

def decrypt_data(encrypted_data: str, key: str) -> str:
    fernet = Fernet(key)
    return fernet.decrypt(encrypted_data.encode()).decode() 