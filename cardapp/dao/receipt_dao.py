from cardapp.dao.discount_dao import check_discount
from cardapp.models import Receipt, ReceiptDetails, Discount, Card, DiscountType, Product, ReceiptStatus
from cardapp import db, utils
from datetime import datetime
from cardapp.utils import TRANSACTIONS_PAGE_SIZE, stats_cart
from cardapp.utils import CARD_DETAILS_PAGE_SIZE

def get_receipts_by_user(user_id, from_date=None, to_date=None, page=1, per_page=TRANSACTIONS_PAGE_SIZE):
    query = Receipt.query.filter(Receipt.user_id == user_id)

    if from_date:
        query = query.filter(Receipt.created_date >= from_date)

    if to_date:
        query = query.filter(Receipt.created_date <= f"{to_date} 23:59:59")

    return query.order_by(Receipt.created_date.desc()).paginate(page=page, per_page=per_page, error_out=False)

def get_cards_by_user(user_id, kw=None, from_date=None, to_date=None, page=1, per_page=CARD_DETAILS_PAGE_SIZE):
    query = Card.query.join(Receipt, Card.receipt_id == Receipt.id).filter(
        Receipt.user_id == user_id,
        Card.is_sold == True
    )

    if kw and kw.isdigit():
        query = query.filter(Receipt.id == int(kw))

    if from_date:
        query = query.filter(Receipt.created_date >= from_date)

    if to_date:
        query = query.filter(Receipt.created_date <= f"{to_date} 23:59:59")

    return query.order_by(Receipt.created_date.desc()).paginate(page=page, per_page=per_page, error_out=False)

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
        discount_id=discount_id,
        status=ReceiptStatus.PENDING
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
            Card.is_sold == False,
            Card.receipt_id.is_(None)
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
        return r.id
    except Exception as e:
        db.session.rollback()
        print(f"Lỗi thanh toán: {str(e)}")
        raise Exception("Có lỗi xảy ra trong quá trình ghi nhận đơn hàng!")


def cancel_expired_receipt(receipt_id):
    r = Receipt.query.get(receipt_id)

    if r and r.status == ReceiptStatus.PENDING:
        r.status = ReceiptStatus.CANCELLED

        for card in r.cards_sold:
            card.is_sold = False
            card.receipt_id = None

        for detail in r.details:
            product = Product.query.get(detail.product_id)
            if product:
                product.inventory += detail.quantity

        if r.discount_id:
            discount = Discount.query.get(r.discount_id)
            if discount and discount.used_count > 0:
                discount.used_count -= 1

        try:
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            print(f"Lỗi khi hủy đơn: {str(e)}")
            return False

    return False
