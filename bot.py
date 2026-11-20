import asyncio
import os
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
import telebot
from TikTokLive import TikTokLiveClient
from TikTokLive.events import ConnectEvent, GiftEvent


class _Health(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"OK")
        except Exception:
            pass

    def log_message(self, *args):
        pass


def _start_health_server():
    try:
        port_raw = os.environ.get("PORT", "10000")
        port = int(port_raw) if str(port_raw).isdigit() else 10000
        server = HTTPServer(("0.0.0.0", port), _Health)
        server.serve_forever()
    except Exception as e:
        print(f"[HealthInfo] {e}", flush=True)


threading.Thread(target=_start_health_server, daemon=True).start()

TELEGRAM_TOKEN = (os.environ.get("TELEGRAM_TOKEN") or "8807351971:AAF_K2hCOPSrn25ZHTfMO2mojge5KX8WuG7lc").strip()
TELEGRAM_CHAT_ID = (os.environ.get("TELEGRAM_CHAT_ID") or "-1003835472130").strip()
TARGET_STREAMERS = ["tiktok", "live", "qazaxistan", "baku"]

bot = telebot.TeleBot(TELEGRAM_TOKEN)


def send_alert(text: str):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        return
    try:
        bot.send_message(TELEGRAM_CHAT_ID, text)
    except Exception as e:
        print(f"[TelegramLog] {e}", flush=True)


async def watch_streamer(username: str):
    print(f"[+] İzlənilir: @{username}", flush=True)
    while True:
        try:
            client = TikTokLiveClient(unique_id=username)

            @client.on(ConnectEvent)
            async def on_connect(event: ConnectEvent):
                print(f"[Connected] @{username}", flush=True)

            @client.on(GiftEvent)
            async def on_gift(event: GiftEvent):
                try:
                    gift = getattr(event, "gift", None)
                    gift_name = str(getattr(gift, "name", "") or "")
                    diamonds_raw = getattr(gift, "diamond_count", 0)
                    diamonds = int(diamonds_raw) if diamonds_raw is not None else 0
                    lower_name = gift_name.lower()

                    if (
                        "box" in lower_name
                        or "sandiq" in lower_name
                        or "sandıq" in lower_name
                        or diamonds >= 500
                    ):
                        msg = (
                            f"Sandıq / Böyük Hədiyyə\n"
                            f"Yayıncı: @{username}\n"
                            f"Hədiyyə: {gift_name} ({diamonds})"
                        )
                        print(f"[ALERT] {msg}", flush=True)
                        await asyncio.to_thread(send_alert, msg)
                except Exception as e:
                    print(f"[GiftLog] @{username}: {e}", flush=True)

            await client.start()
        except Exception as e:
            print(f"[Retry] @{username}: {e}", flush=True)

        await asyncio.sleep(15)


async def main():
    print("[*] Bot aktivdir...", flush=True)
    tasks = [asyncio.create_task(watch_streamer(u)) for u in TARGET_STREAMERS]
    await asyncio.gather(*tasks, return_exceptions=True)
    while True:
        await asyncio.sleep(60)


if __name__ == "__main__":
    while True:
        try:
            asyncio.run(main())
        except Exception as e:
            print(f"[LoopLog] {e}", flush=True)
        import time
        time.sleep(5)
        
