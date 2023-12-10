import requests



def set_telegram_webhook(bot_token, ngrok_url):
    # Make sure to add your bot token and the ngrok URL here
    method = "setWebhook"
    telegram_url = f"https://api.telegram.org/bot{bot_token}/{method}"
    webhook_url = f"{ngrok_url}"  # Your ngrok HTTPS URL should be here
    params = {"url": webhook_url}

    response = requests.get(telegram_url, params=params)
    return response.json()

# Replace 'YOUR_BOT_TOKEN' with your actual bot token and 'YOUR_NGROK_URL' with your ngrok URL
bot_token = '6819822176:AAHnYg7TVpRXaDE4Yt0F6du_WwfDmbDryX8'
ngrok_url = 'https://f5fa-41-42-6-195.ngrok-free.app/webhook'  # Make sure this points to your webhook endpoint
ngrok_url = 'https://publish-zakir.onrender.com/webhook'  # Make sure this points to your webhook endpoint

result = set_telegram_webhook(bot_token, ngrok_url)
print(result)