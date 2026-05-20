from cardapp.test.test_base import test_app, test_session, mock_cloudinary
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
        email="updated@gmail.com",
        avatar_file="new_avatar.png"
    )

    assert result is True
    assert u.name == "updated name"
    assert u.email == "updated@gmail.com"
    assert u.username == original_username
    assert u.avatar == "https://fake-image.com"



@pytest.mark.parametrize("name, email, msg", [
    ("","test@gmail.com", "Tên không được để trống!"),
    ("abc", "test.com", "Email không đúng định dạng!"),
])
def test_update_profile_input_validation(test_session, name, email, msg):
    add_user(name="abcde", username="baseuser", password="aBc@1234", email="test@gmail.com", avatar=None)
    u = User.query.filter_by(username="baseuser").first()

    with pytest.raises(ValueError, match=re.escape(msg)):
        update_profile(user_id=u.id, name=name, email=email)




def test_update_profile_existed_email(test_session):
    add_user(name="User 1", username="username1", email="email1@gmail.com", password="aBc@1234", avatar=None)
    add_user(name="User 2", username="username2", email="email2@gmail.com", password="aBc@1234", avatar=None)

    u1 = User.query.filter_by(username="username1").first()

    with pytest.raises(Conflict, match="Email này đã được sử dụng bởi một tài khoản khác!"):
        update_profile(user_id=u1.id, name="User 1 New", email="email2@gmail.com")



def test_update_profile_cloudinary_error(test_session, monkeypatch):
    add_user(name="abcde", username="username1", password="aBc@1234", email="test@gmail.com", avatar=None)
    u = User.query.filter_by(username="username1").first()

    def mock_upload_fail(*args, **kwargs):
        raise Exception("Cloudinary Down")

    monkeypatch.setattr(cloudinary.uploader, "upload", mock_upload_fail)

    with pytest.raises(Exception, match="Lỗi khi tải ảnh lên Cloudinary: Cloudinary Down"):
        update_profile(user_id=u.id, name="Name", email="user@gmail.com", avatar_file="image.png")
