import requests


def send_whatsapp_message(phone_number, message):
    url = f"{settings.WHATSAPP_API_URL}/v1/messages"
    headers = {
        "Authorization": f"Bearer {settings.WHATSAPP_API_TOKEN}",
        "Content-Type": "application/json",
    }
    payload = {
        "to": phone_number,
        "type": "text",
        "text": {"body": message},
    }
    response = requests.post(url, json=payload, headers=headers)
    return response.json()
