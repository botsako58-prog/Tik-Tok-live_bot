
local http = require("ssl.https")
local ltn12 = require("ltn12")
local json = require("cjson")

-- OZ MELUMATLARINI YAZ
local TOKEN = "8807351971"
local CHAT_ID = "-1003835472130"

local function send_message(text)
    local payload = {
        chat_id = CHAT_ID,
        text = text
    }

    local body = {}

    local _, code = http.request{
        url = "https://api.telegram.org/bot"
            .. TOKEN .. "/sendMessage",
        method = "POST",
        headers = {
            ["Content-Type"] = "application/json"
        },
        source = ltn12.source.string(
            json.encode(payload)
        ),
        sink = ltn12.sink.table(body)
    }

    print("HTTP:", code)
    print("Cavab:", table.concat(body))
end

print("ALFA BOT BASLADI")

send_message("ALFA BOT AKTIVDIR ✅")

while true do
    os.execute("sleep 30")
end
