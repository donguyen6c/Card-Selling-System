import pytest
from datetime import datetime, timedelta
from cardapp import dao, db
from cardapp.models import User, Category, Product, Card, Receipt, Discount, DiscountType
from cardapp.test.test_base import test_app, test_session


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


def test_get_receipts_by_user_no_filter(test_session, sample_data):
    pagination = dao.get_receipts_by_user(user_id=sample_data, page=1, per_page=10)

    assert pagination.total == 2
    assert len(pagination.items) == 2
    assert pagination.items[0].created_date >= pagination.items[1].created_date


def test_get_receipts_by_user_filter_date(test_session, sample_data):
    today = datetime.now().strftime('%Y-%m-%d')
    yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')

    res_from_today = dao.get_receipts_by_user(user_id=sample_data, from_date=today)
    assert res_from_today.total == 2

    res_to_yesterday = dao.get_receipts_by_user(user_id=sample_data, to_date=yesterday)
    assert res_to_yesterday.total == 0


def test_get_receipts_by_user_pagination(test_session, sample_data):
    page1 = dao.get_receipts_by_user(user_id=sample_data, page=1, per_page=1)

    assert page1.total == 2
    assert len(page1.items) == 1
    assert page1.pages == 2

    page2 = dao.get_receipts_by_user(user_id=sample_data, page=2, per_page=1)
    assert len(page2.items) == 1
    assert page2.items[0].id != page1.items[0].id


def test_get_receipts_by_user_empty(test_session):
    pagination = dao.get_receipts_by_user(user_id=999)

    assert pagination.total == 0
    assert len(pagination.items) == 0


