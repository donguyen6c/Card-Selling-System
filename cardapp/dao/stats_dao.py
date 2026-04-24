import datetime
from cardapp.models import Product, Receipt, ReceiptDetails, ReceiptStatus
from cardapp import db
from sqlalchemy import func

def revenue_by_product():
    return (db.session.query(Product.id, Product.name, func.sum(ReceiptDetails.unit_price * ReceiptDetails.quantity) )
            .join(ReceiptDetails, ReceiptDetails.product_id == Product.id)
            .join(Receipt, Receipt.id == ReceiptDetails.receipt_id)
            .filter(Receipt.status == ReceiptStatus.PAID)
            .group_by(Product.id, Product.name)
            .all())

def revenue_by_time(year=None):
    if year is None:
        year = datetime.now().year
    return (db.session.query(func.extract('month', Receipt.created_date).label('month'),func.sum(Receipt.final_amount).label('revenue'))
            .filter(func.extract('year', Receipt.created_date) == year)
            .filter(Receipt.status == ReceiptStatus.PAID)
            .group_by(func.extract('month', Receipt.created_date))
            .order_by(func.extract('month', Receipt.created_date))
            .all())