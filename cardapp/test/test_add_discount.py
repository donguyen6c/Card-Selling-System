import pytest
from unittest.mock import patch
from datetime import datetime, timedelta
from cardapp.models import Discount, DiscountType, User, UserRole
from cardapp.admin import DiscountView
from cardapp import db
from cardapp.test.base import test_app, test_session

@pytest.fixture
def view(test_session):
    return DiscountView(Discount, test_session)


@pytest.fixture
def mock_admin():
    admin = User(username="admin", user_role=UserRole.ADMIN)
    with patch('flask_login.utils._get_user', return_value=admin):
        yield admin


@pytest.fixture
def mock_user():
    user = User(username="user", user_role=UserRole.USER)
    with patch('flask_login.utils._get_user', return_value=user):
        yield user


def test_add_discount_security(test_app, view, mock_user):
    with test_app.test_request_context():
        model = Discount(code="Test_Security", value=10)
        with pytest.raises(ValueError, match="LỖI BẢO MẬT"):
            view.on_model_change(None, model, is_created=True)


def test_add_discount_duplicate(test_app, test_session, view, mock_admin):
    with test_app.test_request_context():
        d1 = Discount(code="SALE10", value=10, discount_type=DiscountType.PERCENTAGE,
                      end_date=datetime.now() + timedelta(days=1))
        test_session.add(d1)
        test_session.commit()

        new_model = Discount(code="SALE10", value=5)
        with pytest.raises(ValueError, match="đã tồn tại"):
            view.on_model_change(None, new_model, is_created=True)


def test_add_discount_invalid_percent(test_app, view, mock_admin):
    with test_app.test_request_context():
        model_high = Discount(code="SALE60", discount_type=DiscountType.PERCENTAGE, value=60)
        with pytest.raises(ValueError, match="không vượt quá 50%"):
            view.on_model_change(None, model_high, is_created=True)

        model_low = Discount(code="SALE0", discount_type=DiscountType.PERCENTAGE, value=0)
        with pytest.raises(ValueError, match="phải lớn hơn 0"):
            view.on_model_change(None, model_low, is_created=True)


def test_add_discount_invalid_date(test_app, view, mock_admin):
    with test_app.test_request_context():
        past_start = datetime.now() - timedelta(days=2)
        past_end = datetime.now() - timedelta(days=1)

        model = Discount(
            code="Expired_Code",
            value=10,
            start_date=past_start,
            end_date=past_end
        )
        with pytest.raises(ValueError, match="không được ở trong quá khứ"):
            view.on_model_change(None, model, is_created=True)


def test_add_discount_quantity_logic(test_app, view, mock_admin):
    with test_app.test_request_context():
        model = Discount(code="Quantity_Code", value=10, min_quantity=10, max_quantity=5,
                         end_date=datetime.now() + timedelta(days=1))
        with pytest.raises(ValueError, match="không được nhỏ hơn tối thiểu"):
            view.on_model_change(None, model, is_created=True)


