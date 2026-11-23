import asyncio
import os
import time
import requests
from TikTokLive import TikTokLiveClient
from TikTokLive.events import ConnectEvent, GiftEvent, EnvelopeEvent

BOT_TOKEN = "8807351971:AAF_K2hCOPSmZ5ZHfM02mojge5KX8MuG7lc"
CHAT_ID = "6837476103"
HEDEF_DOSYASI = os.path.expanduser("~/tiktok-sandiq-radar/hedefler.txt")

canli_siyahisi = []
dinlenenler = {}
sayac_id = 10000

def ad_maskala(ad: str) -> str:
    if not ad:
        return "***"
    if len(ad) <= 2:
        return ad[0] + "***"
    return ad[:2] + "***"

def vaxt_araligi(deqiqe: int = 120) -> str:
    baslangic = time.strftime("%H:%M:%S", time.localtime())
    bitis = time.strftime("%H:%M:%S", time.localtime(time.time() + deqiqe * 60))
    return f"{baslangic} - {bitis}"

def bildirim_gonder(mesaj: str):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    try:
        r = requests.post(url, json={"chat_id": CHAT_ID, "text": mesaj}, timeout=10)
        if r.status_code != 200:
            print("[TG XETA]", r.status_code, r.text)
    except Exception as e:
        print("[TG ELAQE XETA]", e)

def hedefleri_oxu() -> list[str]:
    if not os.path.exists(HEDEF_DOSYASI):
        os.makedirs(os.path.dirname(HEDEF_DOSYASI), exist_ok=True)
        with open(HEDEF_DOSYASI, "w", encoding="utf-8") as f:
            f.write("")
        return []
    try:
        with open(HEDEF_DOSYASI, "r", encoding="utf-8") as f:
            adlar = [
                s.lstrip("@").strip()
                for s in f
                if s.lstrip("@").strip() and not s.strip().startswith("#")
            ]
        return list(dict.fromkeys(adlar))
    except Exception as e:
        print("[FAYL OXUMA XETASI]", e)
        return []

def siyahidan_sil(kullanici_adi: str):
    if kullanici_adi in canli_siyahisi:
        canli_siyahisi.remove(kullanici_adi)
    dinlenenler.pop(kullanici_adi, None)
    if os.path.exists(HEDEF_DOSYASI):
        try:
            with open(HEDEF_DOSYASI, "r", encoding="utf-8") as f:
                setirler = f.readlines()
            yeni_setirler = [
                s for s in setirler
                if s.lstrip("@").strip() != kullanici_adi
            ]
            with open(HEDEF_DOSYASI, "w", encoding="utf-8") as f:
                f.writelines(yeni_setirler)
        except Exception as e:
            print("[SILME XETASI]", e)
    print(f"[x] Silindi: @{kullanici_adi} | Aktiv: {len(canli_siyahisi)}")

def sandiq_bildirimi_gonder(yayinci: str, gonderen: str = "", basliq: str = "SANDIQ / KONVERT"):
    global sayac_id
    sayac_id += 1
    maska = ad_maskala(gonderen or yayinci)
    araliq = vaxt_araligi(120)
    mesaj = (
        f"RadarBot\n"
        f"🎉🎉🎉 {basliq} 🎉🎉🎉\n"
        f"## T{sayac_id} › {maska}\n"
        f"🕒 TIME : {araliq}\n"
        f"https://www.tiktok.com/@{yayinci}/live"
    )
    bildirim_gonder(mesaj)

async def yayini_izle(kullanici_adi: str):
    client = TikTokLiveClient(unique_id=kullanici_adi)

    @client.on(ConnectEvent)
    async def on_connect(event: ConnectEvent):
        print(f"[+] Baglandi: @{kullanici_adi}")

    @client.on(EnvelopeEvent)
    async def on_envelope(event):
        gonderen = ""
        try:
            gonderen = getattr(getattr(event, "user", None), "unique_id", "") or ""
        except Exception:
            pass
        print(f"[SANDIQ / ENVELOPE] @{kullanici_adi}")
        sandiq_bildirimi_gonder(kullanici_adi, gonderen=gonderen, basliq="SANDIQ / KONVERT")

    @client.on(GiftEvent)
    async def on_gift(event: GiftEvent):
        hediye_adi = getattr(event.gift, "name", "") or ""
        if any(k in hediye_adi.lower() for k in ("chest", "sandiq", "treasure", "box", "bag", "envelope")):
            gonderen = ""
            try:
                gonderen = getattr(getattr(event, "user", None), "unique_id", "") or ""
            except Exception:
                pass
            print(f"[HEDIYYE] @{kullanici_adi} -> {hediye_adi}")
            sandiq_bildirimi_gonder(kullanici_adi, gonderen=gonderen, basliq=hediye_adi.upper())

    try:
        await client.start()
    except Exception as e:
        print(f"[-] @{kullanici_adi} xeta / bitdi: {e}")
    finally:
        siyahidan_sil(kullanici_adi)

async def radar_dongusu():
    bildirim_gonder("TikTok Sandiq Radari hazirdir. hedefler.txt izlenir ve bitenler silinir.")
    while True:
        for u in hedefleri_oxu():
            if u not in canli_siyahisi and len(canli_siyahisi) < 20:
                canli_siyahisi.append(u)

        for u in list(canli_siyahisi):
            if u not in dinlenenler:
                dinlenenler[u] = asyncio.create_task(yayini_izle(u))

        print(f"[~] Aktiv siyahı ({len(canli_siyahisi)}): {canli_siyahisi}")
        await asyncio.sleep(3)

if __name__ == "__main__":
    asyncio.run(radar_dongusu())
    
