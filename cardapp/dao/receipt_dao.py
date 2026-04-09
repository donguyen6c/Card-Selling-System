from cardapp.models import Receipt, ReceiptDetails, Discount, Card, DiscountType
from cardapp import db, utils
from datetime import datetime
from cardapp.utils import TRANSACTIONS_PAGE_SIZE

def get_receipts_by_user(user_id, from_date=None, to_date=None, page=1, per_page=TRANSACTIONS_PAGE_SIZE):
    query = Receipt.query.filter(Receipt.user_id == user_id)

    if from_date:
        query = query.filter(Receipt.created_date >= from_date)

    if to_date:
        query = query.filter(Receipt.created_date <= f"{to_date} 23:59:59")

    return query.order_by(Receipt.created_date.desc()).paginate(page=page, per_page=per_page, error_out=False)

def add_receipt(user_id, cart, discount_code=None):
    pass
