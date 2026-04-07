# cardapp/apis/history_api.py
import re
from flask import Blueprint, render_template, redirect
from flask_login import  current_user, login_required

from cardapp import dao

auth_bp = Blueprint('history', __name__)

@auth_bp.route('/history', methods=['GET'])
def history_view():
    if not current_user.is_authenticated:
        return redirect('/login?next=/history')

    receipts = dao.get_receipts_by_user(current_user.id)

    return render_template('history.html', receipts=receipts)