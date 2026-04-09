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