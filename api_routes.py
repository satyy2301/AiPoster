from fastapi import APIRouter, Depends, HTTPException, logger, status
from auth import ALGORITHM, SECRET_KEY, User, supabase, oauth2_scheme, get_user
from jose import JWTError, jwt

router = APIRouter()

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError as e:
        logger.error(f"JWT Error: {str(e)}")
        raise credentials_exception
    
    user = get_user(username)
    if user is None:
        logger.error(f"User not found: {username}")
        raise credentials_exception
    
    return user

@router.post("/api-keys")
async def save_api_keys(
    keys: dict,
    current_user: User = Depends(get_current_user)
):
    try:
        # Use username as the identifier instead of id
        response = supabase.table("users").update({
            "api_keys": keys
        }).eq("username", current_user["username"]).execute()
        
        if not response.data:
            raise HTTPException(status_code=400, detail="Failed to update API keys")
            
        return {"message": "API keys saved successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@router.get("/api-keys")
async def get_api_keys(current_user: User = Depends(get_current_user)):
    return current_user["api_keys"]