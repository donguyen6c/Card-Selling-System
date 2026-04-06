import re

from sqlalchemy.exc import IntegrityError
from cardapp.models import User
import hashlib
import cloudinary.uploader
from cardapp import db
from sqlalchemy.exc import IntegrityError
from werkzeug.exceptions import Conflict

def get_user_by_id(id):
    return User.query.get(id)

def auth_user(username, password):
    password = str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())
    return User.query.filter(User.username == username,
                             User.password == password).first()

def add_user(name, username, password, avatar, email):
    if not name:
        raise ValueError("Thiếu trường tên")
    if not email:
        raise ValueError("Thiếu trường email")

    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        raise ValueError("Email không hợp lệ")

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
    except IntegrityError as dup:
        db.session.rollback()
        raise dup