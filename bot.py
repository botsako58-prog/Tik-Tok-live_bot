import asyncio
from datetime import datetime, timedelta, timezone
import json
import os
import re
import threading
import time
import urllib.parse
import urllib.request
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

TELEGRAM_TOKEN = (
    os.environ.get("TELEGRAM_TOKEN")
    or "8807351971:AAF_K2hCOPSrn25ZHTfMO2mojge5KX8WuG7lc"
).strip()
TELEGRAM_CHAT_ID = (
    os.environ.get("TELEGRAM_CHAT_ID") or "-1003835472130"
).strip()

SEED_STREAMERS = ["tiktok", "live", "qazaxistan", "baku"]
SEARCH_QUERIES = [
    "sandiq",
    "sandıq",
    "box",
    "treasure",
    "gift",
    "live",
]
MAX_AUTO_STREAMERS = 20
DISCOVERY_INTERVAL_SEC = 60
AZ_TZ = timezone(timedelta(hours=4))

bot = telebot.TeleBot(TELEGRAM_TOKEN)
watched_users = set()
state_lock = threading.Lock()


def now_clock() -> str:
    return datetime.now(AZ_TZ).strftime("%H:%M:%S")


def now_exact_sec() -> str:
    dt = datetime.now(AZ_TZ)
    return dt.strftime("%H:%M:%S.") + f"{dt.microsecond // 1000:03d}"


def _esc(text: str) -> str:
    return (
        str(text or "")
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def _extract_timing_info(event, client) -> str:
    parts = []
    sources = [str(event or "")]
    room_info = getattr(client, "room_info", None)
    if room_info is not None:
        sources.append(str(room_info))

    blob = " ".join(sources)
    matches = re.findall(
        r"(?:countdown|timer|duration|expire|end_time|time_left|left_time|timestamp)[\"':=\s]+([A-Za-z0-9_.:-]+)",
        blob,
        flags=re.IGNORECASE,
    )
    for m in matches:
        clean = m.strip(",\"'{}[]() ")
        if clean and clean not in parts:
            parts.append(clean)
        if len(parts) >= 4:
            break

    return ", ".join(parts) if parts else "Yoxdur"


def send_alert(text: str):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        return
    try:
        bot.send_message(
            TELEGRAM_CHAT_ID,
            text,
            parse_mode="HTML",
            disable_web_page_preview=False,
        )
    except Exception as e:
        print(f"[{now_clock()}] [TelegramLog] {e}", flush=True)


def _fetch_html(url: str) -> str:
    try:
        req = urllib.request.Request(
            url,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 (Linux; Android 13; SM-G991B) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/120.0.0.0 Mobile Safari/537.36"
                ),
                "Accept-Language": "az,en-US;q=0.9,en;q=0.8",
            },
        )
        with urllib.request.urlopen(req, timeout=12) as resp:
            return resp.read().decode("utf-8", errors="ignore")
    except Exception:
        return ""


def discover_streamers_sync() -> list:
    found = []
    seen = set()

    for u in SEED_STREAMERS:
        clean = u.strip().lstrip("@").lower()
        if clean and clean not in seen:
            seen.add(clean)
            found.append(clean)

    for q in SEARCH_QUERIES:
        encoded = urllib.parse.quote(q)
        urls = [
            f"https://www.tiktok.com/search/live?q={encoded}",
            f"https://www.tiktok.com/search/user?q={encoded}",
        ]
        for url in urls:
            html = _fetch_html(url)
            if not html:
                continue

            for m in re.findall(r'"uniqueId"\s*:\s*"([A-Za-z0-9._]{2,24})"', html):
                uname = m.lower().strip(".")
                if uname and uname not in seen:
                    seen.add(uname)
                    found.append(uname)
                if len(found) >= MAX_AUTO_STREAMERS:
                    return found

            for m in re.findall(r"/@([A-Za-z0-9._]{2,24})", html):
                uname = m.lower().strip(".")
                if uname and uname not in seen:
                    seen.add(uname)
                    found.append(uname)
                if len(found) >= MAX_AUTO_STREAMERS:
                    return found

    return found


async def watch_streamer(username: str):
    print(f"[{now_clock()}] [+] İzlənilir: @{username}", flush=True)
    while True:
        try:
            client = TikTokLiveClient(unique_id=username)

            @client.on(ConnectEvent)
            async def on_connect(event: ConnectEvent):
                print(f"[{now_exact_sec()}] [Connected] @{username}", flush=True)

            @client.on(GiftEvent)
            async def on_gift(event: GiftEvent):
                try:
                    gift = getattr(event, "gift", None)
                    gift_name = str(getattr(gift, "name", "") or "")
                    diamonds_raw = getattr(gift, "diamond_count", 0)
                    diamonds = int(diamonds_raw) if diamonds_raw is not None else 0
                    event_text = str(event)

                    combined = f"{gift_name} {event_text}".lower()
                    is_box = any(
                        k in combined
                        for k in ("box", "sandiq", "sandıq", "treasure", "chest")
                    )

                    if is_box or diamonds >= 500:
                        exact_ts = now_exact_sec()
                        timing_info = _extract_timing_info(event, client)
                        live_url = f"https://www.tiktok.com/@{username}/live"

                        msg = (
                            f"<b>Sandıq / Hədiyyə Siqnalı</b>\n"
                            f"<b>Yayıncı:</b> @{_esc(username)}\n"
                            f"<b>Canlı link:</b> <a href=\"{_esc(live_url)}\">Yayımı aç</a>\n"
                            f"<b>Hədiyyə:</b> {_esc(gift_name or 'Naməlum')} ({diamonds})\n"
                            f"<b>Düşmə saniyəsi:</b> <code>{_esc(exact_ts)}</code>\n"
                            f"<b>Vaxt/Sayğac sahəsi:</b> <code>{_esc(timing_info)}</code>"
                        )
                        print(f"[{exact_ts}] [ALERT] @{username} | {gift_name} ({diamonds}) | {timing_info}", flush=True)
                        await asyncio.to_thread(send_alert, msg)
                except Exception as e:
                    print(f"[{now_clock()}] [GiftLog] @{username}: {e}", flush=True)

            await client.start()
        except Exception as e:
            print(f"[{now_clock()}] [Retry] @{username}: {e}", flush=True)

        await asyncio.sleep(15)


def _schedule_new_watchers(candidates: list, loop: asyncio.AbstractEventLoop):
    added = []
    with state_lock:
        for u in candidates:
            clean = u.strip().lstrip("@").lower()
            if clean and clean not in watched_users:
                watched_users.add(clean)
                added.append(clean)
                loop.create_task(watch_streamer(clean))
    return added


async def discovery_loop(loop: asyncio.AbstractEventLoop):
    while True:
        await asyncio.sleep(DISCOVERY_INTERVAL_SEC)
        try:
            new_list = await asyncio.to_thread(discover_streamers_sync)
            added = _schedule_new_watchers(new_list, loop)
            if added:
                print(
                    f"[{now_clock()}] [AutoList] Yeni {len(added)} hesab əlavə olundu: {json.dumps(added)}",
                    flush=True,
                )
            else:
                print(
                    f"[{now_clock()}] [AutoList] Yeni əlavə olunacaq canlı hesab tapılmadı.",
                    flush=True,
                )
        except Exception as e:
            print(f"[{now_clock()}] [AutoListLog] {e}", flush=True)


async def main():
    loop = asyncio.get_running_loop()
    print(f"[{now_clock()}] [*] Sandıq izləmə və avto-axtarış botu işə düşdü...", flush=True)

    initial_list = await asyncio.to_thread(discover_streamers_sync)
    added = _schedule_new_watchers(initial_list, loop)
    print(
        f"[{now_clock()}] [InitList] {len(added)} hesab izləməyə verildi: {json.dumps(added)}",
        flush=True,
    )

    await discovery_loop(loop)


if __name__ == "__main__":
    while True:
        try:
            asyncio.run(main())
        except Exception as e:
            print(f"[{now_clock()}] [LoopLog] {e}", flush=True)
        time.sleep(5)
        
