import re

from sqlalchemy.exc import IntegrityError
from cardapp.models import User
import hashlib
import cloudinary.uploader
from cardapp import db

def get_user_by_id(id):
    return User.query.get(id)

def auth_user(username, password):
    password = str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())
    return User.query.filter(User.username == username,
                             User.password == password).first()

def add_user(name, username, password, avatar, email):
    if len(username) < 5:
        raise ValueError("username phai it nhat co 5 ki tu")
    if len(password) < 8:
        raise ValueError("mat khau phai it nhat co 8 ki tu")
    if not re.search(r'[0-9]', password):
        raise ValueError("Mật khẩu phải chứa ít nhất một chữ số")
    if not re.search(r'[a-z]', password):
        raise ValueError("Mật khẩu phải chứa ít nhất một chữ thường")
    if not re.search(r'[A-Z]', password):
        raise ValueError("Mật khẩu phải chứa ít nhất một chữ hoa")
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
        raise Exception('Username đã tồn tại!')