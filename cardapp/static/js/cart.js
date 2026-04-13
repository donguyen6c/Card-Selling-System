function getTierLimit(price) {
    if (price <= 30000) return 10;
    if (price <= 300000) return 5;
    return 3;
}

function changeQuantity(id, step, price) {
    let inputObj = document.getElementById(`qty-${id}`);
    let currentQty = parseInt(inputObj.value);
    let newQty = currentQty + step;

    let limit = getTierLimit(price);

    if (newQty < 1) return;

    if (newQty > limit) {
        alert(`Mệnh giá này chỉ được mua tối đa ${limit} thẻ mỗi đơn!`);
        return;
    }

    inputObj.value = newQty;
    updateCart(id, inputObj, price);
}

function updateCart(id, obj, price) {
    let newQty = parseInt(obj.value);
    let limit = getTierLimit(price);

    if (isNaN(newQty) || newQty < 1) {
        alert("Số lượng không hợp lệ!");
        location.reload();
        return;
    }

    fetch(`/carts/items/${id}`, {
        method: "patch",
        body: JSON.stringify({ "quantity": newQty, "price": price }),
        headers: { "Content-Type": "application/json" }
    }).then(res => res.json()).then(data => {
        if (data.status === "error") {
            alert(data.message);
            location.reload();
        } else {
            let counters = document.getElementsByClassName("cart-counter");
            for (let c of counters) c.innerText = data.total_quantity;

            let amounts = document.getElementsByClassName("cart-amount");
            for (let a of amounts) a.innerText = data.total_amount.toLocaleString("vi-VN");

            let btnPlus = document.getElementById(`btn-plus-${id}`);
            if (btnPlus) {
                if (newQty >= limit) {
                    btnPlus.disabled = true;
                } else {
                    btnPlus.disabled = false;
                }
            }
        }
    }).catch(err => {
        console.error(err);
        alert("Có lỗi xảy ra, vui lòng thử lại!");
        location.reload();
    });
}

function deleteCart(product_id) {
    if(confirm("Bạn có chắc chắn muốn xóa thẻ này khỏi giỏ?")) {
        fetch(`/carts/items/${product_id}`, { method: "delete" })
        .then(res => {
            if (!res.ok) throw new Error("Request failed");
            return res.json();
        })
        .then(data => {
            document.getElementById(`cart${product_id}`).style.display = "none";
            let counters = document.getElementsByClassName("cart-counter");
            for (let c of counters) c.innerText = data.total_quantity;

            let amounts = document.getElementsByClassName("cart-amount");
            for (let a of amounts) a.innerText = data.total_amount.toLocaleString("vi-VN");

            if (data.total_quantity === 0) location.reload();
        })
        .catch(err => {
            console.error(err);
            alert("Có lỗi xảy ra, vui lòng thử lại!")
        })
    }
}