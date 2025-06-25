from flask import Flask
from apscheduler.schedulers.background import BackgroundScheduler
from twilio.rest import Client
import requests
import time
import os

app = Flask(__name__)

# Configura estas variables con tus datos reales (mejor usa variables de entorno en Render)
TWILIO_SID = os.getenv("TWILIO_SID", "ACd18293e4bc9ffe7991e9e3fb47d7f1ae")
TWILIO_TOKEN = os.getenv("TWILIO_TOKEN", "0202c1d6d2cca2cfe5d3d100be552fcf")
WHATSAPP_FROM = os.getenv("WHATSAPP_FROM", "whatsapp:+14155238886")
WHATSAPP_TO = os.getenv("WHATSAPP_TO", "whatsapp:+17875131794")

API_KEY = os.getenv("FOOTBALL_API_KEY", "951440df0d8372075be0d77")
HEADERS = {
    "x-rapidapi-host": "v3.football.api-sports.io",
    "x-rapidapi-key": API_KEY
}

client = Client(TWILIO_SID, TWILIO_TOKEN)

estado_partidos = {}

def enviar_mensaje(texto):
    try:
        client.messages.create(
            body=texto,
            from_=WHATSAPP_FROM,
            to=WHATSAPP_TO
        )
        print(f"Mensaje enviado: {texto}")
    except Exception as e:
        print(f"Error enviando mensaje: {e}")

def obtener_partidos_live():
    url = "https://v3.football.api-sports.io/fixtures"
    params = {"date": time.strftime("%Y-%m-%d")}
    r = requests.get(url, headers=HEADERS, params=params)
    if r.status_code == 200:
        return r.json().get("response", [])
    return []

def obtener_eventos_partido(fixture_id):
    url = "https://v3.football.api-sports.io/fixtures/events"
    params = {"fixture": fixture_id}
    r = requests.get(url, headers=HEADERS, params=params)
    if r.status_code == 200:
        return r.json().get("response", [])
    return []

def chequear_eventos():
    global estado_partidos
    partidos = obtener_partidos_live()
    for partido in partidos:
        fixture_id = partido["fixture"]["id"]
        home = partido["teams"]["home"]["name"]
        away = partido["teams"]["away"]["name"]
        estado_actual = partido["fixture"]["status"]["short"]  # NS, 1H, HT, FT, etc.
        eventos = obtener_eventos_partido(fixture_id)

        anterior = estado_partidos.get(fixture_id, {"estado": None, "goles": {home: 0, away: 0}})

        # Avisar cuando comienza el partido
        if anterior["estado"] != "1H" and estado_actual == "1H":
            enviar_mensaje(f"⚽️ ¡Comenzó el partido! {home} vs {away}")

        # Contar goles actuales
        goles_actual = {home: 0, away: 0}
        for evento in eventos:
            if evento["type"] == "Goal":
                equipo = evento["team"]["name"]
                goles_actual[equipo] = goles_actual.get(equipo, 0) + 1

        # Avisar si hay goles nuevos
        for equipo in [home, away]:
            if goles_actual.get(equipo, 0) > anterior["goles"].get(equipo, 0):
                enviar_mensaje(f"⚽️ Gol de {equipo}! {home} {goles_actual.get(home,0)} - {goles_actual.get(away,0)} {away}")

        # Avisar cuando termina el partido
        if anterior["estado"] != "FT" and estado_actual == "FT":
            enviar_mensaje(f"🏁 ¡Finalizó el partido! {home} {goles_actual.get(home,0)} - {goles_actual.get(away,0)} {away}")

        # Guardar estado para la próxima consulta
        estado_partidos[fixture_id] = {"estado": estado_actual, "goles": goles_actual}

scheduler = BackgroundScheduler()
scheduler.add_job(chequear_eventos, 'interval', seconds=60)
scheduler.start()

@app.route("/")
def home():
    return "Bot funcionando - revisando partidos..."

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
