import json
import requests
import time

products_slugs = [
    "ispring-dental-gel", "gano-plus-sigp", "ng-моchо-chino", "i-royal",
    "ng-cool-tea-latte", "ng-gano-koppe-3in1", "dark-latte", "i-red-gano",
    "i-gano-plus", "i-excel-plus", "igarsino", "ng-cocoa-cino",
    "ng-flakes-chino", "ng-creal", "ng-black-koppe", "i-supremo",
    "i-sakano", "i-cleanse", "i-white", "reskine-коллаген",
    "ng-brown-romance-олии-навли-колумбия-какао-кукуни-ва-ганодерма-экстракти-мазали-ва-хушбуи-иссиқ-гано-шоколад-булиб-организмга-роҳат-ва-қувват-бағишлаиди",
    "excellium-gold", "cordy-gold", "reishi-gold", "icrystal--қувват-кулони"
]


def parse_gano_products_bilingual():
    final_db = []
    base_url = "https://api.gano.uz/api/products/"

    headers = {
        "Accept": "application/json",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/26.5.2 Safari/605.1.15",
        "Origin": "https://gano.uz",
        "Referer": "https://gano.uz/"
    }

    print("Начинаем сбор двуязычной базы данных...")

    for slug in products_slugs:
        print(f"Парсим: {slug}...")

        try:
            # 1. Получаем узбекскую версию
            resp_uz = requests.get(f"{base_url}{slug}?lang=uz", headers=headers)
            data_uz = resp_uz.json() if resp_uz.status_code == 200 else {}

            # Небольшая пауза между запросами к одному товару
            time.sleep(0.5)

            # 2. Получаем русскую версию
            resp_ru = requests.get(f"{base_url}{slug}?lang=ru", headers=headers)
            data_ru = resp_ru.json() if resp_ru.status_code == 200 else {}

            if not data_uz and not data_ru:
                print(f"[-] Не удалось получить данные для {slug}, пропускаем.")
                continue

            # 3. Собираем всё в нужный формат
            product_data = {
                # Формируем id в стиле "p25" (или просто оставляем числом, если убрать "p")
                "id": f"p{data_uz.get('id', '')}",
                "badge": {"uz": "", "ru": ""},
                "badgeType": "",
                "uploads": data_uz.get("uploads", []),
                "name": {
                    "uz": data_uz.get("name", ""),
                    "ru": data_ru.get("name", "")
                },
                "brand": "Gano Excel",
                "price": data_uz.get("price", 0),
                "volume": {
                    "uz": data_uz.get("product_type", ""),
                    "ru": data_ru.get("product_type", "")
                },
                "tags": {
                    "uz": data_uz.get("categories", []),
                    "ru": data_ru.get("categories", [])
                },
                "about": {
                    # Если полного описания нет, страхуемся коротким
                    "uz": data_uz.get("full_description") or data_uz.get("short_description", ""),
                    "ru": data_ru.get("full_description") or data_ru.get("short_description", "")
                },
                "benefits": {
                    "uz": data_uz.get("benefits", []),
                    "ru": data_ru.get("benefits", [])
                }
            }

            final_db.append(product_data)

        except Exception as e:
            print(f"[-] Ошибка при обработке {slug}: {e}")

        # Пауза перед следующим товаром, чтобы не получить бан по IP
        time.sleep(1)

    output_file = "gano_products_bilingual.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(final_db, f, ensure_ascii=False, indent=4)

    print(f"\nГотово! База данных сохранена в {output_file}")


if __name__ == "__main__":
    parse_gano_products_bilingual()