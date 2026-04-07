# cardapp/apis/auth_api.py
import re
from flask import Blueprint, request, render_template, redirect, abort, jsonify
from flask_login import login_user, logout_user, current_user, login_required
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
        return render_template('register.html', err_msg=err_msg, data=data), 400

    try:
        add_user(name=data.get('name'), username=data.get('username'), password=password,
                 avatar=request.files.get('avatar'), email=data.get('email'))
        return redirect('/login')
    except ValueError as ve:
        return render_template('register.html', err_msg=str(ve), data=data), 400
    except Conflict as c:
        return render_template('register.html', err_msg=c.description, data=data), 409
    except IntegrityError:
        return render_template('register.html', err_msg='Thông tin đăng ký đã tồn tại hoặc không hợp lệ!', data=data), 409
    except Exception as ex:
        return render_template('register.html', err_msg=str(ex), data=data), 500

@auth_bp.route('/logout')
@swag_from('../docs/logout.yml')
def logout_process():
    if current_user.is_authenticated:
        logout_user()
        return redirect('/login')
    abort(401)

@auth_bp.route('/profile', methods=['GET'])
@login_required
def profile_get():
    """
    Hiển thị trang thông tin cá nhân
    ---
    tags:
        - "User Profile"
    responses:
      200:
        description: Trả về HTML trang profile
    """
    return render_template('profile.html')

@auth_bp.route('/profile', methods=['PUT'])
@login_required
@swag_from('../docs/profile.yml')
def profile_view():
    name = request.form.get('name')
    email = request.form.get('email')
    avatar_file = request.files.get('avatar')

    try:
        dao.update_profile(current_user.id, name, email, avatar_file)
        return jsonify({
            "status": "success",
            "msg": "Cập nhật thông tin thành công!",
            "avatar_url": current_user.avatar
        }), 200

    except ValueError as ve:
        return jsonify({"status": "danger", "msg": str(ve)}), 400

    except (Conflict, IntegrityError) as ce:
        msg = ce.description if isinstance(ce, Conflict) else "Email đã tồn tại!"
        return jsonify({"status": "danger", "msg": msg}), 409

    except Exception as ex:
        return jsonify({"status": "danger", "msg": "Lỗi hệ thống: " + str(ex)}), 500