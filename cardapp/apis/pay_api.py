import re
import traceback
from datetime import datetime, timedelta

from flask import Blueprint, request, render_template, redirect, abort, jsonify, session, url_for
from flask_login import login_user, logout_user, current_user, login_required
from flasgger import swag_from

from cardapp import dao, utils, db
from cardapp.models import ReceiptStatus, Receipt
from cardapp.observers import PaymentSubject, EmailNotificationObserver

pay_api = Blueprint('pay', __name__)

@pay_api.route('/pay', methods=['GET'])
def checkout_view():
    if not current_user.is_authenticated:
        return redirect('/login?next=/')

    cart = session.get('cart', {})

    if not cart:
        return redirect('/')

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
    payment_method = data.get('payment_method', 'banking')
    discount_code = session.get('discount_code')

    try:
        order_id = dao.add_receipt(
            user_id=current_user.id,
            cart=cart,
            discount_code=discount_code
        )

        session['current_payment_order_id'] = order_id
        session['current_payment_method'] = payment_method

        session['pending_cart'] = cart

        session.pop('cart', None)
        session.pop('discount_code', None)
        session.pop('discount_amount', None)

        return jsonify({
            "status": "success",
            "message": "Tạo đơn hàng thành công! Đang chuyển hướng...",
            "redirect_url": url_for('pay.payment_page')
        })

    except Exception as ex:
        import traceback
        traceback.print_exc()
        return jsonify({"status": "error", "message": str(ex)}), 500


@pay_api.route('/payment', methods=['GET'])
def payment_page():
    if not current_user.is_authenticated:
        return redirect('/login?next=/')

    order_id = session.get('current_payment_order_id')
    if not order_id:
        return redirect('/')

    order = Receipt.query.get_or_404(order_id)

    if order.status == ReceiptStatus.PAID:
        session.pop('current_payment_order_id', None)
        return redirect('/')

    now = datetime.now()
    expires_at = order.created_date + timedelta(minutes=5)
    time_left = int((expires_at - now).total_seconds())

    if time_left <= 0:
        dao.cancel_expired_receipt(order_id)
        session.pop('current_payment_order_id', None)
        return redirect('/carts')

    return render_template('payment.html', order=order, time_left=time_left)


@pay_api.route('/payment', methods=['POST'])
@login_required
def pay():
    order_id = session.get('current_payment_order_id')
    if not order_id:
        return jsonify({"status": "error", "message": "Không tìm thấy phiên giao dịch!"}), 400

    order = Receipt.query.get(order_id)
    if not order:
        return jsonify({"status": "error", "message": "Đơn hàng không tồn tại!"}), 404

    if order.status == ReceiptStatus.PENDING:
        order.status = ReceiptStatus.PAID
        db.session.commit()

        payment_method = session.get('current_payment_method', 'banking')

        cart = session.get('pending_cart', {})

        try:
            payment_subject.notify(
                user_id=order.user_id,
                cart=cart,
                final_amount=order.final_amount,
                payment_method=payment_method
            )
        except Exception as e:
            print(f"Lỗi gửi email: {str(e)}")

        session.pop('current_payment_order_id', None)
        session.pop('current_payment_method', None)
        session.pop('pending_cart', None)

        return jsonify({"status": "success", "message": "Thanh toán thành công! Hãy kiểm tra Email."})

    return jsonify({"status": "error", "message": "Đơn hàng đã được xử lý hoặc hết hạn!"}), 400