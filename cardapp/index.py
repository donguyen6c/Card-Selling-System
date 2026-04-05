import re

from flask import Flask, jsonify, request, redirect, render_template
from flasgger import Swagger
from flask_login import login_user, logout_user, current_user

from cardapp import dao, login, app
from cardapp.dao import add_user

swagger_config = {
    "headers": [],
    "specs": [
        {
            "endpoint": 'apispec_1',
            "route": '/apispec_1.json',
            "rule_filter": lambda rule: True,
            "model_filter": lambda tag: True,
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/docs"
}

template = {
    "swagger": "2.0",
    "info": {
        "title": "CaoThe Website",
        "description": "Hệ thống cung cấp thẻ Viettel, Mobi, Vina, Garena, Zing...",
        "contact": {
            "responsibleOrganization": "Selling Card Team",
            "email": "donguyen6c@gmail.com",
        },
        "version": "1.0.1"
    },
    "basePath": "/",
    "schemes": ["http", "https"]
}

swagger = Swagger(app, config=swagger_config, template=template)
# ==========================================
#CÁC ROUTE TRONG INDEX.PY
# ==========================================
@app.route('/login', methods=['POST'])
def login_process():
    """
    Đăng nhập
    ---
    consumes:
      - application/x-www-form-urlencoded
    produces:
      - application/json
    parameters:
      - name: username
        in: formData
        type: string
        required: true
      - name: password
        in: formData
        type: string
        required: true
    responses:
      200:
        description: Đăng nhập thành công
      401:
        description: Sai tên đăng nhập hoặc mật khẩu
    """
    username = request.form.get('username')
    password = request.form.get('password')

    user = dao.auth_user(username=username, password=password)
    if user:
        login_user(user=user)
        return jsonify({
            "status": "success",
            "message": "Đăng nhập thành công!",
            "data": {
                "user_id": user.id,
                "username": user.username
            }
        }), 200
    else:
        return jsonify({
            "status": "error",
            "message": "Tên đăng nhập hoặc mật khẩu không chính xác!"
        }), 401


@app.route('/register', methods=['POST'])
def register_process():
    """
    Đăng ký
    ---
    consumes:
      - multipart/form-data
    produces:
      - application/json
    parameters:
      - name: name
        in: formData
        type: string
        required: true
      - name: username
        in: formData
        type: string
        required: true
      - name: password
        in: formData
        type: string
        required: true
      - name: confirm
        in: formData
        type: string
        required: true
      - name: email
        in: formData
        type: string
        required: true
      - name: avatar
        in: formData
        type: file
        required: false
    responses:
      201:
        description: Đăng ký thành công
      400:
        description: Dữ liệu đầu vào không hợp lệ
      500:
        description: Lỗi hệ thống khi lưu vào cơ sở dữ liệu
    """
    data = request.form

    password = data.get('password')
    confirm = data.get('confirm')

    if password != confirm:
        return jsonify({
            "status": "error",
            "message": "Mật khẩu không khớp!"
        }), 400

    email = data.get('email')
    email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'

    if not email or not re.match(email_regex, email):
        return jsonify({
            "status": "error",
            "message": "Email không đúng định dạng!"
        }), 400

    try:
        add_user(
            name=data.get('name'),
            username=data.get('username'),
            password=password,
            avatar=request.files.get('avatar'),
            email=email
        )
        return jsonify({
            "status": "success",
            "message": "Đăng ký tài khoản thành công!"
        }), 201
    except Exception as ex:
        return jsonify({
            "status": "error",
            "message": f"Lỗi hệ thống: {str(ex)}"
        }), 500


@app.route('/logout')
def logout_process():
    """
    Đăng xuất
    ---
    produces:
      - application/json
    responses:
      200:
        description: Đăng xuất thành công
    """
    logout_user()
    return jsonify({
        "status": "success",
        "message": "Đã đăng xuất khỏi hệ thống!"
    }), 200


@login.user_loader
def load_user(id):
    return dao.get_user_by_id(id)

if __name__ == '__main__':
    app.run(debug=True)