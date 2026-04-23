import re

from sqlalchemy.exc import IntegrityError
from cardapp.models import User
import hashlib
import cloudinary.uploader
from cardapp import db
from sqlalchemy.exc import IntegrityError
from werkzeug.exceptions import Conflict
from cardapp.utils import validate_email_domain

def get_user_by_id(id):
    return User.query.get(id)

def auth_user(username, password):
    password = str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())
    return User.query.filter(User.username == username,
                             User.password == password).first()

def add_user(name, username, password, avatar, email):
    if not name:
        raise ValueError("Thiếu trường tên")

    email = validate_email_domain(email)

    if len(username) < 5:
        raise ValueError("Username phải ít nhất có 5 kí tự")

    if len(password) < 8:
        raise ValueError("Mật khẩu phải có ít nhất 8 kí tự")

    if not re.search(r'[0-9]', password):
        raise ValueError("Mật khẩu phải chứa ít nhất một chữ số")
    if not re.search(r'[a-z]', password):
        raise ValueError("Mật khẩu phải chứa ít nhất một chữ thường")
    if not re.search(r'[A-Z]', password):
        raise ValueError("Mật khẩu phải chứa ít nhất một chữ hoa")

    existing_user = User.query.filter_by(username=username.strip()).first()
    if existing_user:
        raise Conflict("Username này đã được sử dụng!")

    existing_email = User.query.filter_by(email=email.strip()).first()
    if existing_email:
        raise Conflict("Email này đã được đăng ký!")

    password = str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())
    u = User(name=name.strip(), username=username.strip(), password=password, email=email)

    if avatar:
        res = cloudinary.uploader.upload(avatar)
        u.avatar = res.get("secure_url")

    db.session.add(u)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        raise


def update_profile(user_id, name, password, email, avatar_file=None):
    if not name:
        raise ValueError("Tên không được để trống!")

    if len(password) < 8:
        raise ValueError("Mật khẩu phải có ít nhất 8 kí tự")

    if not re.search(r'[0-9]', password):
        raise ValueError("Mật khẩu phải chứa ít nhất một chữ số")
    if not re.search(r'[a-z]', password):
        raise ValueError("Mật khẩu phải chứa ít nhất một chữ thường")
    if not re.search(r'[A-Z]', password):
        raise ValueError("Mật khẩu phải chứa ít nhất một chữ hoa")

    email = validate_email_domain(email)

    user = User.query.get(user_id)
    if not user:
        raise ValueError("Tài khoản không tồn tại!")

    existing_email = User.query.filter(User.email == email, User.id != user_id).first()
    if existing_email:
        raise Conflict("Email này đã được sử dụng bởi một tài khoản khác!")

    user.name = name
    user.email = email
    user.password = str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())

    if avatar_file:
        try:
            res = cloudinary.uploader.upload(avatar_file)
            user.avatar = res.get('secure_url')
        except Exception as e:
            raise Exception(f"Lỗi khi tải ảnh lên Cloudinary: {str(e)}")

    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        raise

    return True