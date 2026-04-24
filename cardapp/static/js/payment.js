let timeLeft = parseInt(window.INITIAL_TIME_LEFT);
const timerDisplay = document.getElementById('timer');

const countdown = setInterval(() => {
    let minutes = Math.floor(timeLeft / 60);
    let seconds = timeLeft % 60;

    timerDisplay.innerHTML = `${minutes < 10 ? '0' : ''}${minutes}:${seconds < 10 ? '0' : ''}${seconds}`;

    if (timeLeft <= 0) {
        clearInterval(countdown);
        alert("Đã hết thời gian thanh toán. Đơn hàng của bạn đã bị hủy!");
        window.location.href = "/cart";
    }
    timeLeft--;
}, 1000);

const btnConfirmPay = document.getElementById('btn-confirm-pay');
if (btnConfirmPay) {
    btnConfirmPay.addEventListener('click', function() {

        this.disabled = true;
        this.innerHTML = '<span class="spinner-border spinner-border-sm me-1"></span> Đang xử lý...';

        fetch('/payment', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        })
        .then(res => res.json())
        .then(data => {
            if (data.status === 'success') {
                clearInterval(countdown);

                alert(data.message);
                window.location.href = "/";
            } else {
                alert(data.message);
                this.disabled = false;
                this.innerHTML = '<i class="fas fa-check-circle me-1"></i> XÁC NHẬN ĐÃ CHUYỂN KHOẢN';
            }
        })
        .catch(err => {
            console.error(err);
            alert("Lỗi kết nối mạng!");
            this.disabled = false;
            this.innerHTML = '<i class="fas fa-check-circle me-1"></i> XÁC NHẬN ĐÃ CHUYỂN KHOẢN';
        });
    });
}