from concurrent.futures import ThreadPoolExecutor
import os
import requests

products_slugs = [
    "ispring-dental-gel",
    "gano-plus-sigp",
    "ng-моchо-chino",
    "i-royal",
    "ng-cool-tea-latte",
    "ng-gano-koppe-3in1",
    "dark-latte",
    "i-red-gano",
    "i-gano-plus",
    "i-excel-plus",
    "igarsino",
    "ng-cocoa-cino",
    "ng-flakes-chino",
    "ng-creal",
    "ng-black-koppe",
    "i-supremo",
    "i-sakano",
    "i-cleanse",
    "i-white",
    "reskine-коллаген",
    "ng-brown-romance-олии-навли-колумбия-какао-кукуни-ва-ганодерма-экстракти-мазали-ва-хушбуи-иссиқ-гано-шоколад-булиб-организмга-роҳат-ва-қувват-бағишлаиди",
    "excellium-gold",
    "cordy-gold",
    "reishi-gold",
    "icrystal--қувват-кулони",
]

BASE_API = "https://api.gano.uz/api/products/"
BASE_SITE = "https://api.gano.uz"  # Базовый домен для файлов /uploads/
IMAGE_DIR = "uploads"

# Заголовки для обхода блокировок
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15"
    ),
    "Origin": "https://gano.uz",
    "Referer": "https://gano.uz/",
}


def get_image_urls():
    """Собирает все уникальные ссылки на изображения из всех товаров."""
    image_urls = set()
    print("Собираем ссылки на картинки...")

    for slug in products_slugs:
        try:
            res = requests.get(f"{BASE_API}{slug}?lang=ru", headers=HEADERS)
            if res.status_code == 200:
                data = res.json()
                # Берём массив uploads и обложку image_url
                imgs = data.get("uploads", [])
                if data.get("image_url"):
                    imgs.append(data.get("image_url"))

                for img_path in imgs:
                    if img_path:
                        # Превращаем относительный путь /uploads/... в полный URL
                        full_url = (
                            img_path
                            if img_path.startswith("http")
                            else f"{BASE_SITE}{img_path}"
                        )
                        image_urls.add(full_url)
        except Exception as e:
            print(f"Ошибка при сборе ссылок для {slug}: {e}")

    return list(image_urls)


def download_single_image(url):
    """Скачивает одно изображение."""
    try:
        filename = url.split("/")[-1]
        filepath = os.path.join(IMAGE_DIR, filename)

        # Пропускаем, если уже скачано
        if os.path.exists(filepath):
            return

        res = requests.get(url, headers=HEADERS, timeout=10)
        if res.status_code == 200:
            with open(filepath, "wb") as f:
                f.write(res.content)
            print(f"[+] Скачано: {filename}")
        else:
            print(f"[-] Ошибка {res.status_code}: {url}")
    except Exception as e:
        print(f"[-] Ошибка загрузки {url}: {e}")


def main():
    if not os.path.exists(IMAGE_DIR):
        os.makedirs(IMAGE_DIR)

    urls = get_image_urls()
    print(
        f"\nНайдено уникальных картинок: {len(urls)}. Начинаем быструю загрузку в 15 потоков...\n"
    )

    # Запускаем параллельную загрузку в 15 потоков
    with ThreadPoolExecutor(max_workers=15) as executor:
        executor.map(download_single_image, urls)

    print("\nВсе изображения успешно загружены в папку 'uploads'!")


if __name__ == "__main__":
    main()