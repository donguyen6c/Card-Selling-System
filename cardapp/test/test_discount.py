import pytest
from datetime import datetime, timedelta
from cardapp.dao.discount_dao import check_discount
from cardapp.models import Discount, DiscountType
from cardapp.test.test_base import test_app, test_session

@pytest.fixture
def sample_discounts(test_session):
    d1 = Discount(
        code="GAME20",
        description="Giảm 20% thẻ Game",
        discount_type=DiscountType.PERCENTAGE,
        value=20,
        applied_card_type="GAME",
        start_date=datetime.now() - timedelta(days=1),
        end_date=datetime.now() + timedelta(days=30),
        min_quantity=2,
        max_quantity=5,
        active=True,
        used_count=0,
        usage_limit=10
    )
    d2 = Discount(
        code="EXPIRED10",
        description="Mã hết hạn",
        discount_type=DiscountType.FIXED_AMOUNT,
        value=10000,
        applied_card_type="PHONE",
        start_date=datetime.now() - timedelta(days=10),
        end_date=datetime.now() - timedelta(days=1),
        min_quantity=1,
        active=True,
        used_count=0
    )
    d3 = Discount(
        code="FULLUSAGE",
        description="Hết lượt dùng",
        discount_type=DiscountType.FIXED_AMOUNT,
        value=5000,
        start_date=datetime.now() - timedelta(days=1),
        end_date=datetime.now() + timedelta(days=1),
        min_quantity=1,
        usage_limit=5,
        used_count=5,
        active=True
    )
    d4 = Discount(
            code="fixedphonediscount",
            description="Giảm giá 5k cho",
            discount_type=DiscountType.FIXED_AMOUNT,
            value=5000,
            start_date=datetime.now() - timedelta(days=1),
            end_date=datetime.now() + timedelta(days=1),
            min_quantity=1,
            usage_limit=5,
            used_count=0,
            active=True
        )

    test_session.add_all([d1, d2, d3, d4])
    test_session.commit()
    return {
        "game_code": d1.code,
        "expired_code": d2.code,
        "full_code": d3.code,
	"fixed_phone_code": d4.code
    }

def test_discount_empty_cart(test_session, sample_discounts):
    empty_cart = {}
    result = check_discount(sample_discounts["game_code"], empty_cart)

    assert result['success'] is False
    assert result['discount_amount'] == 0
    assert result['message'] == "Giỏ hàng rỗng!"

def test_discount_not_exist(test_session, sample_discounts):
    cart = {"1": {"id": 1, "name": "Garena", "price": 50000, "quantity": 1}}
    result = check_discount("INVALID_CODE", cart)

    assert result['success'] is False
    assert result['message'] == "Mã giảm giá không tồn tại!"

def test_discount_expired(test_session, sample_discounts):
    cart = {"1": {"id": 1, "name": "Viettel", "price": 50000, "quantity": 1, "card_type": "phone"}}
    result = check_discount(sample_discounts["expired_code"], cart)

    assert result['success'] is False
    assert result['message'] == "Mã giảm giá đã hết hạn!"

def test_discount_usage_limit(test_session, sample_discounts):
    cart = {"1": {"id": 1, "name": "Viettel", "price": 50000, "quantity": 1}}
    result = check_discount(sample_discounts["full_code"], cart)

    assert result['success'] is False
    assert "đã hết lượt sử dụng" in result['message']


def test_discount_wrong_card_type(test_session, sample_discounts):
    cart = {"1": {"id": 1, "name": "Mobi", "price": 50000, "quantity": 3, "card_type": "phone"}}
    result = check_discount(sample_discounts["game_code"], cart)

    assert result['success'] is False
    assert "chỉ áp dụng cho thẻ GAME" in result['message']


def test_discount_min_quantity_not_match(test_session, sample_discounts):
    cart = {"1": {"id": 1, "name": "Garena", "price": 50000, "quantity": 1, "card_type": "game"}}
    result = check_discount(sample_discounts["game_code"], cart)

    assert result['success'] is False
    assert "Cần mua ít nhất 2 thẻ" in result['message']


def test_discount_success_percentage(test_session, sample_discounts):
    cart = {
        "1": {"id": 1, "name": "Garena", "price": 100000, "quantity": 2, "card_type": "game"}
    }
    result = check_discount(sample_discounts["game_code"], cart)

    assert result['success'] is True
    assert result['discount_amount'] == 40000
    assert result['message'] == "Áp dụng mã giảm giá thành công!"


def test_discount_success_fixed_amount(test_session, sample_discounts):
    cart = {
        "1": {"id": 1, "name": "Mobi", "price": 100000, "quantity": 2, "card_type": "phone"}
    }
    result = check_discount(sample_discounts["fixed_phone_code"], cart)

    assert result['success'] is True
    assert result['discount_amount'] == 5000
    assert result['message'] == "Áp dụng mã giảm giá thành công!"

