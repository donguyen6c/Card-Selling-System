import re
import traceback

from flask import Blueprint, request, render_template, redirect, abort, jsonify, session
from flask_login import login_user, logout_user, current_user, login_required
from flasgger import swag_from

from cardapp import dao, utils
from cardapp.observers import PaymentSubject, EmailNotificationObserver

pay_api = Blueprint('pay', __name__)

@pay_api.route('/pay', methods=['GET'])
@login_required
def checkout_view():
    if not current_user.is_authenticated:
        return redirect('/login?next=/checkout')

    cart = session.get('cart', {})

    if not cart:
        return redirect('/cart')

    session.pop('discount_code', None)
    session.pop('discount_amount', None)

    cart_stats = utils.stats_cart(cart)
    return render_template('checkout.html', cart_stats=cart_stats)

@pay_api.route('/pay/discount', methods=['POST'])
@login_required
@swag_from('../docs/apply_discount.yml')
def apply_discount_api():
    if not current_user.is_authenticated:
        return jsonify({"status": "error", "message": "Bạn chưa đăng nhập!"}), 401

    code = request.json.get('code')
    cart = session.get('cart', {})

    res = dao.check_discount(code, cart)

    if res['success']:
        session['discount_code'] = code
        session['discount_amount'] = res['discount_amount']
        return jsonify({
            "status": "success",
            "message": res['message'],
            "discount_amount": res['discount_amount']
        })
    else:
        session.pop('discount_code', None)
        session.pop('discount_amount', None)
        return jsonify({
            "status": "error",
            "message": res['message'],
            "discount_amount": 0
        }), 400

payment_subject = PaymentSubject()
payment_subject.attach(EmailNotificationObserver())


@pay_api.route('/pay', methods=['POST'])
@login_required
@swag_from('../docs/pay.yml')
def pay_process():
    if not current_user.is_authenticated:
        return jsonify({"status": "error", "message": "Bạn chưa đăng nhập!"}), 401

    cart = session.get('cart')
    if not cart:
        return jsonify({"status": "error", "message": "Giỏ hàng của bạn đang trống!"}), 400

    data = request.json
    payment_method = data.get('payment_method', 'momo')

    stats = utils.stats_cart(cart)
    total_amount = stats.get('total_amount', 0)
    discount_amount = session.get('discount_amount', 0)
    discount_code = session.get('discount_code')

    final_amount = total_amount - discount_amount
    if final_amount < 0: final_amount = 0

    try:
        dao.add_receipt(
            user_id=current_user.id,
            cart=cart,
            discount_code=discount_code
        )

        payment_subject.notify(
            user_id=current_user.id,
            cart=cart,
            final_amount=final_amount,
            payment_method=payment_method
        )

        session.pop('cart', None)
        session.pop('discount_code', None)
        session.pop('discount_amount', None)

        return jsonify({"status": "success", "message": "Thanh toán thành công! Mã giao dịch đã được gửi vào Email."})

    except Exception as ex:
        traceback.print_exc()
        return jsonify({"status": "error", "message": str(ex)}), 500