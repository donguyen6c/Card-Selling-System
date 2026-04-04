from cardapp.models import Category, Product, Banner, Card
from sqlalchemy import func
from cardapp import db

def load_categories():
    return Category.query.all()

def load_banners():
    return Banner.query.filter(Banner.active == True).all()

def load_products(cate_id=None, kw=None, page=1):
    query = Product.query
    if kw:
        query = query.filter(Product.name.contains(kw))
    if cate_id:
        query = query.filter(Product.category_id.__eq__(cate_id))
    return query.all()

def count_products():
    return Product.query.count()

def count_product_by_cate():
    pass