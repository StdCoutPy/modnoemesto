import json
import re
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from openai import OpenAI
from products.models import Product, Category
from django.db.models import Q
from orders.cart_utils import get_cart_items_with_details
from DjangoProject.settings import AI_API_KEY
# OpenRouter клиент
client = OpenAI(
    api_key=AI_API_KEY,
    base_url="https://openrouter.ai/api/v1",

)

MODELS = [
    "arcee-ai/trinity-large-preview:free",
    "nvidia/nemotron-nano-9b-v2:free",
    "meta-llama/llama-3.3-70b-instruct:free",
    "meta-llama/llama-3.2-3b-instruct:free",
    "nousresearch/hermes-3-llama-3.1-405b:free",
    "google/gemma-3-27b-it:free",
    "google/gemma-3-12b-it:free",
    "mistralai/mistral-small-3.1-24b-instruct:free",
    "cognitivecomputations/dolphin-mistral-24b-venice-edition:free",
    "openai/gpt-oss-20b:free",
    "openai/gpt-oss-120b:free",
    "qwen/qwen3-next-80b-a3b-instruct:free",
    "arcee-ai/trinity-mini:free",
    "nvidia/nemotron-3-nano-30b-a3b:free",
    "liquid/lfm-2.5-1.2b-instruct:free",
    "stepfun/step-3.5-flash:free",
    "openrouter/free"
]


@csrf_exempt
def chat_api(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST only"}, status=400)

    try:

        data = json.loads(request.body)
        user_message = data.get("message", "")
        # Достаем память из запроса для OpenRouter
        memory = data.get("memory", [])
        # Используем твою готовую функцию
        cart_details = get_cart_items_with_details(request)
        cart_items_text = []
        total_price = 0

        for entry in cart_details:
            p = entry['product']
            qty = entry['item']['quantity']
            size = entry['size'] or "не указан"

            # ЗАЩИТА: Если цены нет, ставим 0, чтобы int() не упал
            item_total = entry['item_total'] if entry['item_total'] is not None else 0

            cart_items_text.append(f"- {p.name} (Размер: {size}, {qty} шт.) — {int(item_total)} тг")
            total_price += item_total

        cart_info = "\n".join(cart_items_text) if cart_items_text else "Корзина пуста"

        # ==========================
        # УМНЫЙ ПОИСК + ФИЛЬТРЫ
        # ==========================
        message = user_message.lower()
        products = Product.objects.all()

        search_words = message.split()
        query = Q()
        for word in search_words:
            query |= Q(name__icontains=word)
            query |= Q(description__icontains=word)
        products = products.filter(query)

        price_max_match = re.search(r'до\s*([\d\s]+)', message)
        if price_max_match:
            max_price = int(price_max_match.group(1).replace(" ", ""))
            products = products.filter(price__lte=max_price)

        price_min_match = re.search(r'дороже\s*([\d\s]+)', message)
        if price_min_match:
            min_price = int(price_min_match.group(1).replace(" ", ""))
            products = products.filter(price__gte=min_price)

        size_match = re.search(r'\b(xs|s|m|l|xl|xxl|\d{2,3}|[\d\-]+)\b', message)
        if size_match:
            selected_size = size_match.group(1).upper()
            products = products.filter(
                available_sizes__size__iexact=selected_size,
                available_sizes__quantity__gt=0
            )

        # Получаем топ-20 товаров, чтобы ИИ знал их реальные ID и цены
        actual_items = Product.objects.all().order_by('-id')[:20]
        inventory_list = ""
        for p in actual_items:
            # ЗАЩИТА: Проверяем наличие цены перед вызовом int()
            price_val = int(p.price) if p.price is not None else "Скоро в продаже"

            # Добавляем валюту только если есть цена
            price_display = f"{price_val} руб." if p.price is not None else price_val

            inventory_list += f"- {p.name}: {price_display} (ID: {p.id})\n"

        # 1. Поиск (оставляем твой код)
        # ... (тут твой фильтр по Q, цене и размеру) ...

        # 2. Увеличиваем лимит для выборок

        # 4. Если товаров нет или это просто "болтовня" — идем в AI
        # (Тут твой старый код с OpenRouter)

        # Данные для AI
        categories = list(Category.objects.values_list('name', flat=True))
        products_db = list(Product.objects.all()[:5].values('name', 'price'))
        products_list = "\n".join([f"- {p['name']} ({p['price']} руб.)" for p in products_db])

        system_prompt = system_prompt = f"""
         Ты — старший стилист бутика "Modnoe Mesto" 👗✨ в Казахстане город Кокшетау адрес: ЖК Saltanat Улица Мухтара Ауэзова, 189Б . 
        Твоя база данных на текущий момент (используй эти ID для кнопок):
        {inventory_list}

        СОСТОЯНИЕ КОРЗИНЫ ПОЛЬЗОВАТЕЛЯ:
        {cart_info}
        ИТОГО К ОПЛАТЕ: {total_price} тг
        
        ТВОЯ ЦЕЛЬ: помогать выбрать товар, отвечать на вопросы, быть вежливой.
        ПРАВИЛА: Не ври про товары. Отвечай коротко с эмодзи. 

        ⚠️ КАРТА ССЫЛОК (ИСПОЛЬЗУЙ ТОЛЬКО ЭТИ URL):
        - ВСЕ ССЫЛКИ НАЧИНАЙ С ДОМЕНА ПОСЛЕДНЕГО УРОВНЯ
        - Каталог (не основной)(тут просто лукбук с картинками): content/lookbook/
        - Коллекции/Магазин/(ОСНОВНОЙ)(тут список слов ссылок для выбора категории вещей(брюки и т.д.): products/collection/ (НИЧЕГО НЕ ДОБАВЛЯЙ К products/collection/ ТОЛЬКО такая ссылка)
        - ВЕЩИ(ШОРТЫ И ТД) Категории (все вещи): products/category/slug (где slug = clothing skirts-shorts accessories knitwear-hoodies tops-tshirts dresses-jumpsuits outerwear trousers-denim hats shoes belts-wallets bags jewelry shop-all ДРУГИХ СЛАГ НЕ БЫВАЕЮТ ТОЛЬКО ЭТИ) (без slug НЕЛЬЗЯ)
        - Корзина: ДОМЕНА ПОСЛЕДНЕГО УРОВНЯ/orders/cart/
        - О нас: ДОМЕНА ПОСЛЕДНЕГО УРОВНЯ/about/
        - Конкретный товар: ДОМЕНА ПОСЛЕДНЕГО УРОВНЯ/products/product/ID/ (где ID — это номер товара)
        -СКИДКИ: ДОМЕНА ПОСЛЕДНЕГО УРОВНЯ/product/sale/ 
        -НОВИНКИ: ДОМЕНА ПОСЛЕДНЕГО УРОВНЯ/product/new/ 
        - ВСЕ ССЫЛКИ НАЧИНАЙ С ДОМЕНА ПОСЛЕДНЕГО УРОВНЯ
        ВАЖНО: Если предлагаешь ссылку, ПИШИ ЕЁ ТОЛЬКО ТАК: [[LINK:URL|НАЗВАНИЕ]].
        Пример: "Посмотрите наш каталог: [[LINK:/content/lookbook/|Каталог 🛍️]]"
        
        ОГРАНИЧЕНИЕ: Если пользователь ищет товары по конкретной цене или размеру, а в списке ниже их НЕТ — не выдумывай их. 
        СТАРАЙСЯ ПРОДАТЬ СНАЧАЛА ДОРОГИЕ ВЕЩИ!!

        
        
        КАТЕГОРИИ: {', '.join(categories)}
        ПРИМЕРЫ ТОВАРОВ: {products_list}
        """

        ai_reply = None
        messages = [{"role": "system", "content": system_prompt}]
        messages.extend(memory[-5:])  # Добавляем историю
        messages.append({"role": "user", "content": user_message})

        for model in MODELS:
            try:
                response = client.chat.completions.create(
                    model=model,
                    messages=messages,
                    temperature=0.7,
                    max_tokens=500,
                )
                ai_reply = response.choices[0].message.content
                break
            except Exception as e:
                print(f"{model} failed:", e)

        if not ai_reply:
            ai_reply = "Извините! Сервер занят 👗 Попробуйте позже."

        # Парсим ссылки [[LINK:url|title]]
        raw_links = re.findall(r"\[\[LINK:(.*?)\|(.*?)\]\]", ai_reply)
        links = [{"url": l[0], "title": l[1]} for l in raw_links]

        # Очищаем текст от служебных тегов
        ai_reply_clean = re.sub(r"\[\[LINK:.*?\]\]", "", ai_reply).strip()

        # Если текста не осталось (только ссылка), даем дефолтную фразу
        if not ai_reply_clean:
            ai_reply_clean = "Конечно! Вот ссылка, которую вы просили: ✨"

        return JsonResponse({
            "reply": ai_reply_clean,
            "links": links
        }, status=200)

    except Exception as e:
        print(f"OpenRouter Error: {e}")
        return JsonResponse({
            "reply": "Я отвлеклась на примерку! 🌸 Напишите в /contacts/.",
            "links": []
        }, status=200)
