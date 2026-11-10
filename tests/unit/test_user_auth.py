# tests for user authentication

from unittest.mock import MagicMock, patch
from datetime import datetime
import uuid

import pytest

from app.models.user import User

# test fixtures that will be used by the tests below
@pytest.fixture
def mock_db():
    return MagicMock()

@pytest.fixture
def test_user():

    user = User(
        first_name="John",
        last_name="Smith",
        email="john@example.com",
        username="johnsmith",
        password_hash=User.hash_password("SecurePassword123"),
        is_active=True,
        is_verified=True,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    user.id = uuid.uuid4()
    return user

# test for successful authentication w/ username
def test_authenticate_successful_login(mock_db, test_user):
    mock_db.query.return_value.filter.return_value.first.return_value = test_user
    result = User.authenticate(
        mock_db,
        "johnsmith",
        "SecurePassword123"
    )
    assert result is not None
    assert "access_token" in result
    assert result["token_type"] == "bearer"
    assert "user" in result
    mock_db.commit.assert_called_once()

# test for login with email
def test_authenticate_using_email(mock_db, test_user):
    mock_db.query.return_value.filter.return_value.first.return_value = test_user
    result = User.authenticate(
        mock_db,
        "john@example.com",
        "SecurePassword123"
    )
    assert result is not None
    assert result["token_type"] == "bearer"

# test for incorrect passwords
def test_authenticate_wrong_password(mock_db, test_user):
    mock_db.query.return_value.filter.return_value.first.return_value = test_user
    result = User.authenticate(
        mock_db,
        "johnsmith",
        "WrongPassword123"
    )
    assert result is None
    mock_db.commit.assert_not_called()

# test for last_login updates

def test_authenticate_updates_last_login(mock_db, test_user):
    mock_db.query.return_value.filter.return_value.first.return_value = test_user
    assert test_user.last_login is None
    User.authenticate(
        mock_db,
        "johnsmith",
        "SecurePassword123"
    )
    assert test_user.last_login is not None
    assert isinstance(test_user.last_login, datetime)

# test that access token is generated
def test_authenticate_generates_access_token(mock_db, test_user):
    mock_db.query.return_value.filter.return_value.first.return_value = test_user
    with patch.object(
        User,
        "create_access_token",
        return_value="fake_access_token"
    ) as mock_token:
        result = User.authenticate(
            mock_db,
            "johnsmith",
            "SecurePassword123"
        )
    assert result["access_token"] == "fake_access_token"
    mock_token.assert_called_once()

# testing returned user info
def test_authenticate_returns_correct_user_details(mock_db, test_user):
    mock_db.query.return_value.filter.return_value.first.return_value = test_user
    result = User.authenticate(
        mock_db,
        "johnsmith",
        "SecurePassword123"
    )
    assert result["user"]["email"] == "john@example.com"
    assert result["user"]["username"] == "johnsmith"
    assert result["user"]["first_name"] == "John"
    assert result["user"]["last_name"] == "Smith"