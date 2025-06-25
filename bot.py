from flask import Flask, request
import requests
from twilio.twiml.messaging_response import MessagingResponse

app = Flask(__name__)

def obtener_resumen_equipo(equipo):
    url = "https://www.scorebat.com/video-api/v3/"
    response = requests.get(url)
    if response.status_code != 200:
        return "No pude obtener los datos."
    data = response.json()
    for partido in data['response']:
        if equipo.lower() in partido['title'].lower():
            return f"Resumen de {partido['title']}\nVideo: {partido['matchviewUrl']}"
    return "No encontré resumen para ese equipo."

@app.route("/whatsapp", methods=["POST"])
def responder():
    cuerpo = request.values.get('Body', '').strip().lower()
    respuesta = MessagingResponse()
    if "marcador" in cuerpo:
        equipo = cuerpo.replace("marcador", "").strip()
        resumen = obtener_resumen_equipo(equipo)
        respuesta.message(resumen)
    else:
        respuesta.message("Hola 👋. Escribe:\nmarcador Barcelona\nmarcador Real Madrid\netc.")
    return str(respuesta)
