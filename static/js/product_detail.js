document.addEventListener('DOMContentLoaded', () => {

const mainImage = document.getElementById('mainImage');
if (!mainImage) return;

const thumbs = document.querySelectorAll('.thumb');
const prev = document.querySelector('.prev');
const next = document.querySelector('.next');

let images = Array.from(thumbs).map(t => t.dataset.full);
let index = 0;

/* thumbnails */
thumbs.forEach((thumb, i) => {
    thumb.addEventListener('click', () => {
        index = i;
        mainImage.src = images[index];
        setActive();
    });
});

function setActive() {
    thumbs.forEach(t => t.classList.remove('active'));
    if (thumbs[index]) thumbs[index].classList.add('active');
}

/* arrows */
if (prev && next) {
    prev.addEventListener('click', () => {
        index = (index - 1 + images.length) % images.length;
        mainImage.src = images[index];
        setActive();
    });

    next.addEventListener('click', () => {
        index = (index + 1) % images.length;
        mainImage.src = images[index];
        setActive();
    });
}

/* zoom only for desktop */
if (window.matchMedia('(hover: hover)').matches) {
    mainImage.addEventListener('mousemove', e => {
        const rect = mainImage.getBoundingClientRect();
        const x = ((e.clientX - rect.left) / rect.width) * 100;
        const y = ((e.clientY - rect.top) / rect.height) * 100;
        mainImage.style.transformOrigin = `${x}% ${y}%`;
        mainImage.style.transform = 'scale(2)';
    });

    mainImage.addEventListener('mouseleave', () => {
        mainImage.style.transform = 'scale(1)';
    });
}


/* ===== ADD TO CART ===== */
const form = document.getElementById('addToCartForm');
const btn = document.getElementById('addToCartBtn');
const msg = document.getElementById('cartMessage');
const sizes = document.querySelectorAll('input[name="size"]');

btn.disabled = false;

if (sizes.length) {
    btn.disabled = true;
    sizes.forEach(r => r.addEventListener('change', () => btn.disabled = false));
}

form.addEventListener('submit', e => {
    e.preventDefault();

    const data = new FormData(form);

    fetch(form.action, {
        method: 'POST',
        headers: {
            'X-Requested-With': 'XMLHttpRequest',
            'X-CSRFToken': data.get('csrfmiddlewaretoken')
        },
        body: data
    })
    .then(r => r.json())
    .then(j => {
        msg.innerHTML = j.success
            ? `<span class="ok">${j.message}</span>`
            : `<span class="err">${j.error}</span>`;
    });
});

});

// Добавьте это в product_detail.js после загрузки DOM

// Свайп для мобильных устройств
let touchStartX = 0;
let touchEndX = 0;

const gallery = document.querySelector('.product-gallery');
if (gallery) {
    gallery.addEventListener('touchstart', e => {
        touchStartX = e.changedTouches[0].screenX;
    });

    gallery.addEventListener('touchend', e => {
        touchEndX = e.changedTouches[0].screenX;
        handleSwipe();
    });
}

function handleSwipe() {
    const swipeThreshold = 50;

    if (touchStartX - touchEndX > swipeThreshold) {
        // Свайп влево - следующий слайд
        if (next) next.click();
    }

    if (touchEndX - touchStartX > swipeThreshold) {
        // Свайп вправо - предыдущий слайд
        if (prev) prev.click();
    }
}

// Отключаем зум на мобильных
if ('ontouchstart' in window) {
    mainImage.style.cursor = 'default';
    mainImage.removeEventListener('mousemove', null);
    mainImage.removeEventListener('mouseleave', null);
}
