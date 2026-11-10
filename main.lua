local http = require("socket.http")
local ltn12 = require("ltn12")
local json = require("cjson")

local TOKEN = "8807351971:AAEvFrk-l-BYVE3n4DVCFOS_bfzrkXSYHVw"
local CHAT_ID = "6837476103"
local message_id = nil

local function send_or_update_report(text)
    local url
    local payload = {
        chat_id = CHAT_ID,
        text = text,
        parse_mode = "HTML",
        disable_web_page_preview = true
    }

    if message_id == nil then
        url = "https://api.telegram.org/bot" .. TOKEN .. "/sendMessage"
    else
        url = "https://api.telegram.org/bot" .. TOKEN .. "/editMessageText"
        payload.message_id = message_id
    end

    local response_body = {}
    local _, code = http.request{
        url = url,
        method = "POST",
        headers = { ["Content-Type"] = "application/json" },
        source = ltn12.source.string(json.encode(payload)),
        sink = ltn12.sink.table(response_body)
    }

    if code == 200 then
        local data = json.decode(table.concat(response_body))
        if data.ok and message_id == nil then
            message_id = data.result.message_id
        end
    else
        message_id = nil
    end
end

print("100 - 10000+ Jeton Sandıq Filtri İşə Düşdü...")

while true do
    local response_body = {}
    local _, code = http.request{
        url = "https://www.tiktok.com/live",
        sink = ltn12.sink.table(response_body)
    }

    if code == 200 then
        local html = table.concat(response_body)
        
        local found_valid_box = false
        local target_user = "Bilinmir"
        local box_value = 0

        -- Səhifədəki coinCount dəyərlərini yoxlayırıq (100 və yuxarı)
        for uid, coins in html:gmatch('"uniqueId":"([^"]+)".-("coinCount":(%d+))') do
            local coin_num = tonumber(coins)
            -- 100, 1000, 5000, 8000, 10000 və daha yuxarı sandıqları qəbul edir
            if coin_num and coin_num >= 100 then
                target_user = uid
                box_value = coin_num
                found_valid_box = true
                break
            end
        end

        if found_valid_box then
            local current_time = os.date("%H:%M:%S")
            
            -- Jeton dəyərinə görə xüsusi işarə təyin edirik
            local badge = "🎁 Standart Sandıq"
            if box_value >= 10000 then
                badge = "🔥 <b>ƏLA DƏYƏRLİ VIP SANDIQ (10K+)</b>"
            elseif box_value >= 5000 then
                badge = "💎 <b>BÖYÜK SANDIQ (5K+)</b>"
            elseif box_value >= 1000 then
                badge = "⭐ <b>1K+ Jetonluq Sandıq</b>"
            end

            local report_text = string.format(
                "%s\n\n" ..
                "👤 Kanal: <b>@%s</b>\n" ..
                "💰 Jeton Məbləği: <b>%d Jeton</b>\n" ..
                "🔗 Link: https://www.tiktok.com/@%s/live\n\n" ..
                "━━━━━━━━━━━━━━━━━━━\n" ..
                "🕒 Vaxt: <code>%syi</code>",
                badge, target_user, box_value, target_user, current_time
            )

            send_or_update_report(report_text)
        else
            print("100-dən aşağı yayımlar və ya sandıqsızlar filtrləndi...")
        end
    else
        print("Bağlantı xətası, kod:", code)
    end

    os.execute("sleep 30")
end
