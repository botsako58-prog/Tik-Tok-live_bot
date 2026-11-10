import time
import requests
import re
import json
import os

TOKEN = "8807351971:AAEvFrk-l-BYVE3n4DVCFOS_bfzrkXSYHVw"
CHAT_ID = "6837476103"

message_id = None

def get_automatic_live_accounts():
    """TikTok-un daxili API-si və səhifəsindən canlıda olanları avtomatik tapır"""
    accounts = []
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "az,en;q=0.9",
        "Referer": "https://www.tiktok.com/live"
    }
    
    try:
        # 1. TikTok Live API sorğusu
        api_url = "https://www.tiktok.com/api/recommend/live/room/?aid=1988&count=30"
        api_res = requests.get(api_url, headers=headers, timeout=10)
        data = api_res.json()
        
        if "data" in data and "rooms" in data["data"]:
            for room in data["data"]["rooms"]:
                owner = room.get("owner", {})
                unique_id = owner.get("uniqueId")
                if unique_id:
                    accounts.append(unique_id)
    except Exception as e:
        print(f"API sorğu xətası: {e}")

    # 2. Əgər API-dən nəticə gəlməzsə, əsas səhifəni regex ilə yoxla
    if not accounts:
        try:
            url = "https://www.tiktok.com/live"
            response = requests.get(url, headers=headers, timeout=10)
            matches = re.findall(r'"uniqueId":"([^"]+)"', response.text)  
            if matches:  
                accounts = list(set(matches))  
        except Exception as e:  
            print(f"Səhifə sorğu xətası: {e}")  
      
    print(f"Tapılan hesablar: {len(accounts)} ədəd")
    return list(set(accounts))

def send_or_update_report(text):
    global message_id
    url_send = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    url_edit = f"https://api.telegram.org/bot{TOKEN}/editMessageText"

    if not message_id:  
        payload = {"chat_id": CHAT_ID, "text": text, "parse_mode": "HTML", "disable_web_page_preview": True}  
        try:  
            res = requests.post(url_send, json=payload).json()  
            print("Telegram-dan gələn cavab (Send):", res)
            if res.get("ok"):  
                message_id = res["result"]["message_id"]  
        except Exception as e:
            print(f"Mesaj göndərmə xətası: {e}")  
    else:  
        payload = {  
            "chat_id": CHAT_ID,  
            "message_id": message_id,  
            "text": text,  
            "parse_mode": "HTML",  
            "disable_web_page_preview": True  
        }  
        try:  
            res = requests.post(url_edit, json=payload).json()  
            print("Telegram-dan gələn cavab (Edit):", res)
            if not res.get("ok"):  
                message_id = None
        except Exception as e:
            print(f"Mesaj yeniləmə xətası: {e}")  

if __name__ == '__main__':
    print("Avtomatik sistem işə düşdü...")

    while True:  
        auto_accounts = get_automatic_live_accounts()  
        total_found = len(auto_accounts)  
          
        if total_found > 0:  
            active_user = auto_accounts[0]  
            current_time = time.strftime("%H:%M:%S")  
              
            report_text = (  
                f"🔴 <b>Avtomatik Tapılan Canlı Yayım</b>\n\n"  
                f"👤 Kanal: <b>@{active_user}</b>\n"  
                f"🔗 Link: https://www.tiktok.com/@{active_user}/live\n\n"  
                f"━━━━━━━━━━━━━━━━━━━\n"  
                f"⚙️ <b>SİSTEM RAPORU</b>\n\n"  
                f"📊 Avtomatik Tapılan Canlı Sayı: <b>{total_found}</b>\n"  
                f"🕒 Son Güncelleme: <code>{current_time}</code>"  
            )  
            send_or_update_report(report_text)  
        else:
            print("Canlı tapılmadığı üçün Telegram-a mesaj göndərilmədi.")
          
        time.sleep(30)
        
