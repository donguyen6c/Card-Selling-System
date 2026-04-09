# cardapp/apis/history_api.py
import re

from flasgger import swag_from
from flask import Blueprint, render_template, redirect
from flask_login import  current_user, login_required

from cardapp import dao

history_bp = Blueprint('history', __name__)

@history_bp.route('/users/current-user/transactions', methods=['GET'])
@login_required
@swag_from('../docs/history.yml')
def history_view():
    if not current_user.is_authenticated:
        return redirect('/login?next=/history')

    receipts = dao.get_receipts_by_user(current_user.id)

    return render_template('history.html', receipts=receipts)

@history_bp.route('/users/current-user/transactions')
@login_required
def register_view():
    return render_template('history.html')