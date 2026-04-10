from cardapp.models import Receipt, ReceiptDetails, Discount, Card, DiscountType
from cardapp import db, utils
from datetime import datetime
from cardapp.utils import stats_cart

def load_discounts():
    return Discount.query.filter(Discount.active == True).all()

def get_receipts_by_user(user_id):
    return Receipt.query.filter(Receipt.user_id == user_id).order_by(Receipt.created_date.desc()).all()

def add_receipt(user_id, cart, discount_code=None):
    if not cart:
        raise Exception("Giỏ hàng đang trống!")

    stats = stats_cart(cart)
    total_amount = stats['total_amount']
    final_amount = total_amount
    discount_id = None

    if discount_code:
        discount_result = check_discount(discount_code, cart)
        if discount_result['success']:
            final_amount = total_amount - discount_result['discount_amount']
            discount_id = discount_result['discount_id']
        else:
            raise Exception(discount_result['message'])

    r = Receipt(
        user_id=user_id,
        total_amount=total_amount,
        final_amount=final_amount,
        discount_id=discount_id
    )
    db.session.add(r)

    for c in cart.values():
        buy_qty = c['quantity']
        product_id = c['id']

        d = ReceiptDetails(
            quantity=buy_qty,
            unit_price=c['price'],
            product_id=product_id,
            receipt=r
        )
        db.session.add(d)

        product = Product.query.get(product_id)
        if not product:
            db.session.rollback()
            raise Exception(f"Sản phẩm '{c['name']}' không tồn tại trong hệ thống!")

        available_cards = Card.query.filter(
            Card.product_id == product_id,
            Card.is_sold == False
        ).limit(buy_qty).all()

        if len(available_cards) < buy_qty:
            db.session.rollback()
            raise Exception(f"Sản phẩm '{c['name']}' chỉ còn {len(available_cards)} thẻ. Vui lòng giảm số lượng!")

        for card in available_cards:
            card.is_sold = True
            card.sold_receipt = r

        product.inventory -= buy_qty

    if discount_id:
        discount_obj = Discount.query.get(discount_id)
        if discount_obj:
            discount_obj.used_count += 1

    try:
        db.session.commit()
        return True
    except Exception as e:
        db.session.rollback()
        print(f"Lỗi thanh toán: {str(e)}")
        raise Exception("Có lỗi xảy ra trong quá trình ghi nhận đơn hàng!")
def check_discount(code, cart):
    pass