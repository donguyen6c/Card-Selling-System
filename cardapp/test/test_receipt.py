import pytest
from cardapp import dao, db
from cardapp.models import User, Category, Product, Card, Receipt, ReceiptDetails, ReceiptStatus
from datetime import datetime, timedelta
from cardapp.test.test_base import test_app, test_session, mock_cloudinary

@pytest.fixture
def sample_data(test_session):
    u = User(name="Buyer", username="testbuyer", password="Abc@1234", email="buyer@gmail.com")
    test_session.add(u)

    cate = Category(name="Viettel")
    test_session.add(cate)
    test_session.commit()

    p = Product(name="Viettel 50.000đ", price=50000, inventory=3, category_id=cate.id)
    test_session.add(p)
    test_session.commit()

    for i in range(3):
        c = Card(serial_number=f"SERI-{i}", pin_code=f"PIN-{i}",
                 expiry_date=datetime.now() + timedelta(days=365),
                 product_id=p.id, is_sold=False)
        test_session.add(c)

    test_session.commit()
    return {"user_id": u.id, "product_id": p.id, "product_name": p.name}


def test_add_receipt_empty_cart(test_session, sample_data):
    with pytest.raises(Exception, match="Giỏ hàng đang trống!"):
        dao.add_receipt(user_id=sample_data["user_id"], cart={})


def test_add_receipt_out_of_stock(test_session, sample_data):
    cart = {
        "1": {
            "id": sample_data["product_id"],
            "name": sample_data["product_name"],
            "price": 50000,
            "quantity": 4
        }
    }
    with pytest.raises(Exception, match=f"Sản phẩm '{sample_data['product_name']}' chỉ còn 3 thẻ"):
        dao.add_receipt(user_id=sample_data["user_id"], cart=cart)


def test_add_receipt_success(test_session, sample_data):
    cart = {
        "1": {
            "id": sample_data["product_id"],
            "name": sample_data["product_name"],
            "price": 50000,
            "quantity": 2
        }
    }

    receipt_id = dao.add_receipt(user_id=sample_data["user_id"], cart=cart)

    receipt = Receipt.query.get(receipt_id)

    assert receipt is not None
    assert receipt.user_id == sample_data["user_id"]
    assert receipt.total_amount == 100000
    assert receipt.status == ReceiptStatus.PENDING

    sold_cards = Card.query.filter_by(receipt_id=receipt_id).all()
    assert len(sold_cards) == 2
    assert all(c.is_sold is True for c in sold_cards)

    product = Product.query.get(sample_data["product_id"])
    assert product.inventory == 1


def test_cancel_expired_receipt(test_session, sample_data):
    cart = {"1": {"id": sample_data["product_id"], "name": sample_data["product_name"], "price": 50000, "quantity": 1}}
    receipt_id = dao.add_receipt(user_id=sample_data["user_id"], cart=cart)

    result = dao.cancel_expired_receipt(receipt_id)
    assert result is True

    r = Receipt.query.get(receipt_id)
    assert r.status == ReceiptStatus.CANCELLED

    cards = Card.query.filter_by(product_id=sample_data["product_id"]).all()
    assert all(c.is_sold is False for c in cards)

    p = Product.query.get(sample_data["product_id"])
    assert p.inventory == 3


