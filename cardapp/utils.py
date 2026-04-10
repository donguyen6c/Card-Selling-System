import dns.resolver
import re


def validate_email_domain(email):
    email = email.strip()
    regex = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    if not email or not re.match(regex, email):
        raise ValueError("Email không đúng định dạng!")

    domain = email.split('@')[-1]
    try:
        dns.resolver.resolve(domain, 'MX')
    except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer):
        raise ValueError(f"Tên miền email '@{domain}' không tồn tại!")
    except Exception:
        pass

    return email

def stats_cart(cart):
    total_quantity, total_amount = 0, 0
    game_quantity, phone_quantity = 0, 0

    if cart:
        for c in cart.values():
            qty = c['quantity']
            price = c['price']
            card_type = c.get('card_type')

            total_quantity += qty
            total_amount += qty * price

            if card_type == 'game':
                game_quantity += qty
            elif card_type == 'phone':
                phone_quantity += qty

    return {
        'total_quantity': total_quantity,
        'total_amount': total_amount,
        'game_quantity': game_quantity,
        'phone_quantity': phone_quantity
    }

def get_tier_limit(p):
    if p <= 30000:
        return 10
    elif p <= 300000:
        return 5
    else:
        return 3