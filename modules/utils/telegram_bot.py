import requests

# Store your credentials here (or load via env vars or config later)
BOT_TOKEN = "8057700354:AAHhYwu2naR6ul5YTMQBaI_cO-_PNNDmwRc"
CHAT_ID = "675105848"

def send_message(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "HTML"
    }
    response = requests.post(url, data=payload)
    if response.status_code != 200:
        print(f"Failed to send message: {response.text}")
    else:
        print("Message sent to Telegram.")
