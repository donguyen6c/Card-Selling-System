from cardapp.models import Category, Product, User, Receipt, ReceiptDetails, Discount, Card, DiscountType, Banner
import hashlib

def load_categories():
    return Category.query.all()

def load_banners():
    return Banner.query.filter(Banner.active == True).all()

def load_discounts():
    return Discount.query.filter(Discount.active == True).all()

def load_products(cate_id=None, kw=None, page=1):
    query = Product.query

    if kw:
        query = query.filter(Product.name.contains(kw))

    if cate_id:
        query = query.filter(Product.category_id.__eq__(cate_id))

    return query.all()

def count_products():
    return Product.query.count()

def get_user_by_id(id):
    return User.query.get(id)

def auth_user(username, password):
    password = str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())
    return User.query.filter(User.username==username,
                             User.password==password).first()

def get_receipts_by_user(user_id):
    return Receipt.query.filter(Receipt.user_id == user_id).order_by(Receipt.created_date.desc()).all()

