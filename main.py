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
    
    # Mobil brauzer və cihaz simulyasiyası üçün başlıqlar
    headers = {
        "User-Agent": "com.zhiliaoapp.musically/2023405040 (Linux; U; Android 13; tr_TR; SM-S918B; Build/TP1A.220606.010; PocketBuild/release)",
        "Accept": "application/json",
        "Accept-Language": "az-AZ,az;q=0.9,en-US;q=0.8,en;q=0.7",
        "X-Sec-Child-Token": "",
        "Cookie": "tt_webid=7000000000000000000;"
    }
    
    # Alternativ API endpoint-ləri
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
                
                # 1. Format: room list
                if "data" in data and "rooms" in data["data"]:
                    for room in data["data"]["rooms"]:
                        owner = room.get("owner", {})
                        unique_id = owner.get("uniqueId")
                        if unique_id:
                            accounts.append(unique_id)
                
                # 2. Format: aweme list
                elif "aweme_list" in data:
                    for aweme in data["aweme_list"]:
                        if "live_room" in aweme and aweme["live_room"]:
                            owner = aweme["live_room"].get("owner", {})
                            unique_id = owner.get("uniqueId")
                            if unique_id:
                                accounts.append(unique_id)
                                
                if accounts:
                    break # Əgər hesab tapıldısa, dig
