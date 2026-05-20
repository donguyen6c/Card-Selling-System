from datetime import datetime, timedelta
from unittest.mock import patch
import pytest
from cardapp.test.base import test_client, test_app, test_session
from cardapp.models import User, Category, Product, Card


@pytest.fixture
def sample_data(test_session):
    u = User(name="Buyer", username="testbuyer", password="Abc@1234", email="buyer@gmail.com")
    test_session.add(u)
    test_session.commit()

    cate1 = Category(name="Viettel")
    cate2 = Category(name="Garena")
    test_session.add_all([cate1, cate2])
    test_session.commit()

    p1 = Product(name="Viettel 50.000đ", price=50000, inventory=10, category_id=cate1.id)
    p2 = Product(name="Garena 100.000đ", price=100000, inventory=4, category_id=cate2.id)
    test_session.add_all([p1, p2])
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
        ]
    }


def test_add_to_cart_single(test_client, sample_data):
    u = sample_data["user"]
    p1 = sample_data["products"][0]

    with patch('flask_login.utils._get_user', return_value=u):
        res = test_client.post('/carts/items', json={
            "id": p1["id"],
            "name": p1["name"],
            "price": p1["price"],
            "card_type": "phone",
            "quantity": 2
        })

        assert res.status_code == 200
        data = res.get_json()
        assert data['status'] == 'success'
        assert data['total_quantity'] == 2

        with test_client.session_transaction() as sess:
            assert 'cart' in sess
            assert str(p1["id"]) in sess['cart']


def test_add_to_cart_multiple(test_client, sample_data):
    u = sample_data["user"]
    p1 = sample_data["products"][0]
    p2 = sample_data["products"][1]

    with patch('flask_login.utils._get_user', return_value=u):
        res = test_client.post('/carts/items', json={
            "id": p1["id"],
            "name": p1["name"],
            "price": p1["price"],
            "card_type": "phone",
            "quantity": 2
        })
        assert res.status_code == 200
        assert res.get_json()['total_quantity'] == 2

        res = test_client.post('/carts/items', json={
            "id": p2["id"],
            "name": p2["name"],
            "price": p2["price"],
            "card_type": "game",
            "quantity": 1
        })
        assert res.status_code == 200
        assert res.get_json()['total_quantity'] == 3

        with test_client.session_transaction() as sess:
            assert sess['cart'][str(p1["id"])]['quantity'] == 2
            assert sess['cart'][str(p2["id"])]['quantity'] == 1

def test_update_cart_success(test_client, sample_data):
    u = sample_data["user"]
    p1 = sample_data["products"][0]

    with patch('flask_login.utils._get_user', return_value=u):
        test_client.post('/carts/items', json={
            "id": p1["id"],
            "name": p1["name"],
            "price": p1["price"],
            "card_type": "phone",
            "quantity": 1
        })

        res = test_client.patch(f'/carts/items/{p1["id"]}', json={
            "quantity": 3
        })

        assert res.status_code == 200
        data = res.get_json()
        assert data['status'] == 'success'
        assert data['total_quantity'] == 3

        with test_client.session_transaction() as sess:
            assert sess['cart'][str(p1["id"])]['quantity'] == 3

# Test khi id của thẻ ko tồn tại
def test_update_cart_not_found(test_client, sample_data):
    u = sample_data["user"]

    with patch('flask_login.utils._get_user', return_value=u):
        res = test_client.patch('/carts/items/9999', json={
            "quantity": 2
        })

        assert res.status_code == 404
        data = res.get_json()
        assert data['status'] == 'error'

#Cập nhật ko kèm quantity
def test_update_cart_missing_quantity(test_client, sample_data):
    u = sample_data["user"]
    p1 = sample_data["products"][0]

    with patch('flask_login.utils._get_user', return_value=u):
        test_client.post('/carts/items', json={
            "id": p1["id"],
            "name": p1["name"],
            "price": p1["price"],
            "card_type": "phone",
            "quantity": 1
        })

        res = test_client.patch(f'/carts/items/{p1["id"]}', json={})

        assert res.status_code == 400
        data = res.get_json()
        assert data['status'] == 'error'
        assert data['message'] == 'Thiếu trường quantity'

#Truyền quantity sai
def test_update_cart_invalid_quantity(test_client, sample_data):
    u = sample_data["user"]
    p1 = sample_data["products"][0]

    with patch('flask_login.utils._get_user', return_value=u):
        test_client.post('/carts/items', json={
            "id": p1["id"],
            "name": p1["name"],
            "price": p1["price"],
            "card_type": "phone",
            "quantity": 1
        })

        res = test_client.patch(f'/carts/items/{p1["id"]}', json={
            "quantity": 0
        })
        assert res.status_code == 400
        assert res.get_json()['message'] == 'quantity phải là số nguyên > 0'

        res = test_client.patch(f'/carts/items/{p1["id"]}', json={
            "quantity": -1
        })
        assert res.status_code == 400

# Vượt giới hạn trong kho
def test_update_cart_exceed_inventory(test_client, sample_data):
    u = sample_data["user"]
    p2 = sample_data["products"][1]

    with patch('flask_login.utils._get_user', return_value=u):
        test_client.post('/carts/items', json={
            "id": p2["id"],
            "name": p2["name"],
            "price": p2["price"],
            "card_type": "phone",
            "quantity": 1
        })

        res = test_client.patch(f'/carts/items/{p2["id"]}', json={
            "quantity": 5
        })

        assert res.status_code == 400
        data = res.get_json()
        assert data['status'] == 'error'
        assert 'Kho chỉ còn' in data['message']

# Bị giới hạn loại thẻ
def test_update_cart_exceed_tier_limit(test_client, sample_data):
    u = sample_data["user"]
    p1 = sample_data["products"][0]

    with patch('flask_login.utils._get_user', return_value=u):
        test_client.post('/carts/items', json={
            "id": p1["id"],
            "name": p1["name"],
            "price": p1["price"],
            "card_type": "phone",
            "quantity": 1
        })

        res = test_client.patch(f'/carts/items/{p1["id"]}', json={
            "quantity": 6
        })

        assert res.status_code == 400
        data = res.get_json()
        assert data['status'] == 'error'
        assert 'tối đa' in data['message']

def test_delete_cart(test_client, sample_data):
    u = sample_data["user"]
    p1 = sample_data["products"][0]

    with patch('flask_login.utils._get_user', return_value=u):
        test_client.post('/carts/items', json={
            "id": p1["id"],
            "name": p1["name"],
            "price": p1["price"],
            "card_type": "phone",
            "quantity": 3
        })

        res = test_client.delete(f'/carts/items/{p1["id"]}')

        assert res.status_code == 200
        data = res.get_json()
        assert data['status'] == 'success'
        assert data['total_quantity'] == 0

