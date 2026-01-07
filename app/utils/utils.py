from passlib.context import CryptContext

# Ye setup hai jo batata hai bcrypt use karna hai
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Signup ke waqt use hoga
def hash_password(password: str):
    return pwd_context.hash(password)

# Login ke waqt use hoga
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)