from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import os
import requests
from urllib.parse import urlparse, urljoin


MAX_IMAGES = 60
downloaded_count = 0


BASE_URL = "https://grizas.com"
COLLECTION_URL = "https://grizas.com/blogs/catalogues/spring-summer26-wedding-special-occasions"  # каталог
SAVE_DIR = "Spring|Summer'26 Wedding & Special Occasions"

os.makedirs(SAVE_DIR, exist_ok=True)

driver = webdriver.Chrome()
driver.get(COLLECTION_URL)

time.sleep(5)

# 1️⃣ собираем ссылки на товары
product_links = set()

links = driver.find_elements(By.TAG_NAME, "a")

for link in links:
    href = link.get_attribute("href")
    if href and "/products/" in href:
        product_links.add(href.split("?")[0])

print("Найдено товаров:", len(product_links))

# ... (начало кода без изменений)

# 2️⃣ переходим в каждый товар
for product_url in product_links:
    if downloaded_count >= MAX_IMAGES:
        break

    driver.get(product_url)
    time.sleep(3)  # Ждем загрузки

    # Ищем картинки ТОЛЬКО внутри галереи товара (у Shopify это обычно класс product-single__media или похожий)
    # Если не сработает, используем более точный селектор для картинок товара
    images = driver.find_elements(By.CSS_SELECTOR, "img[src*='/products/']")

    unique_srcs = set()  # Чтобы не качать дубли на одной странице

    for img in images:
        src = img.get_attribute("src")
        if not src: continue

        # Чистим URL от параметров размера Shopify (?v=...), чтобы получить оригинал
        clean_src = src.split("?")[0].replace("_small", "").replace("_100x", "").replace("_500x", "")
        # Форсируем большой размер, если нужно
        clean_src = "https:" + clean_src if clean_src.startswith("//") else clean_src

        if clean_src not in unique_srcs:
            unique_srcs.add(clean_src)

            filename = os.path.basename(urlparse(clean_src).path)
            # Папка для конкретного товара
            folder = os.path.join(SAVE_DIR, product_url.split("/")[-1])
            os.makedirs(folder, exist_ok=True)

            path = os.path.join(folder, filename)

            try:
                r = requests.get(clean_src, timeout=10)
                with open(path, "wb") as f:
                    f.write(r.content)
                downloaded_count += 1
                print(f"Скачано {downloaded_count}: {filename}")
            except Exception as e:
                print(f"Ошибка при скачивании {clean_src}: {e}")

            if downloaded_count >= MAX_IMAGES:
                break

driver.quit()

