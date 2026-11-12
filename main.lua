
local http = require("ssl.https")
local ltn12 = require("ltn12")
local json = require("cjson")

local TOKEN = "AAHRvqJm6rkKE7p96peCjon4U5hVozE2sP8"
local CHAT_ID = "-1003835472130"

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
        headers = {
            ["Content-Type"] = "application/json"
        },
        source = ltn12.source.string(json.encode(payload)),
        sink = ltn12.sink.table(response_body)
    }

    local response = table.concat(response_body)

    print("Telegram HTTP:", code)
    print("Telegram cavabı:", response)

    local success, data = pcall(json.decode, response)

    if success and data.ok then
        if message_id == nil then
            message_id = data.result.message_id
        end
        print("Telegram mesajı göndərildi!")
        return true
    end

    if success and data.description then
        print("Telegram xətası:", data.description)

        if message_id ~= nil then
            message_id = nil
        end
    end

    return false
end

print("TikTok Sandıq Filtri başladıldı...")

while true do
    local response_body = {}

    local _, code = http.request{
        url = "https://www.tiktok.com/live",
        headers = {
            ["User-Agent"] = "Mozilla/5.0"
        },
        sink = ltn12.sink.table(response_body)
    }

    if tonumber(code) == 200 then
        local html = table.concat(response_body)

        local found_valid_box = false

        for uid, coins in html:gmatch(
            '"uniqueId"%s*:%s*"([^"]+)".-"coinCount"%s*:%s*(%d+)'
        ) do

            local box_value = tonumber(coins)

            if box_value and box_value >= 100 then
                local current_time = os.date("%H:%M:%S")

                local badge = "🎁 Standart Sandıq"

                if box_value >= 10000 then
                    badge = "🔥 <b>VIP SANDIQ (10K+)</b>"
                elseif box_value >= 5000 then
                    badge = "💎 <b>BÖYÜK SANDIQ (5K+)</b>"
                elseif box_value >= 1000 then
                    badge = "⭐ <b>1K+ SANDIQ</b>"
                end

                local report_text = string.format(
                    "%s\n\n" ..
                    "👤 Kanal: <b>@%s</b>\n" ..
                    "💰 Jeton: <b>%d</b>\n" ..
                    "🔗 Link: https://www.tiktok.com/@%s/live\n\n" ..
                    "🕒 Vaxt: <code>%s</code>",
                    badge, uid, box_value, uid, current_time
                )

                send_or_update_report(report_text)
                found_valid_box = true
                break
            end
        end

        if not found_valid_box then
            print("Uyğun sandıq tapılmadı.")
        end
    else
        print("TikTok bağlantı xətası:", code)
    end

    os.execute("sleep 1")
end
