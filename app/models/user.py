# app/models/user.py
# handles user accounts, registration, password security and login authentication
# defines how users are stored in the database and provides important functionality 
# EX: create account, store passwords, verification, generating JWTs, verifying tokens, tracking user info

from datetime import datetime, timedelta
import uuid # generates unique identifiers
from typing import Optional, Dict, Any

# interacting with the database
from sqlalchemy import Column, String, DateTime, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base
from sqlalchemy.exc import IntegrityError

# handles password hashing
from passlib.context import CryptContext

# handles JWT creation and validation
from jose import JWTError, jwt

# handles data validation
from pydantic import ValidationError
from app.schemas.base import UserCreate
from app.schemas.user import UserResponse, Token

Base = declarative_base() # database foundations

# configures how passwords are hashed
pwd_context = CryptContext(
    schemes=["bcrypt"], 
    deprecated="auto"
)

# Move to config for authentication tokens
SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

class User(Base): # user class represents a database table
    __tablename__ = 'users' # table name in PostgreSQL

    # defines the columns in the database table
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    username = Column(String(50), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    last_login = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # how the object is represented when printed/inspected in Python
    # useful for debugging and inspecting user objects
    # self = specific user object
    def __repr__(self):
        return f"<User(name={self.first_name} {self.last_name}, email={self.email})>"

    @staticmethod
    def hash_password(password: str) -> str:
        return pwd_context.hash(password) # what gets stored in the database
    # hashing the same password twice will produce different hashes (expected behavior)

    # used during login - accesses a particular user's stored hash
    # compared entered password against hashed password in db
    def verify_password(self, plain_password: str) -> bool:
        return pwd_context.verify(plain_password, self.password)

    # creates a JWT access token with an expiration time
    # expiration is optional, there is a default included
    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
        to_encode = data.copy() # don't want to modify the original dictionary that was passed to the function
        expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)) # calculates when the token expires
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        # returns the encoded JWT token as a string
        # FE will receive token after successful auth

    # verifies and decodes a JWT token
    # should return UUID representing authenticated user or None if fails
    @staticmethod
    def verify_token(token: str) -> Optional[UUID]:
        try: # decodes and verifies the JWT token, checks expiration claim
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            user_id = payload.get("sub") # retrieves ID from token
            return uuid.UUID(user_id) if user_id else None # converts ID to UUID or returns None if missing
        except (JWTError, ValueError): # catches invalid tokens or if the UUID is malformed
            return None

    @classmethod
    # cls goes to the user class, knows that it has been defined
    # db = database session, allows function to query/modify the db
    # user data = info submitted by someone trying to register
    def register(cls, db, user_data: Dict[str, Any]) -> "User": 
        try:
            # Validate password length first
            password = user_data.get('password', '') # retrieves password from user data, defaults to empty string if missing
            if len(password) < 6:  # Strictly less than 6 characters, raises ValueError if password is too short
                raise ValueError("Password must be at least 6 characters long")
            
            # Check if email/username exists
            existing_user = db.query(cls).filter( # .filter adds conditions to the query
                (cls.email == user_data.get('email')) | # checks email address
                (cls.username == user_data.get('username')) # checks username
            ).first() # returns first matching user
            # if no matching user exists, returns None
            
            if existing_user:
                raise ValueError("Username or email already exists") # stops if existing user is found (prevents duplicates)
                # thrown when anything goes wrong essentially, cause FastAPI to throw a request
                # what gets shown in the user interface (FE validation to come in a later unit)

            # Validate using Pydantic schema - checking that the submitted data follows the schema
            user_create = UserCreate.model_validate(user_data)
            
            # Create new user instance with the assigned information
            # takes information from user_create and puts them into a new User object
            new_user = cls(
                first_name=user_create.first_name,
                last_name=user_create.last_name,
                email=user_create.email,
                username=user_create.username,
                password=cls.hash_password(user_create.password),
                is_active=True,
                is_verified=False
            )
            
            db.add(new_user) # adds the new user to the database session
            db.flush() # flushes the pending changes to the database, not committing to the transaction
            return new_user
            
        except ValidationError as e:
            raise ValueError(str(e)) # pragma: no cover
        except ValueError as e:
            raise e

    # handles users trying to log into the app
    # if successful, returns a token response
    # if unsuccessful, returns None
    @classmethod
    def authenticate(cls, db, username: str, password: str) -> Optional[Dict[str, Any]]:
        # finding the user in the database by email or username
        user = db.query(cls).filter(
            (cls.username == username) | (cls.email == username)
        ).first() # returns first matching user

        if not user or not user.verify_password(password):
            return None # pragma: no cover

        user.last_login = datetime.utcnow() # updates user's last login
        db.commit() # permanently saves last_login to the database

        # Create token response using Pydantic models
        user_response = UserResponse.model_validate(user)
        # create access token
        token_response = Token(
            access_token=cls.create_access_token({"sub": str(user.id)}),
            token_type="bearer",
            user=user_response
        )

        return token_response.model_dump() # converts token object into regular python dictionary (info FE will receive after successful login)