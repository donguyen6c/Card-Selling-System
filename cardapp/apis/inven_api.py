# cardapp/apis/iven_api.py
import re
from flask import Blueprint, request, render_template, redirect, abort, jsonify
from flask_login import login_user, logout_user, current_user, login_required
from flasgger import swag_from

from cardapp import dao
from cardapp.dao import add_user

inven_bp = Blueprint('inventory', __name__)

@inven_bp.route('/users/current-user/inventory', methods=['GET'])
@login_required
@swag_from('../docs/inventory.yml')
def inventory_view():
    if not current_user.is_authenticated:
        return redirect('/login?next=/inventory')

    cards = dao.get_cards_by_user(current_user.id)

    return render_template('inventory.html', cards=cards)