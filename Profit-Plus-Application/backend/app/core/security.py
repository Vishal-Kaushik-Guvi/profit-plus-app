from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
import bcrypt
from app.config import settings

# Password hashing setup
# In Java → new BCryptPasswordEncoder()

# ── Password Functions ──────────────────────────────────────────────

def hash_password(password: str) -> str:
    """Convert plain password to hashed password"""
    # In Java → passwordEncoder.encode(password)
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Check if entered password matches stored hash"""
    # In Java → passwordEncoder.matches(plain, hashed)
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

# ── JWT Functions ───────────────────────────────────────────────────

def create_access_token(data: dict) -> str:
    """
    Create a JWT token with expiry
    In Java → Jwts.builder().setSubject(...).signWith(...).compact()
    """
    to_encode = data.copy()

    # Set expiry time
    expire = datetime.now(timezone.utc).replace(tzinfo=None) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    to_encode.update({"exp": expire})

    # Sign and create token
    token = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    return token

def decode_access_token(token: str) -> dict:
    """
    Decode and verify a JWT token
    In Java → Jwts.parser().setSigningKey(...).parseClaimsJws(token)
    """
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        return payload
    except JWTError:
        return None