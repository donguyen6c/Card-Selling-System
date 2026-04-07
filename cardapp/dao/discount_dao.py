from cardapp.models import Receipt, ReceiptDetails, Discount, Card, DiscountType
from cardapp import db, utils
from datetime import datetime

def load_discounts():
    return Discount.query.filter(Discount.active == True).all()

def check_discount(code, cart):
    pass