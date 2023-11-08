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
ngrok_url = 'ea32-2a02-2498-4-7003-00-72e5.ngrok-free.app/webhook'  # Make sure this points to your webhook endpoint

result = set_telegram_webhook(bot_token, ngrok_url)
print(result)