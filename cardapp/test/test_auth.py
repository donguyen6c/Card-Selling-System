from cardapp.test.base import test_app, test_session, mock_cloudinary
import pytest
from cardapp.models import User, UserRole
from cardapp.dao import auth_user, add_user
import hashlib

@pytest.fixture
def existing_user(test_session):
    u = add_user(name="auth_test", username="authtest123", password="Abc@1234", email="testauth@gmail.com", avatar=None)
    return u

def test_auth_success(test_app, test_session,existing_user):
    user = auth_user("authtest123", "Abc@1234")
    assert user is not None
    assert user.username == "authtest123"

def test_auth_wrong_password(test_app, test_session,existing_user):
    user = auth_user("authtest123", "abc@1234")
    assert user is None

def test_auth_empty_username(test_app, test_session, existing_user):
    user = auth_user("", "Abc@1234")
    assert user is None

def test_auth_empty_password(test_app, test_session, existing_user):
    user = auth_user("authtest123", "")
    assert user is None

def test_auth_empty_both(test_app, test_session, existing_user):
    user = auth_user("", "")
    assert user is None

def test_not_existing_user(test_app, test_session):
    user = auth_user("authtest123", "Abc@1234")
    assert user is None
