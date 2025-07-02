import requests
import time

API_URL = "http://localhost:8000/chat"  # ajuste se for diferente
SESSION_ID = "teste_davi"

messages = [
    "Olá! Meu nome é Davi.",
    "Como posso me cadastrar na plataforma?",
    "E depois que me cadastro, posso criar uma equipe?"
]

print(f"📡 Iniciando teste de sessão com ID: {SESSION_ID}\n")

for i, msg in enumerate(messages):
    print(f"🧑 Usuário: {msg}")
    response = requests.post(
        f"{API_URL}",
        json={"question": msg}
    )
    if response.ok:
        print(f"🤖 Bot: {response.json()['response']}\n")
    else:
        print(f"⚠️ Erro na requisição: {response.status_code}")
    time.sleep(1)
