# 👗 Modnoe Mesto — Senior-Grade AI E-commerce Ecosystem

![Python](https://shields.io)
![Django](https://shields.io)
![Docker](https://shields.io)
![Security](https://shields.io)

**Modnoe Mesto** — это полнофункциональная экосистема для e-commerce, разработанная с нуля. Проект демонстрирует архитектурный подход Senior-уровня: от кастомного дизайна до сложной инфраструктуры с интеграцией нейросетей, автоматизированным парсингом и высокой степенью защиты.

## 🚀 Live Demo & Production
*   **Domain:** [https://modnoemesto.asia](https://modnoemesto.asia)
*   **Infrastructure:** Собственный VPS (Ubuntu 24.04), Docker, Nginx, SSL (Let's Encrypt).
*   **PWA Ready:** Сайт полностью оптимизирован для работы в Safari/Chrome как нативное приложение с кастомными иконками и манифестом.

## 🛡 Безопасность и Авторизация (Advanced Auth)
*   **Multi-level Auth:** Реализована классическая авторизация (Email/Password) с дополнением в виде **2FA**.
*   **Telegram Integration:** Бесшовная авторизация через Telegram API и привязка аккаунтов.
*   **Security Hardening:** Защита от CSRF-атак, скрытие окружения через `.env`, работа через защищенный Reverse Proxy (Nginx).
*   **Automated Cleanup:** Management-команда `clear_unverified_users` для автоматической очистки БД от неавторизованных сессий.

## 🤖 AI-Инфраструктура (Fashion Tech)
*   **Multi-Model Assistant:** Кастомный ИИ-стилист, работающий на базе агрегатора из **9 нейросетей** (OpenAI, Gemini и др.).
*   **Smart Consulting:** Бот консультирует по трендам, помогает в выборе размеров и создании образов на основе текущего каталога.
*   **Freedom API Integration:** Временная страница оплаты.

## 🦾 Автоматизация и Парсинг (Custom Management Commands)
Проект содержит мощный инструментарий для автоматизации контента, написанный на уровне системного инжиниринга:
*   **Pinterest/Google Deep Scraper:** Скрипты парсинга лукбуков через имитацию сессий и обход авторизации. Работает даже с закрытыми профилями.
*   **Auto-Cleaning:** Алгоритм автоматической очистки БД от некачественных изображений в Lookbooks.
*   **Content Seeding:** Набор команд для быстрого развертывания витрины: `fill_categories`, `add_sizes`, `delete_categories`.
*   **Background Tasks:** Команда `run_tg_bot` запускает асинхронного Telegram-бота для связи сайта и мессенджера в реальном времени.

## 📈 Маркетинг и CRM-логика
*   **Promo Code System:** Полноценная логика промокодов. Применение скидок в корзине с валидацией по сессиям и пользователям.
*   **Email Automation:** 
    *   Приветственные письма после регистрации с уникальным купоном на первую покупку.
    *   Транзакционные уведомления: отправка деталей заказа и чеков сразу после покупки.
    *   Интеграция с SMTP для надежной доставки сообщений.

## 🏗 Архитектура и Clean Code
Проект построен по принципам модульности и высокой читаемости:
*   **Custom Admin UI:** Использование Jazzmin и кастомных переопределений для удобного управления магазином.
*   **Logic Isolation:** Весь бизнес-функционал вынесен в `utils.py`, `context_processors` и кастомные теги.
*   **Frontend Mastery:** Дизайн с нуля. Адаптивность, использование SVG, тонкая настройка Favicons для iOS/Android.
*   **API First:** Интеграция с TG API, AI API и Freedom API (Paybox) через защищенные методы обработки запросов.

## 📂 Структура проекта (Project Tree)

Архитектура организована профессионально: логика разделена по приложениям, а системные файлы вынесены в корень для удобного управления Docker-окружением.

*   **`chat/`** — Модуль AI-ассистента на базе 9+ нейросетей (OpenAI, Gemini и др.).
*   **`content/`** — Управление динамическим контентом и Lookbooks.
*   **`DjangoProject/`** — Ядро проекта: настройки (`settings.py`), маршрутизация и WSGI/ASGI конфиги.
*   **`main/`** — Основная бизнес-логика, главная страница и базовые шаблоны.
*   **`orders/`** — Система заказов и интеграция с Freedom API (Paybox).
*   **`products/`** — Каталог товаров, управление размерами, категориями и фильтрацией.
*   **`users/`** — Кастомная модель пользователя, система 2FA, регистрация и Email-рассылки.
*   **`static/` & `media/`** — Директории для хранения исходной статики и загружаемого контента.
*   **`templates/`** — Общие HTML-шаблоны с использованием Django Template Language.
*   **`manage.py`** — Точка входа для управления проектом и запуска кастомных команд парсинга.
*   **`docker-compose.yml` & `Dockerfile`** — Конфигурация для мгновенного деплоя в Production.
*   **`.env`** — Файл переменных окружения (API keys, DB creds) — **не для GitHub**.

## 🛠 Команды управления (CLI)

Проект оснащен мощным инструментарием автоматизации, реализованным через кастомные `management commands`. Это позволяет управлять магазином на уровне Senior-разработчика, минимизируя ручной ввод данных:

```bash
# --- Наполнение и управление каталогом ---
python manage.py fill_categories   # Автоматическая генерация структуры категорий
python manage.py add_sizes         # Массовое создание размерной сетки (S, M, L, XL и т.д.)
python manage.py delete_categories  # Полная очистка дерева категорий (Hard Reset)

# --- Интеллектуальный парсинг и AI ---
python manage.py parse_pinterest   # Глубокий скрапинг через сессии (даже для закрытых разделов)
python manage.py clean_lookbooks   # AI-анализ фото: автоудаление некачественного контента из БД

# --- Системные сервисы и безопасность ---
python manage.py run_tg_bot        # Запуск асинхронного Telegram-бота для связи с API
python manage.py clear_unverified  # Очистка базы от неавторизованных/фейковых аккаунтов
```

##🐳 Развертывание (Production Stack)
Проект полностью контейнеризирован и оптимизирован для работы в связке Docker + Nginx + Gunicorn + SSL. Весь процесс запуска на новом сервере занимает менее 5 минут:

```bash
# 1. Клонирование и настройка окружения
git clone https://github.com
cd modnoemesto
nano .env # Добавьте свои API-ключи (OpenAI, TG, Paybox)

# 2. Холодный запуск экосистемы
docker compose up -d --build

# 3. Финализация инфраструктуры
docker compose exec web python manage.py migrate
docker compose exec web python manage.py collectstatic --noinput
docker compose exec web python manage.py createsuperuser
```

##🎨 UI/UX & PWA
Custom Design: Весь интерфейс спроектирован с нуля: чистый код, отсутствие лишних фреймворков, высокая скорость отрисовки.
Safari/Chrome Optimization: Тонкая настройка apple-touch-icon, favicon в форматах SVG/PNG и манифеста для корректной работы сайта как нативного приложения на iOS и Android.
Vector Graphics: Использование SVG для всех иконок, что обеспечивает идеальную четкость на Retina-дисплеях.
