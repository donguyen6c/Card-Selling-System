import pytest
from unittest.mock import patch
from datetime import datetime, timedelta
from cardapp.models import Discount, User, UserRole
from cardapp.admin import DiscountView
from cardapp import db
from cardapp.test.test_base import test_app, test_session
from unittest.mock import MagicMock

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
    user = User(username="username123", user_role=UserRole.USER)
    with patch('flask_login.utils._get_user', return_value=user):
        yield user


def test_delete_discount_already_used(test_app, view, mock_admin):
    with test_app.test_request_context():
        model = Discount(code="USED_CODE", used_count=1)

        with pytest.raises(ValueError, match="TỪ CHỐI XÓA: Mã 'USED_CODE' đã có khách hàng sử dụng"):
            view.on_model_delete(model)


def test_delete_discount_in_history(test_app, view, mock_admin):
    with test_app.test_request_context():

        model = Discount(code="HISTORY_CODE", used_count=0)

        mock_receipt = MagicMock()
        mock_receipt.status.name = 'COMPLETED'
        model.receipts = [mock_receipt]

        with pytest.raises((Exception, ValueError), match="đã được lưu trong lịch sử hóa đơn"):
            view.on_model_delete(model)


def test_delete_discount_pending_order(test_app, view, mock_admin):
    with test_app.test_request_context():
        model = Discount(code="PENDING_CODE", used_count=0)

        mock_receipt = MagicMock()
        mock_receipt.status.name = 'PENDING'
        model.receipts = [mock_receipt]

        with pytest.raises(ValueError, match="đang được áp dụng trong một đơn hàng ĐANG XỬ LÝ"):
            view.on_model_delete(model)


def test_delete_discount_success(test_app, test_session, view, mock_admin):
    with test_app.test_request_context():
        model = Discount(code="CLEAN_CODE", used_count=0)
        model.receipts = []
        view.on_model_delete(model)

def test_delete_discount_not_admin(test_app, view, mock_user):
    with test_app.test_request_context():
        model = Discount(code="SOME_CODE", used_count=0)
        model.receipts = []

        with pytest.raises(ValueError, match="LỖI BẢO MẬT"): view.on_model_delete(model)