import os
import time
import requests
from urllib.parse import urlparse
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

# --- НАСТРОЙКИ ---
COLLECTION_URL = "https://grizas.com/blogs/catalogues/spring-summer26-wedding-special-occasions"
SAVE_DIR = "Spring|Summer'26 Wedding & Special Occasions"
MAX_IMAGES = 45
downloaded = 0

chrome_options = Options()
# Подключаемся к уже открытому порту из Шага 1
chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9233")

os.makedirs(SAVE_DIR, exist_ok=True)

try:
    driver = webdriver.Chrome(options=chrome_options)
    print("Подключился к браузеру!")

    driver.get(COLLECTION_URL)
    time.sleep(5)

    product_links = set()

    # 1️⃣ Сбор ссылок
    print("Собираю ссылки...")
    for _ in range(10):
        links = driver.find_elements(By.CSS_SELECTOR, "a[href*='/pin/'], a[href*='/products/']")
        for link in links:
            href = link.get_attribute("href")
            if href:
                product_links.add(href.split("?")[0])

        if len(product_links) >= MAX_IMAGES: break
        driver.execute_script("window.scrollBy(0, 1200);")
        time.sleep(2)

    links_list = list(product_links)
    print(f"Найдено ссылок: {len(links_list)}. Качаем фото...")

    # 2️⃣ Скачивание
    for url in links_list:
        if downloaded >= MAX_IMAGES: break

        # Убедимся, что ссылка полная
        if not url.startswith('http'):
            url = "https://pinterest.com" + url

        print(f"Перехожу по ссылке: {url}")
        driver.get(url)
        time.sleep(4)  # Даем время на рендер картинки

        # Пробуем найти главную картинку пина/товара разными способами
        found_src = None

        # Способ А: Ищем по селектору большой картинки Pinterest
        selectors = [
            "img[srcset]",
            "img.hCL",
            "div[data-test-id='pin-closeup-image'] img",
            "img[src*='://pinimg.com']"
        ]

        for selector in selectors:
            try:
                el = driver.find_element(By.CSS_SELECTOR, selector)
                found_src = el.get_attribute("src")
                if found_src: break
            except:
                continue

        # Если не нашли через селекторы, берем все img и ищем самую большую
        if not found_src:
            all_imgs = driver.find_elements(By.TAG_NAME, "img")
            for img in all_imgs:
                src = img.get_attribute("src")
                if src and ("://pinimg.com" in src or "://shopify.com" in src):
                    if "originals" in src or "736x" in src or "_1200x" in src:
                        found_src = src
                        break

        if found_src:
            # Улучшаем качество до оригинала
            high_res = found_src.replace("236x", "originals").replace("474x", "originals").replace("736x",
                                                                                                   "originals").replace(
                "_500x", "_1200x")

            # Чистим имя файла от параметров типа ?v=123
            clean_url = high_res.split('?')[0]
            filename = os.path.basename(urlparse(clean_url).path)
            if not filename: filename = f"img_{downloaded}.jpg"

            path = os.path.join(SAVE_DIR, filename)

            try:
                # Добавляем User-Agent, чтобы сервер не сбросил соединение
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
                r = requests.get(high_res, timeout=15, headers=headers)

                if r.status_code == 200:
                    with open(path, "wb") as f:
                        f.write(r.content)
                    downloaded += 1
                    print(f"[{downloaded}/{MAX_IMAGES}] Успех: {filename}")
                else:
                    print(f"Ошибка сервера: {r.status_code}")
            except Exception as e:
                print(f"Не удалось скачать {high_res}: {e}")
        else:
            print("Картинка на странице не найдена")


except Exception as e:
    print(f"Ошибка: {e}")

finally:
    print(f"\nЗавершено! Скачано: {downloaded}")
