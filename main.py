import time
import requests
import json
import os

TOKEN = "8807351971:AAEvFrk-l-BYVE3n4DVCFOS_bfzrkXSYHVw"
CHAT_ID = "6837476103"

message_id = None

def get_automatic_live_accounts():
    """TikTok mobil/veb API nöqtələrindən istifadə edərək canlı yayımları avtomatik tapır"""
    accounts = []
    
    headers = {
        "User-Agent": "com.zhiliaoapp.musically/2023405040 (Linux; U; Android 13; tr_TR; SM-S918B; Build/TP1A.220606.010; PocketBuild/release)",
        "Accept": "application/json",
        "Accept-Language": "az-AZ,az;q=0.9,en-US;q=0.8,en;q=0.7",
        "X-Sec-Child-Token": "",
        "Cookie": "tt_webid=7000000000000000000;"
    }
    
    api_urls = [
        "https://api16-normal-useast5.tiktokv.com/aweme/v1/feed/?type=51&count=20",
        "https://www.tiktok.com/api/recommend/live/room/?aid=1988&count=30",
        "https://m.tiktok.com/api/live/list/?aid=1988&count=30"
    ]
    
    for api_url in api_urls:
        try:
            response = requests.get(api_url, headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                
                if "data" in data and "rooms" in data["data"]:
                    for room in data["data"]["rooms"]:
                        owner = room.get("owner", {})
                        unique_id = owner.get("uniqueId")
                        if unique_id:
                            accounts.append(unique_id)
                
                elif "aweme_list" in data:
                    for aweme in data["aweme_list"]:
                        if "live_room" in aweme and aweme["live_room"]:
                            owner = aweme["live_room"].get("owner", {})
                            unique_id = owner.get("uniqueId")
                            if unique_id:
                                accounts.append(unique_id)
                                
                if accounts:
                    break
        except Exception as e:
            continue

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
        
