from cardapp.models import Receipt, ReceiptDetails, Discount, Card, DiscountType
from cardapp import db, utils
from datetime import datetime

def load_discounts():
    return Discount.query.filter(Discount.active == True).all()

def get_receipts_by_user(user_id):
    return Receipt.query.filter(Receipt.user_id == user_id).order_by(Receipt.created_date.desc()).all()

def add_receipt(user_id, cart, discount_code=None):
    pass

def check_discount(code, cart):
    pass