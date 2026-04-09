from cardapp.models import Receipt, ReceiptDetails, Discount, Card, DiscountType
from cardapp import db, utils
from datetime import datetime
from cardapp.utils import CARD_DETAILS_PAGE_SIZE

def load_discounts():
    return Discount.query.filter(Discount.active == True).all()

def get_receipts_by_user(user_id):
    return Receipt.query.filter(Receipt.user_id == user_id).order_by(Receipt.created_date.desc()).all()

def get_cards_by_user(user_id, page=1, per_page=CARD_DETAILS_PAGE_SIZE):
    return (Card.query.join(Receipt, Card.receipt_id == Receipt.id).
            filter(Receipt.user_id == user_id, Card.is_sold == True)
            .order_by(Receipt.created_date.desc())
            .paginate(page=page, per_page=per_page, error_out=False))

def add_receipt(user_id, cart, discount_code=None):
    pass

def check_discount(code, cart):
    pass