from cardapp.models import Product, Receipt, ReceiptDetails
from cardapp import db
from sqlalchemy import func

def revenue_by_product():
    return (db.session.query(Product.id, Product.name, func.sum(ReceiptDetails.unit_price * ReceiptDetails.quantity))
            .join(ReceiptDetails, ReceiptDetails.product_id == Product.id)
            .group_by(Product.id, Product.name).all())

def revenue_by_time(period="month"):
    return ((db.session.query(func.extract('month', Receipt.created_date), func.sum(Receipt.final_amount))
            .group_by(func.extract('month', Receipt.created_date)))
            .order_by(func.extract('month', Receipt.created_date)).all())