let currentDiscount = 0;

document.addEventListener('DOMContentLoaded', function() {
    const imgMomo = document.getElementById('qr-momo');
    const imgBanking = document.getElementById('qr-banking');

    const radios = document.querySelectorAll('input[name="payment_method"]');

    radios.forEach(radio => {
        radio.addEventListener('change', function() {
            if (this.value === 'momo') {
                imgMomo.classList.remove('d-none');
                imgBanking.classList.add('d-none');
            }
            else if (this.value === 'banking') {
                imgBanking.classList.remove('d-none');
                imgMomo.classList.add('d-none');
            }
        });
    });
});

function applyDiscount() {
    const code = document.getElementById('discount-code').value.trim();
    const msgBox = document.getElementById('discount-msg');

    if (code === "") {
        msgBox.innerHTML = "<span class='text-danger'>Vui lòng nhập mã giảm giá!</span>";
        return;
    }

    fetch('/pay/discount', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ code: code })
    })
    .then(res => res.json())
    .then(data => {
        if (data.status === 'success') {
            msgBox.innerHTML = `<span class='text-success'>${data.message}</span>`;
            currentDiscount = data.discount_amount;
            updateFinalAmount();
        } else {
            msgBox.innerHTML = `<span class='text-danger'>${data.message}</span>`;
            currentDiscount = 0;
            updateFinalAmount();
        }
    })
    .catch(err => console.error(err));
}

function updateFinalAmount() {
    let subtotalStr = document.getElementById('subtotal').innerText.replace(/\./g, '').replace(/,/g, '');
    let subtotal = parseFloat(subtotalStr) || 0;

    let finalAmount = subtotal - currentDiscount;
    if (finalAmount < 0) finalAmount = 0;

    document.getElementById('discount-amount').innerText = currentDiscount.toLocaleString('vi-VN');
    document.getElementById('final-amount').innerText = finalAmount.toLocaleString('vi-VN');
}

function pay() {
    // 1. Lấy dữ liệu
    const paymentMethodInput = document.querySelector('input[name="payment_method"]:checked');
    const paymentMethod = paymentMethodInput ? paymentMethodInput.value : 'qr_code';

    const discountCodeInput = document.getElementById('discount-code');
    const discountCode = discountCodeInput ? discountCodeInput.value.trim() : '';

    // Lấy ID của nút thanh toán (Bạn nhớ đổi 'btn-pay' thành id thật trong HTML của bạn nhé)
    const payBtn = document.getElementById('btn-pay');

    // 2. Khóa nút bấm để tránh spam click tạo nhiều đơn hàng
    if (payBtn) {
        payBtn.disabled = true;
        payBtn.innerHTML = '<span class="spinner-border spinner-border-sm"></span> Đang xử lý...';
    }

    // 3. Gọi API tạo đơn hàng
    fetch('/pay', { // Đường dẫn API mà bạn vừa cấu hình bên backend
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            payment_method: paymentMethod,
            discount_code: discountCode
        })
    })
    .then(res => res.json())
    .then(data => {
        if (data.status === 'success') {
            if (data.redirect_url) {
                window.location.href = data.redirect_url;
            } else {
                alert("Lỗi: Không tìm thấy đường dẫn thanh toán!");
            }
        } else {
            alert("Lỗi thanh toán: " + data.message);

            if (payBtn) {
                payBtn.disabled = false;
                payBtn.innerHTML = 'XÁC NHẬN THANH TOÁN';
            }
        }
    })
    .catch(err => {
        console.error("Lỗi Fetch:", err);
        alert("Có lỗi kết nối mạng. Vui lòng thử lại!");

        if (payBtn) {
            payBtn.disabled = false;
            payBtn.innerHTML = 'XÁC NHẬN THANH TOÁN';
        }
    });
}