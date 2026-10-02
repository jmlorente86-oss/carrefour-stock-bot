import os
import threading
import time
import asyncio
import requests

from bs4 import BeautifulSoup
from flask import Flask
from telegram import Bot


# =========================
# CONFIGURACIÓN
# =========================

TOKEN = os.environ["TELEGRAM_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]

PRODUCTS = {
    "Mini Latas 30º Aniversario":
        "https://www.carrefour.es/pokemon-30th-aniversario-mini-latas-6-anos-unboxing/VC4A-34535247/p",

    "Caja 6 sobres 30º Aniversario":
        "https://www.carrefour.es/pokemon-caja-lote-6-sobres-30th-aniversario-juego-de-mesa-6-anos-unboxing/VC4A-34530762/p",
}


# =========================
# SERVIDOR WEB
# =========================

app = Flask(__name__)


@app.route("/")
def home():
    return "Bot de stock Carrefour funcionando ✅"


# =========================
# SESIÓN DE CARREFOUR
# =========================

session = requests.Session()

session.headers.update({
    "User-Agent": (
        "Mozilla/5.0 (Linux; Android 10; K) "
        "AppleWebKit/537.36 "
        "(KHTML, like Gecko) "
        "Chrome/143.0.0.0 Mobile Safari/537.36"
    ),
    "Accept": (
        "text/html,application/xhtml+xml,"
        "application/xml;q=0.9,image/avif,"
        "image/webp,*/*;q=0.8"
    ),
    "Accept-Language": "es-ES,es;q=0.9,en;q=0.8",
    "Accept-Encoding": "gzip, deflate",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
})


# =========================
# COMPROBAR STOCK
# =========================

def check_stock(url):

    for intento in range(1, 4):

        try:
            print(
                f"🌐 Consultando Carrefour "
                f"(intento {intento}/3)..."
            )

            response = session.get(
                url,
                timeout=30,
                allow_redirects=True
            )

            print(
                f"📡 Respuesta Carrefour: "
                f"{response.status_code}"
            )

            # Carrefour está bloqueando la petición
            if response.status_code == 403:

                if intento < 3:
                    print(
                        "⚠️ Carrefour ha rechazado la petición. "
                        "Reintentando..."
                    )
                    time.sleep(5)
                    continue

                raise Exception(
                    "Carrefour ha bloqueado la petición (403)"
                )

            response.raise_for_status()

            text = BeautifulSoup(
                response.text,
                "html.parser"
            ).get_text(
                " ",
                strip=True
            ).lower()

            unavailable = [
                "agotado",
                "sin stock",
                "no disponible"
            ]

            for word in unavailable:

                if word in text:
                    return False

            return True

        except requests.RequestException as e:

            if intento < 3:
                print(
                    f"⚠️ Error de conexión: {e}"
                )
                time.sleep(5)
            else:
                raise e


# =========================
# ENVIAR TELEGRAM
# =========================

async def send_telegram_message(text):

    bot = Bot(TOKEN)

    async with bot:
        await bot.send_message(
            chat_id=CHAT_ID,
            text=text
        )


def send_alert(text):

    try:

        asyncio.run(
            send_telegram_message(text)
        )

        print("📱 Alerta enviada a Telegram")

    except Exception as e:

        print(
            f"❌ Error enviando Telegram: {e}"
        )


# =========================
# MONITOR
# =========================

def monitor():

    print("🚀 MONITOR DE CARREFOUR INICIADO")

    previous_status = {}

    print("✅ Monitor preparado")

    while True:

        print("🔎 Comprobando stock...")

        for name, url in
