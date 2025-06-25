from flask import Flask, request
import requests
from twilio.twiml.messaging_response import MessagingResponse

app = Flask(__name__)

def obtener_partidos_del_dia():
    url = "https://www.scorebat.com/video-api/v3/"
    response = requests.get(url)
    if response.status_code != 200:
        return "No pude obtener los datos de los partidos."
    data = response.json()
    partidos = data['response']
    if not partidos:
        return "No hay partidos disponibles hoy."
    
    resultados = []
    for partido in partidos:
        titulo = partido['title']
        enlace = partido['matchviewUrl']
        resultados.append(f"{titulo}\nVideo: {enlace}")
    return "\n\n".join(resultados)

@app.route("/whatsapp", methods=["POST"])
def responder():
    cuerpo = request.values.get('Body', '').strip().lower()
    respuesta = MessagingResponse()
    
    if "partidos" in cuerpo or "lista" in cuerpo or cuerpo == "todos":
        resumen = obtener_partidos_del_dia()
        respuesta.message(resumen)
    elif "marcador" in cuerpo:
        equipo = cuerpo.replace("marcador", "").strip()
        resumen = ""
        url = "https://www.scorebat.com/video-api/v3/"
        response = requests.get(url)
        if response.status_code != 200:
            resumen = "No pude obtener los datos."
        else:
            data = response.json()
            for partido in data['response']:
                if equipo.lower() in partido['title'].lower():
                    resumen = f"Resumen de {partido['title']}\nVideo: {partido['matchviewUrl']}"
                    break
            if resumen == "":
                resumen = "No encontré resumen para ese equipo."
        respuesta.message(resumen)
    else:
        respuesta.message("Hola 👋. Puedes escribir:\n- partidos (para lista completa)\n- marcador [nombre equipo]\nEjemplo: marcador Barcelona")
    return str(respuesta)
Actualizado para listar partidos del día

