import pytest
from unittest.mock import patch
from cardapp.models import Discount, User, UserRole, Receipt, ReceiptStatus
from cardapp.admin import DiscountView
from cardapp import db
from cardapp.test.test_base import test_app, test_session


@pytest.fixture
def view(test_session):
    return DiscountView(Discount, test_session)


@pytest.fixture
def mock_admin():
    admin = User(username="admin", user_role=UserRole.ADMIN)
    with patch('flask_login.utils._get_user', return_value=admin):
        yield admin


@pytest.fixture
def sample_user(test_session):
    u = User(username="buyer", password="123", email="buyer@gmail.com")
    test_session.add(u)
    test_session.commit()
    return u


def test_delete_discount_already_used(test_app, test_session, view, mock_admin):
    with test_app.test_request_context():
        d = Discount(code="USED_CODE", used_count=1)
        test_session.add(d)
        test_session.commit()

        with pytest.raises(ValueError, match="TỪ CHỐI XÓA: Mã 'USED_CODE' đã có khách hàng sử dụng"):
            view.on_model_delete(d)


def test_delete_discount_in_history(test_app, test_session, view, mock_admin, sample_user):
    with test_app.test_request_context():
        d = Discount(code="HISTORY_CODE", used_count=0)
        test_session.add(d)
        test_session.commit()

        r = Receipt(
            user_id=sample_user.id,
            total_amount=100000,
            final_amount=100000,
            status=ReceiptStatus.PAID,
            discount_id=d.id
        )
        test_session.add(r)
        test_session.commit()

        with pytest.raises((Exception, ValueError), match="đã được lưu trong lịch sử hóa đơn"):
            view.on_model_delete(d)


def test_delete_discount_pending_order(test_app, test_session, view, mock_admin, sample_user):
    with test_app.test_request_context():
        d = Discount(code="PENDING_CODE", used_count=0)
        test_session.add(d)
        test_session.commit()

        r = Receipt(
            user_id=sample_user.id,
            total_amount=100000,
            final_amount=100000,
            status=ReceiptStatus.PENDING,
            discount_id=d.id
        )
        test_session.add(r)
        test_session.commit()

        with pytest.raises(ValueError, match="đang được áp dụng trong một đơn hàng ĐANG XỬ LÝ"):
            view.on_model_delete(d)


def test_delete_discount_success(test_app, test_session, view, mock_admin):
    with test_app.test_request_context():
        d = Discount(code="CLEAN_CODE", used_count=0)
        test_session.add(d)
        test_session.commit()

        view.on_model_delete(d)