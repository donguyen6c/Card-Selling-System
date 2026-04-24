from cardapp.test.base import test_app, test_session, mock_cloudinary
import pytest
from cardapp.models import User
from cardapp.dao import add_user, update_profile
from sqlalchemy.exc import IntegrityError
import re
from cardapp.dao.user_dao import Conflict
import cloudinary
import hashlib


def test_update_profile_success(test_session, mock_cloudinary):

    original_username = "username1"
    add_user(name="abcde", username=original_username, password="aBc@1234", email="test@gmail.com", avatar=None)
    u = User.query.filter_by(username=original_username).first()

    result = update_profile(
        user_id=u.id,
        name="updated name",
        password="NewPassword123@",
        email="updated@gmail.com",
        avatar_file="new_avatar.png"
    )

    assert result is True
    assert u.name == "updated name"
    assert u.email == "updated@gmail.com"
    assert u.username == original_username
    assert u.avatar == "https://fake-image.com"
    expected_hash = hashlib.md5("NewPassword123@".encode('utf-8')).hexdigest()
    assert u.password == expected_hash


@pytest.mark.parametrize("name, password, email, msg", [
    ("", "aBc@1234", "test@gmail.com", "Tên không được để trống!"),
    ("abc", "123", "test@gmail.com", "Mật khẩu phải có ít nhất 8 kí tự"),
    ("abc", "password123", "test@gmail.com", "Mật khẩu phải chứa ít nhất một chữ hoa"),
    ("abc", "aBc@1234", "test.com", "Email không đúng định dạng!"),
])
def test_update_profile_input_validation(test_session, name, password, email, msg):

    add_user(name="basename", username="baseuser", password="aBc@1234", email="base@gmail.com", avatar=None)
    u = User.query.filter_by(username="baseuser").first()

    with pytest.raises(ValueError, match=re.escape(msg)):
        update_profile(user_id=u.id, name=name, password=password, email=email)


def test_update_profile_user_not_found(test_session):
    with pytest.raises(ValueError, match="Tài khoản không tồn tại!"):
        update_profile(user_id=9999, name="Name", password="aBc@1234", email="test@gmail.com")


def test_update_profile_email_conflict(test_session):
    add_user(name="User 1", username="username1", password="Password123@", email="email1@gmail.com", avatar=None)
    add_user(name="User 2", username="username2", password="Password123@", email="email2@gmail.com", avatar=None)

    u1 = User.query.filter_by(username="username1").first()

    with pytest.raises(Conflict, match="Email này đã được sử dụng bởi một tài khoản khác!"):
        update_profile(user_id=u1.id, name="User 1 New", email="email2@gmail.com")



def test_update_profile_cloudinary_error(test_session, monkeypatch):
    add_user(name="User1", username="username1", password="Password123@", email="user@gmail.com", avatar=None)
    u = User.query.filter_by(username="username1").first()

    def mock_upload_fail(*args, **kwargs):
        raise Exception("Cloudinary Down")

    monkeypatch.setattr(cloudinary.uploader, "upload", mock_upload_fail)

    with pytest.raises(Exception, match="Lỗi khi tải ảnh lên Cloudinary: Cloudinary Down"):
        update_profile(user_id=u.id, name="Name", email="user@gmail.com", avatar_file="image.png")


