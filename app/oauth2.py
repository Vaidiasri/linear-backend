from jose import JWTError, jwt
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

# .env file se environment variables load karo
load_dotenv()

# JWT Configuration .env se load karo
SECRET_KEY = os.getenv("SECRET_KEY")  # Ye secret key token sign karne ke liye
ALGORITHM = os.getenv("ALGORITHM", "HS256")  # Default HS256 algorithm use karenge
EXPIRE_MINUTES = int(
    os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30")
)  # Token 30 min baad expire hoga

# Agar SECRET_KEY nahi mila toh error throw karo
if not SECRET_KEY:
    raise ValueError("SECRET_KEY environment variable nahi mila .env file mein")


def create_access_token(data: dict):
    """
    JWT access token banata hai
    data: dict - Token mein store karne ka data (usually user email/id)
    Returns: encoded JWT token string
    """
    # Original data ko copy karo taaki modify na ho
    to_encode = data.copy()

    # Expiry time calculate karo (current time + EXPIRE_MINUTES)
    time_delta = timedelta(minutes=EXPIRE_MINUTES)
    to_encode.update({"exp": datetime.utcnow() + time_delta})

    # Token encode karo SECRET_KEY aur ALGORITHM se
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
