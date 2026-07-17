from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.core.security import decode_access_token
from app.models.user import User

# Tells FastAPI where the login endpoint is
# In Java → configure(HttpSecurity http) in SecurityConfig
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# ── Database Session ────────────────────────────────────────────────

def get_db():
    """
    Creates a new DB session for each request,
    closes it when request is done.
    In Java → @PersistenceContext EntityManager em
    """
    db = SessionLocal()
    try:
        yield db        # give the session to the route
    finally:
        db.close()      # always close after request ends

# ── Get Current User ────────────────────────────────────────────────

def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """
    Reads JWT token from request header,
    finds and returns the logged in user.
    In Java → SecurityContextHolder.getContext().getAuthentication()
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # Decode the token
    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception

    # Get user id from token
    user_id: str = payload.get("sub")
    if user_id is None:
        raise credentials_exception

    # Find user in database
    try:
        import uuid
        uuid.UUID(user_id)
    except ValueError:
        raise credentials_exception
        
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exception

    return user