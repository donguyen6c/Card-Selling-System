from datetime import datetime, timedelta
from unittest.mock import patch
import pytest
from cardapp.test.base import test_client, test_app, test_session
from cardapp.models import User, Category, Product, Card, Discount


@pytest.fixture
def sample_data(test_session):
    u = User(name="Buyer", username="testbuyer", password="Abc@1234", email="buyer@gmail.com")
    test_session.add(u)
    test_session.commit()

    cate1 = Category(name="Viettel", card_type="PHONE")
    cate2 = Category(name="Garena", card_type="GAME")
    test_session.add_all([cate1, cate2])
    test_session.commit()

    p1 = Product(name="Viettel 50.000đ", price=50000, inventory=10, category_id=cate1.id)
    p2 = Product(name="Garena 100.000đ", price=100000, inventory=4, category_id=cate2.id)
    test_session.add_all([p1, p2])
    test_session.commit()

    d1 = Discount(code="CODE1", discount_type="FIXED_AMOUNT", value=10000, applied_card_type="PHONE", end_date=datetime(2026, 5, 30), max_quantity=5, usage_limit=2 )
    d2 = Discount(code="CODE2", discount_type="FIXED_AMOUNT", value=10000, applied_card_type="GAME", end_date=datetime(2026, 5, 30), max_quantity=2, usage_limit=2 ,used_count=1 )
    d3 = Discount(code="CODE3", discount_type="FIXED_AMOUNT", value=10000, applied_card_type="GAME", end_date=datetime(2026, 5, 30), max_quantity=2, usage_limit=1 ,used_count=1 )
    test_session.add_all([d1, d2, d3])
    test_session.commit()

    for i in range(3):
        c1 = Card(serial_number=f"SERI1-{i}", pin_code=f"PIN1-{i}",
                  expiry_date=datetime.now() + timedelta(days=365),
                  product_id=p1.id, is_sold=False)
        c2 = Card(serial_number=f"SERI2-{i}", pin_code=f"PIN2-{i}",
                  expiry_date=datetime.now() + timedelta(days=365),
                  product_id=p2.id, is_sold=False)
        test_session.add_all([c1, c2])

    test_session.commit()

    return {
        "user": u,
        "products": [
            {"id": p1.id, "name": p1.name, "price": p1.price},
            {"id": p2.id, "name": p2.name, "price": p2.price}
        ],
        "discounts": [d1,d2,d3]
    }

def test_check_discount(test_client, sample_data):
    u = sample_data["user"]
    p1 = sample_data["products"][0]
    d1 = sample_data["discounts"][0]

    with patch('flask_login.utils._get_user', return_value=u):
        test_client.post('/carts/items', json={
            "id": p1["id"],
            "name": p1["name"],
            "price": p1["price"],
            "card_type": "phone",
            "quantity": 1
        })

        res = test_client.post(f'/pay/discount', json={"code": d1.code})

        data = res.get_json()
        assert data['status'] == 'success'
        assert data['discount_amount'] == 10000

# Mã PHONE nhưng giỏ toàn GAME
def test_check_discount_wrong_card_type(test_client, sample_data):
    u = sample_data["user"]
    p2 = sample_data["products"][1]
    d1 = sample_data["discounts"][0]

    with patch('flask_login.utils._get_user', return_value=u):
        test_client.post('/carts/items', json={
            "id": p2["id"], "name": p2["name"],
            "price": p2["price"], "card_type": "game", "quantity": 1
        })

        res = test_client.post('/pay/discount', json={"code": d1.code})
        data = res.get_json()

        print(data)
        assert res.status_code == 400
        assert data['status'] == 'error'
        assert data['discount_amount'] == 0
        assert data['message'] == 'Mã này chỉ áp dụng cho thẻ PHONE!'


def test_check_discount_invalid_code(test_client, sample_data):
    u = sample_data["user"]
    p1 = sample_data["products"][0]

    with patch('flask_login.utils._get_user', return_value=u):
        test_client.post('/carts/items', json={
            "id": p1["id"], "name": p1["name"],
            "price": p1["price"], "card_type": "phone", "quantity": 1
        })

        res = test_client.post('/pay/discount', json={"code": "INVALID_CODE"})
        data = res.get_json()

        assert res.status_code == 400
        assert data['status'] == 'error'
        assert data['message'] == 'Mã giảm giá không tồn tại!'

# Giỏ hàng rỗng
def test_check_discount_empty_cart(test_client, sample_data):
    u = sample_data["user"]
    d1 = sample_data["discounts"][0]

    with patch('flask_login.utils._get_user', return_value=u):
        res = test_client.post('/pay/discount', json={"code": d1.code})
        data = res.get_json()

        assert res.status_code == 400
        assert data['status'] == 'error'
        assert data['message'] == 'Giỏ hàng rỗng!'

# Hết lượt sử dụng mã
def test_check_discount_usage_limit_exceeded(test_client, sample_data):
    u = sample_data["user"]
    p2 = sample_data["products"][0]
    d2 = sample_data["discounts"][2]

    with patch('flask_login.utils._get_user', return_value=u):
        test_client.post('/carts/items', json={
            "id": p2["id"], "name": p2["name"],
            "price": p2["price"], "card_type": "game", "quantity": 1
        })

        res = test_client.post('/pay/discount', json={"code": d2.code})
        data = res.get_json()

        assert res.status_code == 400
        assert data['status'] == 'error'
        assert 'hết lượt sử dụng' in data['message']

# mã 2 max_quantity=2 nhưng giỏ có 3 thẻ GAME
def test_check_discount_exceeds_max_quantity(test_client, sample_data):
    u = sample_data["user"]
    p2 = sample_data["products"][1]
    d2 = sample_data["discounts"][1]

    with patch('flask_login.utils._get_user', return_value=u):
        test_client.post('/carts/items', json={
            "id": p2["id"], "name": p2["name"],
            "price": p2["price"], "card_type": "game", "quantity": 3
        })

        res = test_client.post('/pay/discount', json={"code": d2.code})
        data = res.get_json()

        assert res.status_code == 400
        assert data['status'] == 'error'
        assert data['message'] == 'Mã này chỉ áp dụng khi mua tối đa 2 thẻ!'