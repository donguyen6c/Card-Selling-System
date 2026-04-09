from cardapp.models import Receipt, ReceiptDetails, Discount, Card, DiscountType
from cardapp import db, utils
from datetime import datetime
from cardapp.utils import TRANSACTIONS_PAGE_SIZE

def get_receipts_by_user(user_id, page = 1, per_page = TRANSACTIONS_PAGE_SIZE):
    return Receipt.query.filter(Receipt.user_id == user_id).order_by(Receipt.created_date.desc()).paginate(page=page, per_page = per_page, error_out = False)

def add_receipt(user_id, cart, discount_code=None):
    pass
