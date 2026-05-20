import pytest
from datetime import datetime, timedelta
from cardapp import dao, db
from cardapp.models import User, Category, Product, Card, Receipt, Discount, DiscountType
from cardapp.test.test_base import test_app, test_session
from cardapp.dao.receipt_dao import get_cards_by_user

@pytest.fixture
def sample_data(test_session):
    u = User(name="Tester", username="tester", password="123", email="t@gmail.com")
    test_session.add(u)
    test_session.commit()

    cate = Category(name="Phone Card")
    test_session.add(cate)
    test_session.commit()

    p = Product(name="Viettel 10k", price=10000, category_id=cate.id)
    test_session.add(p)
    test_session.commit()

    d = Discount(code="SALE5", active=True, discount_type="FIXED_AMOUNT", value=5000,
                 start_date=datetime.now(), end_date=datetime.now() + timedelta(days=1))
    test_session.add(d)

    for i in range(2):
        r = Receipt(user_id=u.id, total_amount=20000, final_amount=20000)
        test_session.add(r)
        test_session.commit()

        for j in range(2):
            c = Card(serial_number=f"SN-{i}-{j}",
                     pin_code=f"PIN-{i}-{j}",
                     expiry_date=datetime.now() + timedelta(days=365),
                     product_id=p.id,
                     is_sold=True,
                     receipt_id=r.id)
            test_session.add(c)

    test_session.commit()
    return u.id

def test_load_discounts(test_session, sample_data):
    discounts = dao.load_discounts()
    assert len(discounts) >= 1
    assert discounts[0].code == "SALE5"
    assert discounts[0].active is True

def test_get_receipts_by_user(test_session, sample_data):
    receipts = dao.get_receipts_by_user(user_id=sample_data)

    assert len(receipts.items) == 2
    assert receipts.items[0].created_date >= receipts.items[1].created_date


def test_get_cards_by_user_no_filter(test_session, sample_data):
    pagination = dao.get_cards_by_user(user_id=sample_data, page=1, per_page=2)

    assert pagination.total == 4
    assert len(pagination.items) == 2
    assert pagination.pages == 2


def test_get_cards_by_user_filter_kw(test_session, sample_data):
    first_receipt = Receipt.query.filter_by(user_id=sample_data).first()

    pagination = dao.get_cards_by_user(user_id=sample_data, kw=str(first_receipt.id))

    assert pagination.total == 2
    assert all(card.receipt_id == first_receipt.id for card in pagination.items)


def test_get_cards_by_user_filter_date(test_session, sample_data):
    today = datetime.now().strftime('%Y-%m-%d')
    yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')

    res_today = dao.get_cards_by_user(user_id=sample_data, from_date=today)
    assert res_today.total == 4


    res_yesterday = dao.get_cards_by_user(user_id=sample_data, to_date=yesterday)
    assert res_yesterday.total == 0

