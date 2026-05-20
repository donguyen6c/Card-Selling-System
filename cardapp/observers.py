import threading
from flask_mail import Message
from cardapp import app, mail
from cardapp.models import User


class PaymentSubject:
    def __init__(self):
        self._observers = []

    def attach(self, observer):
        if observer not in self._observers:
            self._observers.append(observer)

    def notify(self, user_id, cart, final_amount, payment_method):
        for observer in self._observers:
            observer.update(user_id, cart, final_amount, payment_method)


class Observer:
    def update(self, user_id, cart, final_amount, payment_method):
        pass


class EmailNotificationObserver(Observer):
    def update(self, user_id, cart, final_amount, payment_method):
        thread = threading.Thread(
            target=self.send_mail,
            kwargs={
                'user_id': user_id,
                'cart': cart,
                'final_amount': final_amount,
                'payment_method': payment_method
            }
        )
        thread.start()

    def send_mail(self, user_id, cart, final_amount, payment_method):
        with app.app_context():
            user = User.query.get(user_id)
            if not user or not user.email:
                return

            msg = Message("Xác nhận thanh toán thành công - CaoThe", recipients=[user.email])
            pay_method_str = 'Ví MoMo' if payment_method == 'momo' else 'Ngân hàng'

            body = f"Chào {user.name}, đơn hàng của bạn đã được thanh toán thành công qua {pay_method_str}.\n\n"
            body += "CHI TIẾT THẺ ĐÃ MUA:\n"

            for item in cart.values():
                item_total = item['price'] * item['quantity']
                body += f"- {item['name']} | Số lượng: {item['quantity']} | Thành tiền: {item_total:,.0f} đ\n"

            body += f"\nTỔNG THANH TOÁN: {final_amount:,.0f} VNĐ\n"
            body += "\nTrạng thái: Đã thanh toán."
            body += "\nMã thẻ (Số seri & Mã nạp) đã được cập nhật. Vui lòng đăng nhập và kiểm tra mục Lịch sử mua hàng trên website nhé!"

            msg.body = body

            mail.send(msg)