# cardapp/apis/history_api.py
import re

from flasgger import swag_from
from flask import Blueprint, render_template, redirect, request
from flask_login import  current_user, login_required

from cardapp import dao

history_bp = Blueprint('history', __name__)


@history_bp.route('/users/current-user/transactions', methods=['GET'])
@login_required
@swag_from('../docs/history.yml')
def history_view():
    if not current_user.is_authenticated:
        return redirect('/login?next=/history')

    from_date = request.args.get('from_date')
    to_date = request.args.get('to_date')
    page = request.args.get('page', 1, type=int)

    receipts = dao.get_receipts_by_user(
        user_id=current_user.id,
        from_date=from_date,
        to_date=to_date,
        page=page
    )

    return render_template('history.html', receipts=receipts, from_date=from_date, to_date=to_date)
