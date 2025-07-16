// 상담 신청 폼 기능 (contact.html에서 작동)
const form = document.getElementById('consultation-form');
if (form) {
    form.addEventListener('submit', async function(event) {
        event.preventDefault();
        const formData = {
            name: document.getElementById('name').value, phone: document.getElementById('phone').value,
            address: document.getElementById('address').value, product: document.getElementById('product').value,
        };
        try {
            const response = await fetch('/submit-consultation', {
                method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(formData),
            });
            const result = await response.json();
            if (result.result === 'success') { window.location.href = '/'; } 
            else { throw new Error('서버 응답이 올바르지 않습니다.'); }
        } catch (error) {
            document.getElementById('form-result').innerHTML = `<div class="alert alert-danger">오류가 발생했습니다.</div>`;
        }
    });
}

// 제품 카테고리 필터링 기능 (index.html에서 작동)
const categoryMenu = document.getElementById('category-menu');
if (categoryMenu) {
    const filterButtons = categoryMenu.querySelectorAll('.filter-btn');
    const productItems = document.querySelectorAll('.product-item');
    filterButtons.forEach(button => {
        button.addEventListener('click', function(event) {
            event.preventDefault();
            filterButtons.forEach(btn => btn.classList.remove('active'));
            this.classList.add('active');
            const filter = this.getAttribute('data-filter');
            productItems.forEach(item => {
                if (filter === 'all' || item.getAttribute('data-category') === filter) {
                    item.style.display = 'block';
                } else {
                    item.style.display = 'none';
                }
            });
        });
    });
}