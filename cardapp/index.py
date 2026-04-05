import re

from flask import Flask, jsonify, request, redirect, render_template
from flasgger import Swagger, swag_from
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
# CÁC ROUTE TRONG INDEX.PY
# ==========================================
@app.route('/login')
def login_view():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
@swag_from('docs/login.yml')
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
        return render_template('login.html', err_msg=err_msg)


@app.route('/register')
def register_view():
    return render_template('register.html')


@app.route('/register', methods=['POST'])
@swag_from('docs/register.yml')
def register_process():
    data = request.form
    password = data.get('password')
    confirm = data.get('confirm')
    if password != confirm:
        err_msg = 'Mật khẩu không khớp!'
        return render_template('register.html', err_msg=err_msg)

    email = data.get('email')
    email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'

    if not email or not re.match(email_regex, email):
        err_msg = 'Email không đúng định dạng!'
        return render_template('register.html', err_msg=err_msg)
    try:
        add_user(name=data.get('name'), username=data.get('username'), password=password,
                 avatar=request.files.get('avatar'), email=data.get('email'))
        return redirect('/login')
    except Exception as ex:
        return render_template('register.html', err_msg=str(ex))


@app.route('/logout')
def logout_process():
    logout_user()
    return redirect('/login')

@login.user_loader
def load_user(id):
    return dao.get_user_by_id(id)


if __name__ == '__main__':
    app.run(debug=True)
