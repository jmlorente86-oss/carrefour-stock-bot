import os
import threading
import time
import requests
from bs4 import BeautifulSoup
from flask import Flask
from telegram import Bot

TOKEN = os.environ["TELEGRAM_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]

PRODUCTS = {
    "Mini Latas 30º Aniversario": "https://www.carrefour.es/pokemon-30th-aniversario-mini-latas-6-anos-unboxing/VC4A-34535247/p",
    "Caja 6 sobres 30º Aniversario": "https://www.carrefour.es/pokemon-caja-lote-6-sobres-30th-aniversario-juego-de-mesa-6-anos-unboxing/VC4A-34530762/p",
}

app = Flask(__name__)


@app.route("/")
def home():
    return "Bot de stock Carrefour funcionando ✅"


def check_stock(url):
    headers = {"User-Agent": "Mozilla/5.0"}

    response = requests.get(
        url,
        headers=headers,
        timeout=20
    )

    response.raise_for_status()

    text = BeautifulSoup(
        response.text,
        "html.parser"
    ).get_text(" ", strip=True).lower()

    unavailable = [
        "agotado",
        "sin stock",
        "no disponible"
    ]

    return not any(word in text for word in unavailable)


def monitor():
    print("🚀 MONITOR DE CARREFOUR INICIADO")

    print("📱 Creando bot de Telegram...")
bot = Bot(TOKEN)
print("✅ Bot de Telegram creado")
    previous_status = {}
print("✅ Monitor preparado")

    while True:
        print("🔎 Comprobando stock...")

        for name, url in PRODUCTS.items():

            try:
                available = check_stock(url)

                print(
                    f"{name}: "
                    f"{'🟢 STOCK' if available else '🔴 SIN STOCK'}"
                )

                if available and previous_status.get(name) is False:
                    bot.send_message(
                        chat_id=CHAT_ID,
                        text=(
                            f"🚨 ¡STOCK DETECTADO!\n\n"
                            f"{name}\n\n"
                            f"{url}"
                        )
                    )

                previous_status[name] = available

            except Exception as e:
                print(
                    f"❌ Error comprobando {name}: {e}"
                )

        print("⏳ Esperando 5 minutos...")
        time.sleep(300)


# Iniciar monitor
threading.Thread(
    target=monitor,
    daemon=True
).start()
