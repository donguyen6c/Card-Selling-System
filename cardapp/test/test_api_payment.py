from datetime import datetime, timedelta
from unittest.mock import patch
import pytest
from cardapp.test.test_base import test_client, test_app, test_session
from cardapp.models import User, Category, Product, Card, Discount, Receipt, ReceiptStatus
from cardapp import db


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

# TEST THANH TOÁN - /pay (POST)

# Thanh toán thành công
def test_pay_success(test_client, sample_data, mocker):
    u = sample_data["user"]
    p1 = sample_data["products"][0]

    with patch('flask_login.utils._get_user', return_value=u):
        test_client.post('/carts/items', json={
            "id": p1["id"], "name": p1["name"],
            "price": p1["price"], "card_type": "phone", "quantity": 1
        })

        mock_receipt = mocker.patch('cardapp.dao.add_receipt', return_value=1)

        res = test_client.post('/pay', json={"payment_method": "banking"})
        data = res.get_json()

        assert res.status_code == 200
        assert data['status'] == 'success'
        assert data['message'] == 'Tạo đơn hàng thành công! Đang chuyển hướng...'
        mock_receipt.assert_called_once()

        with test_client.session_transaction() as sess:
            assert sess.get('current_payment_order_id') == 1
            assert sess.get('current_payment_method') == 'banking'

# Giỏ hàng trống
def test_pay_empty_cart(test_client, sample_data):
    u = sample_data["user"]

    with patch('flask_login.utils._get_user', return_value=u):
        res = test_client.post('/pay', json={"payment_method": "banking"})
        data = res.get_json()

        assert res.status_code == 400
        assert data['status'] == 'error'
        assert data['message'] == 'Giỏ hàng của bạn đang trống!'

# Thanh toán kèm mã giảm giá
def test_pay_with_discount(test_client, sample_data, mocker):
    u = sample_data["user"]
    p1 = sample_data["products"][0]
    d1 = sample_data["discounts"][0]

    with patch('flask_login.utils._get_user', return_value=u):
        test_client.post('/carts/items', json={
            "id": p1["id"], "name": p1["name"],
            "price": p1["price"], "card_type": "phone", "quantity": 1
        })

        test_client.post('/pay/discount', json={"code": d1.code})

        mock_receipt = mocker.patch('cardapp.dao.add_receipt', return_value=1)

        res = test_client.post('/pay', json={"payment_method": "banking"})
        data = res.get_json()

        assert res.status_code == 200
        assert data['status'] == 'success'
        mock_receipt.assert_called_once()
        with test_client.session_transaction() as sess:
            assert 'cart' not in sess
            assert 'discount_code' not in sess


def test_pay_dao_exception(test_client, sample_data, mocker):
    u = sample_data["user"]
    p1 = sample_data["products"][0]

    with patch('flask_login.utils._get_user', return_value=u):
        test_client.post('/carts/items', json={
            "id": p1["id"], "name": p1["name"],
            "price": p1["price"], "card_type": "phone", "quantity": 1
        })

        mocker.patch('cardapp.dao.add_receipt', side_effect=Exception('DB Error'))

        res = test_client.post('/pay', json={"payment_method": "banking"})
        data = res.get_json()

        assert res.status_code == 400
        assert data['status'] == 'error'
        with test_client.session_transaction() as sess:
            assert 'cart' in sess


# TEST XÁC NHẬN THANH TOÁN - /payment (POST)

# PENDING → PAID
def test_payment_success(test_client, sample_data, mocker):
    u = sample_data["user"]
    p1 = sample_data["products"][0]

    with patch('flask_login.utils._get_user', return_value=u):
        test_client.post('/carts/items', json={
            "id": p1["id"], "name": p1["name"],
            "price": p1["price"], "card_type": "phone", "quantity": 1
        })

        mocker.patch('cardapp.dao.add_receipt', return_value=1)
        mocker.patch('cardapp.apis.pay_api.payment_subject.notify')

        test_client.post('/pay', json={"payment_method": "banking"})

        order = Receipt(id=1, user_id=u.id, final_amount=50000, status=ReceiptStatus.PENDING)
        db.session.add(order)
        db.session.commit()

        res = test_client.post('/payment')
        data = res.get_json()

        assert res.status_code == 200
        assert data['status'] == 'success'

        with test_client.session_transaction() as sess:
            assert 'current_payment_order_id' not in sess
            assert 'pending_cart' not in sess


def test_payment_no_session(test_client, sample_data):
    u = sample_data["user"]

    with patch('flask_login.utils._get_user', return_value=u):
        res = test_client.post('/payment')
        data = res.get_json()

        assert res.status_code == 400
        assert data['status'] == 'error'
        assert data['message'] == 'Không tìm thấy phiên giao dịch!'

# Đơn đã thanh toán PAID
def test_payment_already_paid(test_client, sample_data, mocker):
    u = sample_data["user"]

    with patch('flask_login.utils._get_user', return_value=u):
        from cardapp.models import Receipt, ReceiptStatus
        from cardapp import db
        order = Receipt(id=1, user_id=u.id, final_amount=50000, status=ReceiptStatus.PAID)
        db.session.add(order)
        db.session.commit()

        with test_client.session_transaction() as sess:
            sess['current_payment_order_id'] = 1

        res = test_client.post('/payment')
        data = res.get_json()
        assert res.status_code == 400
        assert data['status'] == 'error'
        assert data['message'] == 'Đơn hàng đã được xử lý hoặc hết hạn!'


# TEST ALL - Thêm giỏ → Áp mã → Thanh toán

def test_full_flow_with_discount(test_client, test_session, sample_data, mocker):
    u = sample_data["user"]
    p1 = sample_data["products"][0]
    d1 = sample_data["discounts"][0]

    with patch('flask_login.utils._get_user', return_value=u):
        # 1: Thêm vào giỏ
        res = test_client.post('/carts/items', json={
            "id": p1["id"], "name": p1["name"],
            "price": p1["price"], "card_type": "phone", "quantity": 2
        })
        assert res.status_code == 200
        assert res.get_json()['total_quantity'] == 2

        # 2: Áp mã giảm giá
        res = test_client.post('/pay/discount', json={"code": d1.code})
        assert res.status_code == 200
        assert res.get_json()['discount_amount'] == 10000

        with test_client.session_transaction() as sess:
            assert sess.get('discount_code') == d1.code

        # 3: Tạo đơn hàng
        mocker.patch('cardapp.dao.add_receipt', return_value=1)
        mocker.patch('cardapp.apis.pay_api.payment_subject.notify')

        res = test_client.post('/pay', json={"payment_method": "banking"})
        assert res.status_code == 200
        assert res.get_json()['status'] == 'success'

        with test_client.session_transaction() as sess:
            assert 'cart' not in sess
            assert 'discount_code' not in sess
            assert sess.get('current_payment_order_id') == 1

        # 4: Xác nhận thanh toán
        from cardapp.models import Receipt, ReceiptStatus
        from cardapp import db
        order = Receipt(id=1, user_id=u.id, final_amount=90000, status=ReceiptStatus.PENDING)
        db.session.add(order)
        db.session.commit()

        res = test_client.post('/payment')
        assert res.status_code == 200
        assert res.get_json()['status'] == 'success'

        with test_client.session_transaction() as sess:
            assert 'current_payment_order_id' not in sess


def test_full_flow_without_discount(test_client, test_session, sample_data, mocker):
    u = sample_data["user"]
    p2 = sample_data["products"][1]

    with patch('flask_login.utils._get_user', return_value=u):
        # 1: Thêm giỏ
        res = test_client.post('/carts/items', json={
            "id": p2["id"], "name": p2["name"],
            "price": p2["price"], "card_type": "game", "quantity": 1
        })
        assert res.status_code == 200

        # 2: Thanh toán không dùng mã
        mocker.patch('cardapp.dao.add_receipt', return_value=1)
        mocker.patch('cardapp.apis.pay_api.payment_subject.notify')

        res = test_client.post('/pay', json={"payment_method": "cash"})
        assert res.status_code == 200

        from cardapp.models import Receipt, ReceiptStatus
        from cardapp import db
        order = Receipt(id=1, user_id=u.id, final_amount=100000, status=ReceiptStatus.PENDING)
        db.session.add(order)
        db.session.commit()

        res = test_client.post('/payment')
        assert res.status_code == 200
        assert res.get_json()['status'] == 'success'


