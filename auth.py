import hashlib
import logging
from supabase import create_client, Client
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from datetime import datetime, timedelta
from pydantic import BaseModel
from cryptography.fernet import Fernet
from config import settings  # Import from config instead of os.getenv

logger = logging.getLogger(__name__)

# Supabase setup - Get from config
SUPABASE_URL = settings.SUPABASE_URL
SUPABASE_KEY = settings.SUPABASE_KEY

try:
    if not SUPABASE_URL or not SUPABASE_KEY:
        logger.warning("Supabase credentials missing in settings")
        supabase = None
    else:
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        # Test connection with error handling
        try:
            result = supabase.table("users").select("*").limit(1).execute()
            logger.info("Supabase connected successfully")
        except Exception as test_error:
            logger.warning(f"Supabase test query failed but continuing: {test_error}")
            # Still set supabase, but log the warning
except Exception as e:
    logger.error(f"Supabase initialization failed: {str(e)}")
    supabase = None

# Security setup - Get from config
SECRET_KEY = settings.SECRET_KEY
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1440  # 24 hours
REFRESH_TOKEN_EXPIRE_DAYS = 7  # 7 days

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# User model
class User(BaseModel):
    username: str
    email: str
    disabled: bool = False

class UserInDB(User):
    hashed_password: str
    api_keys: dict = {}

# Simple password hashing without external dependencies
def get_password_hash(password: str) -> str:
    """Hash password using SHA256 (for development only)"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash"""
    return get_password_hash(plain_password) == hashed_password

# Database functions
def get_user(username: str):
    if not supabase:
        logger.error("Supabase not initialized")
        return None
        
    try:
        res = supabase.table("users").select("*").eq("username", username).execute()
        return res.data[0] if res.data else None
    except Exception as e:
        logger.error(f"Error getting user {username}: {str(e)}")
        return None

def create_user(username: str, email: str, password: str):
    if not supabase:
        raise Exception("Supabase not initialized. Please check your Supabase credentials in the .env file.")
        
    try:
        # Check if user already exists
        existing_user = get_user(username)
        if existing_user:
            raise Exception(f"User {username} already exists")
            
        hashed_password = get_password_hash(password)
        user_data = {
            "username": username,
            "email": email,
            "hashed_password": hashed_password,
            "api_keys": {},
            "created_at": datetime.utcnow().isoformat()
        }
        result = supabase.table("users").insert(user_data).execute()
        
        if result.data:
            logger.info(f"User {username} created successfully")
            return {"message": f"User {username} created successfully", "user": result.data[0]}
        else:
            raise Exception("Failed to create user in database")
            
    except Exception as e:
        logger.error(f"Error creating user {username}: {str(e)}")
        raise e

# Auth functions
def authenticate_user(username: str, password: str):
    if not supabase:
        logger.error("Supabase not initialized")
        return False
        
    try:
        user = get_user(username)
        if not user:
            logger.warning(f"User {username} not found")
            return False
            
        if not verify_password(password, user["hashed_password"]):
            logger.warning(f"Invalid password for user {username}")
            return False
            
        logger.info(f"User {username} authenticated successfully")
        return user
        
    except Exception as e:
        logger.error(f"Authentication error for {username}: {str(e)}")
        return False

def create_access_token(data: dict, expires_delta: timedelta = None):
    """Create access token with optional custom expiration"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_refresh_token(data: dict):
    """Create a longer-lived refresh token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str):
    """Verify token and return payload, or raise exception"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError as e:
        logger.warning(f"Token verification failed: {e}")
        return None

def encrypt_data(data: str, key: str) -> str:
    fernet = Fernet(key)
    return fernet.encrypt(data.encode()).decode()

def decrypt_data(encrypted_data: str, key: str) -> str:
    fernet = Fernet(key)
    return fernet.decrypt(encrypted_data.encode()).decode()