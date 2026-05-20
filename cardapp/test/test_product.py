import pytest
from cardapp import dao, db
from cardapp.models import Category, Product
from cardapp.test.test_base import test_app, test_session

@pytest.fixture
def sample_data(test_session):
    c1 = Category(name="Điện thoại")
    c2 = Category(name="Thẻ Game")
    c3 = Category(name="Khác")
    test_session.add_all([c1, c2, c3])
    test_session.commit()

    p1 = Product(name="Viettel 100k", price=100000, category_id=c1.id)
    p2 = Product(name="Vinaphone 50k", price=50000, category_id=c1.id)
    p3 = Product(name="Garena 20k", price=20000, category_id=c2.id)
    test_session.add_all([p1, p2, p3])

    test_session.commit()
    return {"cate_mobile": c1.id, "cate_game": c2.id, "cate_empty": c3.id}

def test_load_categories(test_session, sample_data):
    categories = dao.load_categories()
    assert len(categories) == 3
    assert categories[0].name == "Điện thoại"


def test_load_products_no_filter(test_session, sample_data):
    products = dao.load_products()
    assert len(products) == 3

def test_load_products_filter_kw(test_session, sample_data):
    products = dao.load_products(kw="Viettel")
    assert len(products) == 1
    assert products[0].name == "Viettel 100k"

def test_load_products_filter_cate(test_session, sample_data):
    products = dao.load_products(cate_id=sample_data["cate_game"])
    assert len(products) == 1
    assert "Garena" in products[0].name

def test_count_products(test_session, sample_data):
    assert dao.count_products() == 3


