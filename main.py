import time
import asyncio
import requests
from playwright.async_api import async_playwright
import re
import os

TOKEN ="8807351971:AAEvFrk-l-BYVE3n4DVCFOS_bfzrkXSYHVw"

CHAT_ID = "6837476103"

message_id = None

async def get_automatic_live_accounts_browser():
    """Playwright ilə səhifəni aşağı sürüşdürərək canlı yayımları avtomatik tapır"""
    accounts = []
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True, args=["--no-sandbox", "--disable-setuid-sandbox"])
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
            page = await context.new_page()
            
            # TikTok live səhifəsinə daxil oluruq
            await page.goto("https://www.tiktok.com/live", timeout=60000)
            
            # Səhifənin elementləri yüklənməsi üçün gözləyirik
            await page.wait_for_timeout(7000)
            
            # Canlı yayımların yüklənməsi üçün səhifəni aşağı scroll edirik
            for _ in range(3):
                await page.evaluate("window.scrollTo(0, document.body.scrollHeight);")
                await page.wait_for_timeout(3000)
            
            # Səhifənin mətnini çəkib uniqueId-ləri tapırıq
            content = await page.content()
            matches = re.findall(r'"uniqueId":"([^"]+)"', content)
            if matches:
                accounts = list(set(matches))
                
            await browser.close()
    except Exception as e:
        print(f"Playwright xətası: {e}")
        
    print(f"Tapılan hesablar (Brauzer): {len(accounts)} ədəd")
    return accounts

def send_or_update_report(text):
    global message_id
    url_send = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    url_edit = f"https://api.telegram.org/bot{TOKEN}/editMessageText"

    if not message_id:  
        payload = {"chat_id": CHAT_ID, "text": text, "parse_mode": "HTML", "disable_web_page_preview": True}  
        try:  
            res = requests.post(url_send, json=payload).json()  
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
            if not res.get("ok"):  
                message_id = None
        except Exception as e:
            print(f"Mesaj yeniləmə xətası: {e}")  

async def main():
    print("Avtomatik Playwright sistemi işə düşdü...")
    while True:
        auto_accounts = await get_automatic_live_accounts_browser()
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
            print("Canlı tapılmadı.")
            
        await asyncio.sleep(30)

if __name__ == '__main__':
    asyncio.run(main())
    
