from cardapp.models import Receipt

def get_receipts_by_user(user_id):
    return Receipt.query.filter(Receipt.user_id == user_id).order_by(Receipt.created_date.desc()).all()

def add_receipt(user_id, cart, discount_code=None):
    pass
