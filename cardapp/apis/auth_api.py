# cardapp/apis/auth_api.py
import re
from flask import Blueprint, request, render_template, redirect
from flask_login import login_user, logout_user
from flasgger import swag_from
from sqlalchemy.exc import IntegrityError
from werkzeug.exceptions import Conflict

from cardapp import dao
from cardapp.dao import add_user

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login')
def login_view():
    return render_template('login.html')

@auth_bp.route('/login', methods=['POST'])
@swag_from('../docs/login.yml')
def login_process():
    username = request.form.get('username')
    password = request.form.get('password')

    user = dao.auth_user(username=username, password=password)
    if user:
        login_user(user=user)
        next_page = request.args.get('next')
        return redirect(next_page if next_page else '/')
    else:
        err_msg = "Tên đăng nhập hoặc mật khẩu không chính xác!"
        return render_template('login.html', err_msg=err_msg), 400

@auth_bp.route('/register')
def register_view():
    return render_template('register.html')

@auth_bp.route('/register', methods=['POST'])
@swag_from('../docs/register.yml')
def register_process():
    data = request.form
    password = data.get('password')
    confirm = data.get('confirm')
    if password != confirm:
        err_msg = 'Mật khẩu không khớp!'
        return render_template('register.html', err_msg=err_msg), 400

    email = data.get('email')
    email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'

    if not email or not re.match(email_regex, email):
        err_msg = 'Email không đúng định dạng!'
        return render_template('register.html', err_msg=err_msg), 400
    try:
        add_user(name=data.get('name'), username=data.get('username'), password=password,
                 avatar=request.files.get('avatar'), email=data.get('email'))
        return redirect('/login')
    except ValueError as ve:
        return render_template('register.html', err_msg=str(ve)), 400
    except Conflict as c:
        return render_template('register.html', err_msg=c.description), 409
    except IntegrityError:
        return render_template('register.html', err_msg='Thông tin đăng ký đã tồn tại hoặc không hợp lệ!'), 409
    except Exception as ex:
        return render_template('register.html', err_msg=str(ex)), 500

@auth_bp.route('/logout')
def logout_process():
    logout_user()
    return redirect('/login')