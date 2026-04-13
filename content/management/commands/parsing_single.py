import os
import time
import requests
import re
from urllib.parse import urlparse
from selenium import webdriver
from selenium.webdriver.common.by import By

MAX_IMAGES = 100
URL = "https://grizas.com/blogs/catalogues/spring-summer26-wedding-special-occasions"  # каталог
SAVE_DIR = "Spring|Summer'26 Wedding & Special Occasions"
os.makedirs(SAVE_DIR, exist_ok=True)

driver = webdriver.Chrome()
driver.get(URL)

print("Прокрутка для загрузки всех фото...")
# Медленно скроллим до самого низа, чтобы прогрузились все Lazy-Load картинки
last_height = driver.execute_script("return document.body.scrollHeight")
while True:
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(2)
    new_height = driver.execute_script("return document.body.scrollHeight")
    if new_height == last_height:
        break
    last_height = new_height

# Собираем все img
imgs = driver.find_elements(By.TAG_NAME, "img")
downloaded_urls = set()
count = 0

for img in imgs:
    if count >= MAX_IMAGES:
        break

    # Проверяем и src, и data-src
    src = img.get_attribute("data-src") or img.get_attribute("src")

    # Фильтруем: нам нужны папки /articles/ или /files/
    if src and ("cdn.shopify.com" in src) and ("/articles/" in src or "/files/" in src):

        # 1. Убираем параметры размера типа _500x, _300x300 и т.д.
        clean_src = re.sub(r'_\d+x\d*', '', src)
        clean_src = re.sub(r'_\d+x', '', clean_src)

        # 2. Форсируем ширину 3000, если есть параметр width в URL
        if "width=" in clean_src:
            clean_src = re.sub(r'width=\d+', 'width=3000', clean_src)

        if clean_src.startswith("//"):
            clean_src = "https:" + clean_src

        # Убираем всё после расширения файла (токены версии ?v=...) для чистого сравнения
        url_for_set = clean_src.split('?')[0]

        if url_for_set not in downloaded_urls:
            downloaded_urls.add(url_for_set)

            filename = os.path.basename(url_for_set)
            path = os.path.join(SAVE_DIR, f"{count + 1}_{filename}")

            try:
                # Используем clean_src (с параметрами), чтобы сервер отдал нужный размер
                r = requests.get(clean_src, timeout=15)
                if r.status_code == 200:
                    with open(path, "wb") as f:
                        f.write(r.content)
                    count += 1
                    print(f"[{count}] Скачано: {filename}")
            except:
                print(f"Ошибка: {url_for_set}")

driver.quit()
print(f"\nГотово! Всего сохранено: {count}")
