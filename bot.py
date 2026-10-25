import os
import time
import requests
from datetime import datetime

FOOTBALL_API_KEY = os.getenv("FOOTBALL_API_KEY")
FACEBOOK_PAGE_ID = os.getenv("FACEBOOK_PAGE_ID")
FACEBOOK_ACCESS_TOKEN = os.getenv("FACEBOOK_ACCESS_TOKEN")

API_URL = "https://v3.football.api-sports.io/fixtures"

# Intervalo entre verificações: 60 segundos
INTERVALO = 60

# Evita publicar repetidamente o mesmo acontecimento
publicados = set()


def obter_jogos():
    hoje = datetime.now().strftime("%Y-%m-%d")

    resposta = requests.get(
        API_URL,
        headers={"x-apisports-key": FOOTBALL_API_KEY},
        params={"date": hoje},
        timeout=30
    )

    resposta.raise_for_status()
    return resposta.json().get("response", [])


def publicar_facebook(mensagem):
    url = (
        f"https://graph.facebook.com/vXX.X/"
        f"{FACEBOOK_PAGE_ID}/feed"
    )

    resposta = requests.post(
        url,
        data={
            "message": mensagem,
            "access_token": FACEBOOK_ACCESS_TOKEN
        },
        timeout=30
    )

    resposta.raise_for_status()
    print("Publicação enviada:", resposta.json())


def executar():
    if not FOOTBALL_API_KEY:
        raise RuntimeError("Falta configurar FOOTBALL_API_KEY.")

    if not FACEBOOK_PAGE_ID or not FACEBOOK_ACCESS_TOKEN:
        raise RuntimeError(
            "Faltam as credenciais da página do Facebook."
        )

    while True:
        try:
            jogos = obter_jogos()

            for jogo in jogos:
                fixture = jogo["fixture"]
                equipas = jogo["teams"]
                golos = jogo["goals"]
                estado = fixture["status"]["short"]

                # Publica apenas jogos em andamento ou terminados
                if estado not in ("1H", "HT", "2H", "ET", "P", "FT"):
                    continue

                chave = (
                    str(fixture["id"]),
                    str(golos["home"]),
                    str(golos["away"]),
                    estado
                )

                if chave in publicados:
                    continue

                mensagem = (
                    "⚽ FUTEBOL EM DIRETO\n\n"
                    f"{equipas['home']['name']} "
                    f"{golos['home']} - {golos['away']} "
                    f"{equipas['away']['name']}\n\n"
                    f"Estado: {fixture['status']['long']}\n"
                    "#Futebol #Resultados"
                )

                publicar_facebook(mensagem)
                publicados.add(chave)

        except Exception as erro:
            print("Erro:", erro)

        time.sleep(INTERVALO)


if __name__ == "__main__":
    executar()
