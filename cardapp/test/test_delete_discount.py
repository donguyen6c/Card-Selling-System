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


def test_delete_discount_already_used(test_app, view, mock_admin):
    with test_app.test_request_context():
        model = Discount(code="USED_CODE", used_count=1)

        with pytest.raises(ValueError, match="TỪ CHỐI XÓA: Mã 'USED_CODE' đã có khách hàng sử dụng"):
            view.on_model_delete(model)


def test_delete_discount_in_history(test_app, view, mock_admin):
    with test_app.test_request_context():
        from unittest.mock import MagicMock
        model = Discount(code="HISTORY_CODE", used_count=0)

        mock_receipt = MagicMock()
        mock_receipt.status.name = 'COMPLETED'
        model.receipts = [mock_receipt]

        with pytest.raises((Exception, ValueError), match="đã được lưu trong lịch sử hóa đơn"):
            view.on_model_delete(model)


def test_delete_discount_pending_order(test_app, view, mock_admin):
    with test_app.test_request_context():
        model = Discount(code="PENDING_CODE", used_count=0)

        from unittest.mock import MagicMock
        mock_receipt = MagicMock()
        mock_receipt.status.name = 'PENDING'
        model.receipts = [mock_receipt]

        with pytest.raises(ValueError, match="đang được áp dụng trong một đơn hàng ĐANG XỬ LÝ"):
            view.on_model_delete(model)


def test_delete_discount_success(test_app, test_session, view, mock_admin):
    with test_app.test_request_context():
        model = Discount(code="CLEAN_CODE", used_count=0)
        model.receipts = []
        try:
            view.on_model_delete(model)
        except Exception as e:
            pytest.fail(f"Không nên báo lỗi khi xóa mã sạch: {e}")