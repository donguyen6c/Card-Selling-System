from flask_admin import Admin, AdminIndexView, BaseView, expose
from flask_admin.contrib.sqla import ModelView
from flask_login import current_user, logout_user
from flask import redirect, flash
from wtforms import FileField
from datetime import datetime
from cardapp.models import Category, Product, Card, User, Receipt, Discount, Banner, UserRole, DiscountType
from cardapp import app, db
import cardapp.dao as dao
import cloudinary.uploader

class AdminModelView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.user_role == UserRole.ADMIN


class CardView(AdminModelView):
    column_list = ['product', 'serial_number', 'pin_code', 'expiry_date', 'is_sold']
    column_searchable_list = ['serial_number', 'pin_code']
    column_filters = ['is_sold', 'expiry_date']
    page_size = 50

    column_labels = {
        'product': 'Tên sản phẩm',
        'serial_number': 'Số Serial',
        'pin_code': 'Mã PIN',
        'expiry_date': 'Hạn sử dụng',
        'is_sold': 'Trạng thái bán'
    }

    column_formatters = {
        'is_sold': lambda v, c, m, p: "Đã bán" if m.is_sold else "Chưa bán"
    }

    def on_model_change(self, form, model, is_created):
        if is_created and not model.is_sold:
            model.product.inventory += 1

    def on_model_delete(self, model):
        if not model.is_sold:
            model.product.inventory -= 1


class DiscountView(AdminModelView):
    column_labels = {
        'code': 'Mã giảm giá',
        'description': 'Mô tả',
        'discount_type': 'Loại giảm',
        'value': 'Giá trị',
        'applied_card_type': 'Loại thẻ áp dụng',
        'start_date': 'Ngày bắt đầu',
        'end_date': 'Ngày kết thúc',
        'min_quantity': 'SL mua tối thiểu',
        'max_quantity': 'SL mua tối đa',
        'usage_limit': 'Giới hạn lượt dùng',
        'used_count': 'Đã dùng'
    }

    form_excluded_columns = ['receipts']

    form_args = {
        'applied_card_type': {
            'allow_blank': True,
            'blank_text': 'Tất cả'
        }
    }

    form_widget_args = {
        'used_count': {
            'readonly': True
        }
    }

    def handle_view_exception(self, exc):
        if isinstance(exc, ValueError):
            flash(str(exc), 'error')
            return True
        return super(DiscountView, self).handle_view_exception(exc)

    def on_model_change(self, form, model, is_created):
        if current_user.user_role != UserRole.ADMIN:
            raise ValueError("LỖI BẢO MẬT: Chỉ Admin mới có quyền thao tác mã giảm giá!")

        existing = db.session.query(Discount).filter_by(code=model.code).first()

        if existing and (existing is not model):

            if model.id is None or existing.id != model.id:
                raise ValueError(f"LỖI: Mã giảm giá '{model.code}' đã tồn tại!")

        start = model.start_date if model.start_date else datetime.now()
        if model.end_date:
            if model.end_date <= start:
                raise ValueError("LỖI: Ngày kết thúc phải lớn hơn ngày bắt đầu!")
            if model.end_date.date() < datetime.now().date():
                raise ValueError("LỖI: Ngày kết thúc không được ở trong quá khứ!")

        discount_type_name = str(
            model.discount_type.name if hasattr(model.discount_type, 'name') else model.discount_type)
        if "PERCENTAGE" in discount_type_name:
            val = float(model.value)
            if val <= 0 or val > 50:
                raise ValueError("LỖI: Mức giảm phần trăm (%) phải lớn hơn 0 và không vượt quá 50%!")
        else:
            if float(model.value) <= 0:
                raise ValueError("LỖI: Giá trị giảm giá phải lớn hơn 0 VNĐ!")

        start = model.start_date if model.start_date else datetime.now()
        if model.end_date:
            if model.end_date <= start:
                raise ValueError("LỖI: Ngày kết thúc phải sau ngày bắt đầu!")
            if model.end_date.date() < datetime.now().date():
                raise ValueError("LỖI: Không được tạo mã hết hạn trong quá khứ!")

        if model.min_quantity < 1:
            raise ValueError("LỖI: Số lượng mua tối thiểu ít nhất là 1!")

        if model.max_quantity and model.max_quantity < model.min_quantity:
            raise ValueError("LỖI: Số lượng tối đa không được nhỏ hơn tối thiểu!")

        if model.usage_limit is not None and model.usage_limit < 1:
            raise ValueError("LỖI: Giới hạn lượt dùng của mã (Usage Limit) phải lớn hơn 0!")

    def on_model_delete(self, model):
        if model.used_count > 0:
            raise ValueError(
                f"TỪ CHỐI XÓA: Mã '{model.code}' đã có khách hàng sử dụng ({model.used_count} lần). Hãy sửa 'Ngày kết thúc' về quá khứ để vô hiệu hóa mã này thay vì xóa!")

        if len(model.receipts) > 0:
            has_pending = any(r.status.name == 'PENDING' for r in model.receipts if hasattr(r, 'status'))

            if has_pending:
                raise ValueError(f"TỪ CHỐI XÓA: Mã '{model.code}' đang được áp dụng trong một đơn hàng ĐANG XỬ LÝ!")
            else:
                raise ValueError(
                    f"TỪ CHỐI XÓA: Mã '{model.code}' đã được lưu trong lịch sử hóa đơn. Vui lòng giữ lại để đối soát!")

class BannerView(AdminModelView):
    form_extra_fields = {
        'image_file': FileField('Tải ảnh Banner')
    }

    form_excluded_columns = ['image_url']

    def on_model_change(self, form, model, is_created):
        avatar = form.image_file.data

        if avatar:
            res = cloudinary.uploader.upload(avatar)
            model.image_url = res.get("secure_url")


class MyAdminIndexView(AdminIndexView):
    @expose('/')
    def index(self, **kwargs):
        return self.render('admin/index.html', cate_stats=dao.count_product_by_cate())

    def is_accessible(self):
        return current_user.is_authenticated and current_user.user_role == UserRole.ADMIN


class StatsView(BaseView):
    @expose('/')
    def index(self):
        return self.render('admin/stats.html',
                           revenue_products=dao.revenue_by_product(),
                           revenue_times=dao.revenue_by_time("month"))

    def is_accessible(self):
        return current_user.is_authenticated and current_user.user_role == UserRole.ADMIN


class LogoutView(BaseView):
    @expose('/')
    def index(self):
        logout_user()
        return redirect('/login')

    def is_accessible(self):
        return current_user.is_authenticated


class UserView(AdminModelView):
    column_labels = {
        'name': 'Họ tên',
        'avatar': 'Ảnh đại diện',
        'username': 'Tên đăng nhập',
        'email': 'Email',
        'password': 'Mật khẩu',
        'user_role': 'Vai trò (Quyền)'
    }

    column_list = ['id', 'name', 'username', 'email', 'user_role']
    column_searchable_list = ['name', 'username', 'email']
    column_filters = ['user_role']

    form_excluded_columns = ['receipts']

    def on_model_delete(self, model):
        if model.receipts and len(model.receipts) > 0:
            raise ValueError(
                f"TỪ CHỐI XÓA: Tài khoản '{model.username}' đã có {len(model.receipts)} hóa đơn. Hãy vô hiệu hóa thay vì xóa!")


class ReceiptView(AdminModelView):
    column_labels = {
        'id': 'Mã hóa đơn',
        'user': 'Khách hàng',
        'created_date': 'Ngày thanh toán',
        'total_amount': 'Tổng tiền gốc',
        'final_amount': 'Số tiền thực thu',
        'discount_applied': 'Mã giảm giá'
    }

    column_list = ['id', 'user', 'total_amount', 'final_amount', 'created_date']

    can_create = False
    can_edit = False
    can_delete = False

    column_filters = ['created_date', 'user.username']
    column_searchable_list = ['id']
    column_default_sort = ('created_date', True)


admin = Admin(app=app, name="Quản Trị Bán Thẻ", index_view=MyAdminIndexView())

admin.add_view(AdminModelView(Category, db.session, name="Nhà mạng"))
admin.add_view(AdminModelView(Product, db.session, name="Mệnh giá thẻ"))
admin.add_view(CardView(Card, db.session, name="Kho thẻ"))
admin.add_view(DiscountView(Discount, db.session, name="Khuyến mãi"))
admin.add_view(BannerView(Banner, db.session, name="Banner"))
admin.add_view(ReceiptView(Receipt, db.session, name="Lịch sử Hóa đơn"))
admin.add_view(UserView(User, db.session, name="Tài khoản người dùng"))
admin.add_view(StatsView(name='Thống kê & Báo cáo'))
admin.add_view(LogoutView(name='Đăng xuất'))
