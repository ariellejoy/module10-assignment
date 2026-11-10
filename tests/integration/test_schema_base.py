import pytest
from uuid import uuid4
from datetime import datetime, timezone
from pydantic import ValidationError
from app.schemas.base import UserBase, PasswordMixin, UserCreate, UserLogin, UserRead

from app.models.user import User

def test_user_base_valid():
    """Test UserBase with valid data."""
    data = {
        "first_name": "John",
        "last_name": "Doe",
        "email": "john.doe@example.com",
        "username": "johndoe",
    }
    user = UserBase(**data)
    assert user.first_name == "John"
    assert user.email == "john.doe@example.com"


def test_user_base_invalid_email():
    """Test UserBase with invalid email."""
    data = {
        "first_name": "John",
        "last_name": "Doe",
        "email": "invalid-email",
        "username": "johndoe",
    }
    with pytest.raises(ValidationError):
        UserBase(**data)


def test_password_mixin_valid():
    """Test PasswordMixin with valid password."""
    data = {"password": "SecurePass123"}
    password_mixin = PasswordMixin(**data)
    assert password_mixin.password == "SecurePass123"


def test_password_mixin_invalid_short_password():
    """Test PasswordMixin with short password."""
    data = {"password": "short"}
    with pytest.raises(ValidationError):
        PasswordMixin(**data)


def test_password_mixin_no_uppercase():
    """Test PasswordMixin with no uppercase letter."""
    data = {"password": "lowercase1"}
    with pytest.raises(ValidationError, match="Password must contain at least one uppercase letter"):
        PasswordMixin(**data)


def test_password_mixin_no_lowercase():
    """Test PasswordMixin with no lowercase letter."""
    data = {"password": "UPPERCASE1"}
    with pytest.raises(ValidationError, match="Password must contain at least one lowercase letter"):
        PasswordMixin(**data)


def test_password_mixin_no_digit():
    """Test PasswordMixin with no digit."""
    data = {"password": "NoDigitsHere"}
    with pytest.raises(ValidationError, match="Password must contain at least one digit"):
        PasswordMixin(**data)


def test_user_create_valid():
    """Test UserCreate with valid data."""
    data = {
        "first_name": "John",
        "last_name": "Doe",
        "email": "john.doe@example.com",
        "username": "johndoe",
        "password": "SecurePass123",
    }
    user_create = UserCreate(**data)
    assert user_create.username == "johndoe"
    assert user_create.password == "SecurePass123"


def test_user_create_invalid_password():
    """Test UserCreate with invalid password."""
    data = {
        "first_name": "John",
        "last_name": "Doe",
        "email": "john.doe@example.com",
        "username": "johndoe",
        "password": "short",
    }
    with pytest.raises(ValidationError):
        UserCreate(**data)

def test_user_read_valid():
    """Test UserRead with valid data."""
    user = User(
        id=uuid4(),
        first_name="John",
        last_name="Doe",
        email="john.doe@example.com",
        username="johndoe",
        password="hashed_password",
        is_active=True,
        is_verified=False,
        last_login=None,
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )
    user_read = UserRead.model_validate(user)
    assert user_read.username == "johndoe"
    assert user_read.first_name == "John"
    assert user_read.last_name == "Doe"
    assert user_read.email == "john.doe@example.com"
    assert user_read.id == user.id
    assert user_read.created_at == user.created_at
    assert user_read.updated_at == user.updated_at
    assert user_read.is_active == user.is_active
    assert user_read.is_verified == user.is_verified
    assert user_read.last_login == user.last_login
    
def test_user_read_invalid_email():
    """Test UserRead with invalid email."""
    data = {
        "id": uuid4(),
        "first_name": "John",
        "last_name": "Doe",
        "email": "invalid-email",
        "username": "johndoe",
        "password": "hashed_password",
        "is_active": True,
        "is_verified": False,
        "last_login": None,
        "created_at": datetime.now(),
        "updated_at": datetime.now(),
    }
    with pytest.raises(ValidationError):
        UserRead(**data)

def test_user_read_missing_fields():
    """Test UserRead with missing fields."""
    data = {
        "first_name": "John",
        "last_name": "Doe",
        "email": "john.doe@example.com",
        "username": "johndoe",       
    }
    with pytest.raises(ValidationError):
        UserRead(**data)

def test_user_read_invalid_id():
    """Test UserRead with invalid id."""
    data = {
        "id": "invalid-id",
        "first_name": "John",
        "last_name": "Doe",
        "email": "john.doe@example.com",
        "username": "johndoe",
        "password": "hashed_password",
        "is_active": True,
        "is_verified": False,
        "last_login": None,
        "created_at": datetime.now(),
        "updated_at": datetime.now(),
    }
    with pytest.raises(ValidationError):
        UserRead(**data)

def test_user_read_invalid_username():
    """Test UserRead with short username."""
    data = {
        "id": uuid4(),
        "first_name": "John",
        "last_name": "Doe",
        "email": "john.doe@example.com",
        "username": "jd",
        "password": "hashed_password",
        "is_active": True,
        "is_verified": False,
        "last_login": None,
        "created_at": datetime.now(),
        "updated_at": datetime.now(),
    }
    with pytest.raises(ValidationError):
        UserRead(**data)

def test_user_read_missing_last_login():
    """Test last_login defaults to None when omitted."""
    now = datetime.now(timezone.utc)
    data = {
        "id": uuid4(),
        "first_name": "John",
        "last_name": "Doe",
        "email": "john.doe@example.com",
        "username": "johndoe",
        "is_active": True,
        "is_verified": False,
        "created_at": now,
        "updated_at": now
    }
    user = UserRead(**data)
    assert user.last_login is None

def test_user_login_valid():
    """Test UserLogin with valid data."""
    data = {"username": "johndoe", "password": "SecurePass123"}
    user_login = UserLogin(**data)
    assert user_login.username == "johndoe"

def test_user_login_invalid_username():
    """Test UserLogin with short username."""
    data = {"username": "jd", "password": "SecurePass123"}
    with pytest.raises(ValidationError):
        UserLogin(**data)


def test_user_login_invalid_password():
    """Test UserLogin with invalid password."""
    data = {"username": "johndoe", "password": "short"}
    with pytest.raises(ValidationError):
        UserLogin(**data)

def test_user_read_from_sqlalchemy_model():
    """Test UserRead can validate a SQLAlchemy User object."""
    now = datetime.now(timezone.utc)
    user = User(
        id=uuid4(),
        first_name="Jane",
        last_name="Smith",
        email="jane@example.com",
        username="janesmith",
        password="hashed_password",
        is_active=True,
        is_verified=True,
        last_login=None,
        created_at=now,
        updated_at=now
    )
    user_read = UserRead.model_validate(user)
    assert user_read.id == user.id
    assert user_read.first_name == user.first_name
    assert user_read.email == user.email
    assert user_read.username == user.username
    assert user_read.is_verified is True
