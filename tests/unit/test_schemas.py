import pytest
import uuid

from datetime import datetime
from pydantic import ValidationError

from app.schemas.base import UserCreate, UserRead, UserLogin
from app.schemas.user import UserResponse, Token
from app.models.user import User

# testing user creation
def test_valid_user_create():
    user = UserCreate(
        first_name="John",
        last_name="Smith",
        email="john@example.com",
        username="johnsmith",
        password="SecurePassword123"
    )
    assert user.email == "john@example.com"
    assert user.username == "johnsmith"
    assert user.first_name == "John"
    assert user.last_name == "Smith"

def test_invalid_email_rejected():
    with pytest.raises(ValidationError):
        UserCreate(
            first_name="John",
            last_name="Smith",
            email="invalid-email",
            username="johnsmith",
            password="SecurePassword123"
        )
    
def test_invalid_email_rejected():
    with pytest.raises(ValidationError):
        UserCreate(
            first_name="John",
            last_name="Smith",
            email="invalid-email",
            username="johnsmith",
            password="SecurePassword123"
        )

def test_missing_required_fields():
    with pytest.raises(ValidationError):
        UserCreate(
            email="john@example.com"
        )

def test_empty_password_rejected():
    with pytest.raises(ValidationError):
        UserCreate(
            first_name="John",
            last_name="Smith",
            email="john@example.com",
            username="johnsmith",
            password=""
        )

# testing user response validation
def test_valid_user_response():
    user = UserResponse(
        id=uuid.uuid4(),
        username="johnsmith",
        email="john@example.com",
        first_name="John",
        last_name="Smith",
        is_active=True,
        is_verified=False,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    assert user.username == "johnsmith"
    assert user.email == "john@example.com"
    assert user.is_active is True

def test_user_response_invalid_email():
    with pytest.raises(ValidationError):
        UserResponse(
            id=uuid.uuid4(),
            username="johnsmith",
            email="invalid-email",
            first_name="John",
            last_name="Smith",
            is_active=True,
            is_verified=False,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

def test_user_response_missing_username():
    with pytest.raises(ValidationError):
        UserResponse(
            id=uuid.uuid4(),
            email="john@example.com",
            first_name="John",
            last_name="Smith",
            is_active=True,
            is_verified=False,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

# testing user login 
def test_valid_user_login():
    login = UserLogin(
        username="johnsmith",
        password="SecurePassword123"
    )
    assert login.username == "johnsmith"

def test_login_missing_password():
    with pytest.raises(ValidationError):
        UserLogin(username="johnsmith")

def test_login_missing_username():
    with pytest.raises(ValidationError):
        UserLogin(password="SecurePassword123")

def test_login_empty_username():
    with pytest.raises(ValidationError):
        UserLogin(
            username="",
            password="SecurePassword123"
        )

# testing token validation
def test_valid_token_response():
    now = datetime.utcnow()
    user = UserResponse(
        id=uuid.uuid4(),
        username="johnsmith",
        email="john@example.com",
        first_name="John",
        last_name="Smith",
        is_active=True,
        is_verified=False,
        created_at=now,
        updated_at=now
    )
    token = Token(
        access_token="sample_access_token",
        token_type="bearer",
        user=user
    )
    assert token.token_type == "bearer"
    assert token.user.username == "johnsmith"

def test_token_missing_access_token():
    with pytest.raises(ValidationError):
        Token(
            token_type="bearer",
            user=None
        )

# testing UserRead
def test_valid_user_read():
    now = datetime.utcnow()
    user = UserRead(
        id=uuid.uuid4(),
        first_name="John",
        last_name="Smith",
        email="john@example.com",
        username="johnsmith",
        is_active=True,
        is_verified=False,
        last_login=now,
        created_at=now,
        updated_at=now
    )
    assert user.first_name == "John"
    assert user.last_name == "Smith"
    assert user.email == "john@example.com"
    assert user.username == "johnsmith"
    assert user.is_active is True
    assert user.is_verified is False
    assert user.last_login == now
    assert user.created_at == now
    assert user.updated_at == now

def test_user_read_invalid_email():
    with pytest.raises(ValidationError):
        UserRead(
            id=uuid.uuid4(),
            first_name="John",
            last_name="Smith",
            email="invalid-email",
            username="johnsmith",
            is_active=True,
            is_verified=False,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

def test_user_read_missing_email():
    with pytest.raises(ValidationError):
        UserRead(
            id=uuid.uuid4(),
            first_name="John",
            last_name="Smith",
            username="johnsmith",
            is_active=True,
            is_verified=False,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

def test_user_read_invalid_uuid():
    with pytest.raises(ValidationError):
        UserRead(
            id="not-a-valid-uuid",
            first_name="John",
            last_name="Smith",
            email="john@example.com",
            username="johnsmith",
            is_active=True,
            is_verified=False,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

def test_user_read_without_last_login():
    user = UserRead(
        id=uuid.uuid4(),
        first_name="John",
        last_name="Smith",
        email="john@example.com",
        username="johnsmith",
        is_active=True,
        is_verified=False,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    assert user.last_login is None

def test_user_read_invalid_created_at():
    with pytest.raises(ValidationError):
        UserRead(
            id=uuid.uuid4(),
            first_name="John",
            last_name="Smith",
            email="john@example.com",
            username="johnsmith",
            is_active=True,
            is_verified=False,
            created_at="not-a-date",
            updated_at=datetime.utcnow()
        )

def test_user_read_from_orm():
    now = datetime.utcnow()
    user = User(
        id=uuid.uuid4(),
        first_name="John",
        last_name="Smith",
        email="john@example.com",
        username="johnsmith",
        password_hash="hashed_password",
        is_active=True,
        is_verified=False,
        last_login=None,
        created_at=now,
        updated_at=now
    )
    result = UserRead.model_validate(user)
    assert result.username == "johnsmith"
    assert result.email == "john@example.com"
    assert result.first_name == "John"
    assert result.last_login is None
    assert result.created_at == now
    assert result.updated_at == now

