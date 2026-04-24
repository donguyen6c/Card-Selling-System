from datetime import datetime

from cardapp import utils, db
from cardapp.models import Receipt, ReceiptDetails, Discount, Card, DiscountType

def check_discount(code, cart):
    fail_res = {'success': False, 'discount_amount': 0, 'message': "", 'discount_id': None}

    if not cart:
        fail_res['message'] = "Giỏ hàng rỗng!"
        return fail_res

    discount = Discount.query.filter(Discount.code == code, Discount.active == True).first()
    if not discount:
        fail_res['message'] = "Mã giảm giá không tồn tại!"
        return fail_res

    if discount.usage_limit is not None:
        if discount.used_count >= discount.usage_limit:
            fail_res['message'] = f"Mã này đã hết lượt sử dụng (Giới hạn: {discount.usage_limit} lần)!"
            return fail_res

    now = datetime.now()
    if now < discount.start_date or now > discount.end_date:
        fail_res['message'] = "Mã giảm giá đã hết hạn!"
        return fail_res

    stats = utils.stats_cart(cart)
    applicable_qty = 0
    applicable_amount = 0

    if discount.applied_card_type:
        target_type = discount.applied_card_type.value if hasattr(discount.applied_card_type, 'value') else str(
            discount.applied_card_type)
        target_type = str(target_type).lower()

        if 'phone' in target_type:
            target_type = 'phone'
        elif 'game' in target_type:
            target_type = 'game'

        if target_type == 'game':
            applicable_qty = stats.get('game_quantity', 0)
            applicable_amount = sum([c['price'] * c['quantity'] for c in cart.values() if c.get('card_type') == 'game'])
        elif target_type == 'phone':
            applicable_qty = stats.get('phone_quantity', 0)
            applicable_amount = sum(
                [c['price'] * c['quantity'] for c in cart.values() if c.get('card_type') == 'phone'])

        if applicable_qty == 0:
            fail_res['message'] = f"Mã này chỉ áp dụng cho thẻ {target_type.upper()}!"
            return fail_res
    else:
        applicable_qty = stats.get('total_quantity', 0)
        applicable_amount = stats.get('total_amount', 0)

    if applicable_qty < discount.min_quantity:
        fail_res['message'] = f"Cần mua ít nhất {discount.min_quantity} thẻ để áp dụng mã!"
        return fail_res

    if discount.max_quantity and applicable_qty > discount.max_quantity:
        fail_res['message'] = f"Mã này chỉ áp dụng khi mua tối đa {discount.max_quantity} thẻ!"
        return fail_res

    if discount.discount_type == DiscountType.PERCENTAGE:
        discount_amount = applicable_amount * (discount.value / 100)
    else:
        discount_amount = discount.value

    discount_amount = min(discount_amount, applicable_amount)

    return {
        'success': True,
        'discount_amount': discount_amount,
        'message': "Áp dụng mã giảm giá thành công!",
        'discount_id': discount.id
    }

def load_discounts():
    return Discount.query.filter(Discount.active == True).all()

