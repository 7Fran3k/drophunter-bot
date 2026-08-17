import time
import requests
from curl_cffi import requests as cureq

WEBHOOK_URL = "https://discord.com/api/webhooks/1538679889564270625/wIo-m3S6kz18lO6tFcVXIUXWozthzd8sPMNRoFoip3Zos6Zjo25KGg1WzTDrdAXGSg_Y"
SEARCH_URL = "https://www.vinted.pl/api/v2/catalog/items?order=newest_first&page=1&per_page=10"

seen_item_ids = set()

def get_vinted_items():
    session = cureq.Session(impersonate="chrome120")
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*"
    }
    
    try:
        session.get("https://www.vinted.pl", headers=headers)
        response = session.get(SEARCH_URL, headers=headers)
        if response.status_code == 200:
            return response.json().get("items", [])
        else:
            print(f"Status Vinted: {response.status_code}")
            return []
    except Exception as e:
        print(f"Błąd połączenia: {e}")
        return []

def send_to_discord(item):
    title = item.get("title") or item.get("brand_title") or "Nowa oferta"
    price = f"{item.get('price', {}).get('amount', '0.00')} {item.get('price', {}).get('currency_code', 'PLN')}"
    item_url = item.get("url")
    if item_url and not item_url.startswith("http"):
        item_url = f"https://www.vinted.pl{item_url}"
        
    photo_url = item.get("photo", {}).get("url")
    brand = item.get("brand_title", "Brak")
    size = item.get("size_title", "Brak")

    embed = {
        "title": f"🔥 {title}",
        "url": item_url,
        "color": 0x09B1BA,
        "fields": [
            {"name": "💰 Cena", "value": price, "inline": True},
            {"name": "🏷️ Marka", "value": brand, "inline": True},
            {"name": "📏 Rozmiar", "value": size, "inline": True}
        ]
    }
    
    if photo_url:
        embed["image"] = {"url": photo_url}

    payload = {
        "username": "DropHunter Vinted",
        "embeds": [embed]
    }

    requests.post(WEBHOOK_URL, json=payload)

def run_tracker():
    print("🚀 DropHunter Vinted wystartował pomyślnie!")
    
    initial_items = get_vinted_items()
    for item in initial_items:
        if item.get("id"):
            seen_item_ids.add(item["id"])
    print(f"Załadowano początkowo {len(seen_item_ids)} ofert. Czekam na nowe okazje...")

    while True:
        try:
            items = get_vinted_items()
            for item in items:
                item_id = item.get("id")
                if item_id and item_id not in seen_item_ids:
                    print(f"Znaleziono nową ofertę: {item.get('title') or item.get('brand_title')}")
                    send_to_discord(item)
                    seen_item_ids.add(item_id)
        except Exception as e:
            print(f"Wystąpił błąd: {e}")

        time.sleep(45)

if __name__ == "__main__":
    run_tracker()
