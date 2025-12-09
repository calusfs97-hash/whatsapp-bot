from flask import Flask, request, jsonify, Response
import requests
import os

app = Flask(__name__)

# Pegando os tokens e IDs do ambiente (Render)
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")
WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
PHONE_ID = os.getenv("PHONE_ID")

# Rota GET para validação do webhook
@app.route("/webhook", methods=["GET"])
def verify_webhook():
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    # LOG de depuração para checar o token
    print("META GET:", mode, token, challenge)
    print("VERIFY_TOKEN atual:", VERIFY_TOKEN)

    if mode == "subscribe" and token == VERIFY_TOKEN:
        # Retorna o challenge como text/plain, como o Meta exige
        return Response(challenge, status=200, mimetype="text/plain")
    return "Erro de verificação", 403

# Rota POST para receber mensagens do WhatsApp
@app.route("/webhook", methods=["POST"])
def receive_message():
    data = request.get_json()

    try:
        message = data["entry"][0]["changes"][0]["value"]["messages"][0]
        number = message["from"]
        text = message.get("text", {}).get("body", "")
        print(f"Mensagem recebida de {number}: {text}")

        if text and text.lower().strip() == "oi":
            send_whatsapp_message(number, "Olá! Tudo bem? 😊")
    except Exception as e:
        print("Sem mensagem válida ou erro:", e)

    return jsonify({"status": "ok"}), 200

# Função para enviar mensagens via WhatsApp API
def send_whatsapp_message(to, text):
    url = f"https://graph.facebook.com/v17.0/{PHONE_ID}/messages"
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {"body": text}
    }
    resp = requests.post(url, headers=headers, json=payload)
    print("Envio status:", resp.status_code, resp.text)

# Inicialização do Flask usando a porta do Render
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)
