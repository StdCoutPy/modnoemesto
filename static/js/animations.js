// static/js/animations.js

document.addEventListener('DOMContentLoaded', function() {
    console.log('Animations script loaded');

    // Параллакс эффект
    const parallaxItems = document.querySelectorAll('.parallax-item');
    function handleParallax() {
        parallaxItems.forEach(item => {
            const rate = parseFloat(item.getAttribute('data-parallax-rate')) || 0.5;
            const scrollY = window.scrollY;
            item.style.transform = `translateY(${scrollY * rate}px)`;
        });
    }

    // Анимация при скролле
    const animatedElements = document.querySelectorAll('.animate-fadeInUp, .animate-scaleIn, .animate-textReveal');
    function checkScroll() {
        animatedElements.forEach(el => {
            const rect = el.getBoundingClientRect();
            if (rect.top < window.innerHeight * 0.8) {
                el.style.animationPlayState = 'running';
            }
        });
    }

    // Бегущая строка - только если элементы существуют
    const marquee = document.querySelector('.marquee');
    const container = document.querySelector('.marquee-container');

    if (marquee && container) {
        console.log('Marquee element found');
        marquee.style.animation = 'marquee 20s linear infinite';

        container.addEventListener('mouseenter', function() {
            marquee.style.animationPlayState = 'paused';
        });

        container.addEventListener('mouseleave', function() {
            marquee.style.animationPlayState = 'running';
        });
    } else {
        console.log('Marquee elements not found - skipping marquee animation');
    }

    // Инициализация скролла только если есть элементы для анимации
    if (parallaxItems.length > 0 || animatedElements.length > 0) {
        window.addEventListener('scroll', () => {
            if (parallaxItems.length > 0) {
                handleParallax();
            }
            if (animatedElements.length > 0) {
                checkScroll();
            }
        });

        // Инициализация при загрузке
        if (parallaxItems.length > 0) {
            handleParallax();
        }
        if (animatedElements.length > 0) {
            checkScroll();
        }
    }
});