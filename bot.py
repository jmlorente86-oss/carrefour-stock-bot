import os
import asyncio
import requests
from bs4 import BeautifulSoup
from telegram import Bot

TOKEN = os.environ["TELEGRAM_TOKEN"]

PRODUCTS = {
    "Mini Latas 30º Aniversario": "https://www.carrefour.es/pokemon-30th-aniversario-mini-latas-6-anos-unboxing/VC4A-34535247/p",
    "Caja 6 sobres 30º Aniversario": "https://www.carrefour.es/pokemon-caja-lote-6-sobres-30th-aniversario-juego-de-mesa-6-anos-unboxing/VC4A-34530762/p",
}

INTERVAL = 300  # 5 minutos

def check_stock(url):
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    response = requests.get(url, headers=headers, timeout=20)
    response.raise_for_status()

    text = BeautifulSoup(response.text, "html.parser").get_text(" ", strip=True).lower()

    unavailable = [
        "agotado",
        "sin stock",
        "no disponible",
    ]

    return not any(word in text for word in unavailable)


async def main():
    bot = Bot(TOKEN)

    chat_id = os.environ["CHAT_ID"]

    previous_status = {}

    while True:
        for name, url in PRODUCTS.items():
            try:
                available = check_stock(url)

                if available and previous_status.get(name) is False:
                    await bot.send_message(
                        chat_id=chat_id,
                        text=f"🚨 ¡STOCK DETECTADO!\n\n{name}\n\n{url}"
                    )

                previous_status[name] = available

            except Exception as e:
                print(f"Error comprobando {name}: {e}")

        await asyncio.sleep(INTERVAL)


if __name__ == "__main__":
    asyncio.run(main())
