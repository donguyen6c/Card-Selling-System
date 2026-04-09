function updateProfile(form) {
    const formData = new FormData(form);

    fetch("/users/current-user", {
        method: "put",
        body: formData
    })
    .then(res => res.json())
    .then(data => {
        document.querySelectorAll('.alert').forEach(el => el.remove());

        form.insertAdjacentHTML('afterbegin', `
            <div class="alert alert-${data.status} alert-dismissible fade show shadow-sm">
                ${data.msg}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            </div>
        `);

        if (data.status === 'success') {
            setTimeout(() => {
                window.location.reload();
            }, 1500);
        }
    })
    .catch(err => alert("Lỗi hệ thống: " + err));
}

document.getElementById('profileForm').onsubmit = function(e) {
    e.preventDefault();
    updateProfile(this);
};