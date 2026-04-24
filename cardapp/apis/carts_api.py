# cardapp/apis/auth_api.py
import re
from flask import Blueprint, request, render_template, redirect, abort, jsonify, session
from flask_login import login_user, logout_user, current_user, login_required
from flasgger import swag_from
from sqlalchemy.exc import IntegrityError
from werkzeug.exceptions import Conflict

from cardapp import dao, utils
from cardapp.models import Product

carts_api = Blueprint('carts', __name__)

@carts_api.route('/carts', methods=['GET'])
@login_required
@swag_from('../docs/get_cart.yml')
def cart_view():
    cart = session.get('cart', {})

    cart_stats = utils.stats_cart(cart)

    return render_template('cart.html', cart_stats=cart_stats)

@carts_api.route('/carts/items', methods=['POST'])
@login_required
@swag_from('../docs/add_carts_items.yml')
def add_to_cart():
    cart = session.get('cart')
    if not cart:
        cart = {}

    data = request.json
    product_id = str(data.get('id'))
    name = data.get('name')
    price = float(data.get('price'))
    card_type = data.get('card_type')
    added_qty = int(data.get('quantity', 1))


    current_tier_limit = utils.get_tier_limit(price)

    qty_in_same_tier = 0
    for item in cart.values():
        if utils.get_tier_limit(item['price']) == current_tier_limit:
            if item['id'] != product_id:
                qty_in_same_tier += item['quantity']

    current_product_qty = cart[product_id]['quantity'] if product_id in cart else 0
    new_product_qty = current_product_qty + added_qty
    new_total_tier_qty = qty_in_same_tier + new_product_qty

    if new_total_tier_qty > current_tier_limit:
        return jsonify({
            "status": "error",
            "message": f"Hệ thống chỉ cho phép mua tối đa {current_tier_limit} thẻ thuộc mệnh giá {price:,.0f}đ/đơn. Giỏ hàng của bạn đang có {qty_in_same_tier + current_product_qty} thẻ nhóm này!"
        }), 400

    product = Product.query.get(product_id)
    if not product:
        return jsonify({
            "status": "error",
            "message": "Sản phẩm không tồn tại!"
        }), 404

    if new_product_qty > product.inventory:
        return jsonify({
            "status": "error",
            "message": f"Kho chỉ còn {product.inventory} mã thẻ!"
        }), 400

    if product_id in cart:
        cart[product_id]["quantity"] += added_qty
    else:
        cart[product_id] = {
            "id": product_id,
            "name": name,
            "price": price,
            "card_type": card_type,
            "quantity": added_qty
        }

    session['cart'] = cart

    stats = utils.stats_cart(cart)
    return jsonify({
        "status": "success",
        "message": f"Đã thêm vào giỏ! (Nhóm này đang có {new_total_tier_qty}/{current_tier_limit} thẻ)",
        "total_quantity": stats.get('total_quantity', 0)
    })

@carts_api.route('/carts/items/<id>', methods=['PATCH'])
@login_required
@swag_from('../docs/update_carts.yml')
def update_to_cart(id):
    cart = session.get('cart', {})

    if id not in cart:
        return jsonify({
            "status": "error",
            "message": "Sản phẩm không tồn tại trong giỏ"
        }), 404

    data = request.json
    if not data or "quantity" not in data:
        return jsonify({
            "status": "error",
            "message": "Thiếu trường quantity"
        }), 400

    try:
        new_qty = int(data.get("quantity"))
        if new_qty <= 0:
            raise ValueError()
    except (ValueError, TypeError):
        return jsonify({
            "status": "error",
            "message": "quantity phải là số nguyên > 0"
        }), 400

    price = cart[id]['price']
    current_tier_limit = utils.get_tier_limit(price)

    qty_in_same_tier = 0
    for item in cart.values():
        if utils.get_tier_limit(item['price']) == current_tier_limit:
            if item['id'] != id:
                qty_in_same_tier += item['quantity']

    if (qty_in_same_tier + new_qty) > current_tier_limit:
        return jsonify({
            "status": "error",
            "message": f"Hệ thống chỉ cho phép mua tối đa {current_tier_limit} thẻ nhóm giá {price:,.0f}đ/đơn!"
        }), 400

    product = Product.query.get(id)

    # ✅ tách rõ tránh lỗi ngầm
    if not product:
        return jsonify({
            "status": "error",
            "message": "Sản phẩm không tồn tại!"
        }), 404

    if new_qty > product.inventory:
        return jsonify({
            "status": "error",
            "message": f"Kho chỉ còn {product.inventory} mã thẻ!"
        }), 400

    cart[id]["quantity"] = new_qty
    session['cart'] = cart

    stats = utils.stats_cart(cart)
    return jsonify({
        "status": "success",
        "total_quantity": stats['total_quantity'],
        "total_amount": stats['total_amount']
    })

@carts_api.route('/carts/items/<product_id>', methods=['DELETE'])
@login_required
@swag_from('../docs/delete_carts_items.yml')
def delete_to_cart(product_id):
    cart = session.get('cart') or {}

    if cart and product_id in cart:
        del cart[product_id]
        session['cart'] = cart

    stats = utils.stats_cart(cart)
    return jsonify({
        "status": "success",
        "total_quantity": stats['total_quantity'],
        "total_amount": stats['total_amount']
    }), 200