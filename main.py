from flask import Flask, request, jsonify, Response
import requests
import os

app = Flask(__name__)

# Pegando os tokens e IDs do ambiente (Render)
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")
WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
PHONE_ID = os.getenv("PHONE_ID")

# DEBUG: imprime no log para garantir que o token está sendo carregado
print("VERIFY_TOKEN carregado:", VERIFY_TOKEN)


# ---------------------------
# ROTA GET: VALIDAÇÃO WEBHOOK
# ---------------------------
@app.route("/webhook", methods=["GET"])
def verify_webhook():
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    print("META GET:", mode, token, challenge)
    print("VERIFY_TOKEN atual:", VERIFY_TOKEN)

    if mode == "subscribe" and token == VERIFY_TOKEN:
        return Response(challenge, status=200, mimetype="text/plain")
    
    return "Erro de verificação", 403


# ---------------------------
# ROTA POST: RECEBER MENSAGENS  **(ALTERADA)**
# ---------------------------
@app.route("/webhook", methods=["POST"])
def receive_message():

    print("\n===== NOVA REQUISIÇÃO DO META =====")

    # Sempre imprime o body bruto
    raw = request.data.decode("utf-8")
    print("RAW BODY:", raw)

    # Tenta converter para JSON
    try:
        data = request.get_json()
        print("JSON PARSEADO:", data)
    except Exception as e:
        print("ERRO AO PARSEAR JSON:", e)

    print("====================================\n")

    return jsonify({"status": "ok"}), 200


# ---------------------------
# FUNÇÃO PARA ENVIAR MENSAGEM
# ---------------------------
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


# ---------------------------
# INICIALIZAÇÃO FLASK (RENDER)
# ---------------------------
if __name__ == "__main__":
    # Agora garantido que usa exatamente a porta definida pelo Render
    port = int(os.environ["PORT"])
    print("Rodando na porta:", port)
    app.run(host="0.0.0.0", port=port)
