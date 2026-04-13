// Улучшенный скрипт для работы с корзиной
document.addEventListener('DOMContentLoaded', function() {
    // Авто-отправка формы при изменении количества
    const quantityInputs = document.querySelectorAll('.quantity-input');
    quantityInputs.forEach(input => {
        input.addEventListener('change', function() {
            const form = this.closest('form');
            if (form) {
                form.submit();
            }
        });
    });
document.addEventListener('DOMContentLoaded', function() {
    // Обработка удаления с подтверждением
    const removeForms = document.querySelectorAll('.remove-form');

    removeForms.forEach(form => {
        form.addEventListener('submit', function(e) {
            if (!confirm('Вы уверены, что хотите удалить товар из корзины?')) {
                e.preventDefault();
            }
        });
    });

    // Обработка обновления количества с AJAX (опционально)
    const updateForms = document.querySelectorAll('.update-form');

    updateForms.forEach(form => {
        const quantityInput = form.querySelector('.quantity-input');

        quantityInput.addEventListener('change', function() {
            const value = parseInt(this.value);
            if (value < 1) {
                this.value = 1;
            } else if (value > 99) {
                this.value = 99;
            }
        });
    });
});

    // Функция для обновления счетчика корзины в шапке
    function updateCartCounter(count) {
        const cartCounter = document.querySelector('.cart-counter');
        const cartLink = document.querySelector('.cart-link');

        if (cartCounter) {
            if (count > 0) {
                cartCounter.textContent = count;
                cartCounter.style.display = 'flex';
            } else {
                cartCounter.style.display = 'none';
            }
        }

        // Если счетчика нет, но есть корзина с товарами - создаем его
        if (!cartCounter && count > 0 && cartLink) {
            const newCounter = document.createElement('span');
            newCounter.className = 'cart-counter';
            newCounter.textContent = count;
            cartLink.appendChild(newCounter);
        }
    }

    // Проверяем начальное состояние счетчика
    const initialCount = document.querySelector('.cart-counter')?.textContent || 0;
    updateCartCounter(parseInt(initialCount));
});