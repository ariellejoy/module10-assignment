from datetime import timedelta
from jose import jwt
import uuid
from unittest.mock import MagicMock
import pytest

from app.models.user import User, SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES

# tests for user modeling
def test_user_has_correct_table_name():
    assert User.__tablename__ == "users"

def test_user_id_is_generated():
    user = User()
    user.id = uuid.uuid4()
    assert isinstance(user.id, uuid.UUID)

def test_user_repr():
    user = User(
        first_name="John",
        last_name="Smith",
        email="john@example.com"
    )
    assert "John Smith" in repr(user)
    assert "john@example.com" in repr(user)

def test_user_default_fields():
    user = User(
        first_name="John",
        last_name="Smith",
        email="john@example.com",
        username="johnsmith",
        password_hash="hashed_password"
    )
    assert user.is_active is None or user.is_active is True
    assert user.is_verified is None or user.is_verified is False

# tests for password hashing functionality
def test_password_is_hashed():
    password = "SecurePassword123"
    hashed = User.hash_password(password)
    assert hashed != password
    assert isinstance(hashed, str)

def test_correct_password_is_verified():
    password = "SecurePassword123"
    user = User()
    user.password_hash = User.hash_password(password)
    assert user.verify_password(password) is True

def test_incorrect_password_is_rejected():
    user = User()
    user.password_hash = User.hash_password("SecurePassword123")
    assert user.verify_password("WrongPassword123") is False

def test_same_password_produces_different_hashes():
    password = "SecurePassword123"
    hash1 = User.hash_password(password)
    hash2 = User.hash_password(password)

    # bcrypt uses a random salt
    assert hash1 != hash2

def test_hashed_password_can_be_verified():
    password = "MyPassword123!"
    hashed = User.hash_password(password)
    user = User()
    user.password_hash = hashed
    assert user.verify_password(password)

# tests for token creation 
def test_access_token_is_created():
    token = User.create_access_token({"sub": "123"})
    assert isinstance(token, str)
    assert len(token) > 0

def test_access_token_contains_user_id():
    token = User.create_access_token({"sub": "123"})
    payload = jwt.decode(
        token,
        SECRET_KEY,
        algorithms=[ALGORITHM]
    )
    assert payload["sub"] == "123"

def test_access_token_contains_expiration():
    token = User.create_access_token({"sub": "123"})
    payload = jwt.decode(
        token,
        SECRET_KEY,
        algorithms=[ALGORITHM]
    )
    assert "exp" in payload

def test_custom_expiration_is_applied():
    token = User.create_access_token(
        {"sub": "123"},
        expires_delta=timedelta(minutes=10)
    )
    payload = jwt.decode(
        token,
        SECRET_KEY,
        algorithms=[ALGORITHM]
    )
    assert "exp" in payload

# tests for token verification
def test_valid_token_returns_user_uuid():
    user_id = str(uuid.uuid4())
    token = User.create_access_token({"sub": user_id})
    result = User.verify_token(token)
    assert result == uuid.UUID(user_id)

def test_invalid_token_returns_none():
    result = User.verify_token("invalid.token.value")
    assert result is None

def test_expired_token_returns_none():
    token = User.create_access_token(
        {"sub": str(uuid.uuid4())},
        expires_delta=timedelta(seconds=-1)
    )
    result = User.verify_token(token)
    assert result is None

def test_token_without_user_id_returns_none():
    token = User.create_access_token({"role": "user"})
    result = User.verify_token(token)
    assert result is None

def test_token_with_invalid_uuid_returns_none():
    token = User.create_access_token({"sub": "not-a-uuid"})
    result = User.verify_token(token)
    assert result is None

# tests for registration
def test_registration_rejects_short_password():
    db = MagicMock()
    user_data = {
        "first_name": "John",
        "last_name": "Smith",
        "email": "john@example.com",
        "username": "johnsmith",
        "password": "123"
    }
    with pytest.raises(ValueError):
        User.register(db, user_data)
    db.add.assert_not_called()


def test_registration_rejects_existing_user():
    db = MagicMock()
    db.query.return_value.filter.return_value.first.return_value = User()
    user_data = {
        "first_name": "John",
        "last_name": "Smith",
        "email": "john@example.com",
        "username": "johnsmith",
        "password": "SecurePassword123"
    }
    with pytest.raises(ValueError, match="already exists"):
        User.register(db, user_data)
    db.add.assert_not_called()