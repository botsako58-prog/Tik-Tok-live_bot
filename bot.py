
import asyncio
import telebot
from TikTokLive import TikTokLiveClient
from TikTokLive.events import ConnectEvent, GiftEvent

TELEGRAM_TOKEN = "8807351971:AAF_K2hCOPSmZ5ZHfM02mojge5KX8MuG7lc"
TELEGRAM_CHAT_ID = "-1003835472130"

TARGET_STREAMERS = ["tiktok", "live", "qazaxistan", "baku"]

bot = telebot.TeleBot(TELEGRAM_TOKEN)


def send_alert(text: str):
    try:
        bot.send_message(TELEGRAM_CHAT_ID, text)
    except Exception as e:
        print(f"Telegram xətası: {e}")


async def watch_streamer(username: str):
    print(f"[+] İzləməyə başlandı: @{username}")
    client = TikTokLiveClient(unique_id=username)

    @client.on(ConnectEvent)
    async def on_connect(event: ConnectEvent):
        print(f"[Connected] Qoşuldu: @{username}")

    @client.on(GiftEvent)
    async def on_gift(event: GiftEvent):
        gift_name = getattr(event.gift, "name", "") or ""
        diamonds = getattr(event.gift, "diamond_count", 0) or 0
        if "box" in gift_name.lower() or "sandiq" in gift_name.lower() or "sandıq" in gift_name.lower() or "chest" in gift_name.lower() or diamonds >= 100:
            msg = f"🎁 Sandıq / Böyük Hədiyyə!\nYayımçı: @{username}\nHədiyyə: {gift_name}\nDəyəri: {diamonds} almaz"
            print(f"[ALERT] {msg}")
            send_alert(msg)

    while True:
        try:
            await client.connect()
        except Exception as e:
            print(f"[-] @{username} bağlantı xətası: {e}")
        await asyncio.sleep(3)


async def main():
    print("Konkret hesablar izlənilir...")
    tasks = [asyncio.create_task(watch_streamer(u)) for u in TARGET_STREAMERS]
    await asyncio.gather(*tasks)


