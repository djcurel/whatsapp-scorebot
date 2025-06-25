from flask import Flask, request
import requests
from twilio.twiml.messaging_response import MessagingResponse

app = Flask(__name__)

def obtener_partidos_del_dia():
    url = "https://www.scorebat.com/video-api/v3/"
    try:
        response = requests.get(url)
        data = response.json()
        partidos = data.get('response', [])
        if not partidos:
            return "No hay partidos disponibles hoy."

        resultados = []
        for partido in partidos[:5]:  # solo mostrar 5 partidos
            titulo = partido['title']
            enlace = partido['matchviewUrl']
            resultados.append(f"{titulo}\nVideo: {enlace}")
        return "\n\n".join(resultados)
    except Exception as e:
        return f"Error al obtener los partidos: {e}"

def obtener_resumen_equipo(equipo):
    url = "https://www.scorebat.com/video-api/v3/"
    try:
        response = requests.get(url)
        data = response.json()
        partidos = data.get('response', [])
        for partido in partidos:
            if equipo.lower() in partido['title'].lower():
                return f"Resumen de {partido['title']}\nVideo: {partido['matchviewUrl']}"
        return f"No encontré resumen para {equipo}."
    except Exception:
        return "Hubo un error al buscar el marcador."

def obtener_partidos_mundial_clubes():
    url = "https://www.scorebat.com/video-api/v3/"
    try:
        response = requests.get(url)
        data = response.json()
        partidos = data.get('response', [])
        mundial_partidos = [p for p in partidos if "mundial" in p['title'].lower() or "clubes" in p['title'].lower()]
        if not mundial_partidos:
            return "No hay partidos del Mundial de Clubes disponibles."

        resultados = []
        for partido in mundial_partidos:
            titulo = partido['title']
            enlace = partido['matchviewUrl']
            resultados.append(f"{titulo}\nVideo: {enlace}")
        return "\n\n".join(resultados)

    except Exception as e:
        return f"Error al obtener partidos del Mundial de Clubes: {e}"

@app.route("/whatsapp", methods=["POST"])
def responder():
    cuerpo = request.values.get('Body', '').strip().lower()
    respuesta = MessagingResponse()

    if "partidos" in cuerpo or "lista" in cuerpo or cuerpo == "todos":
        resumen = obtener_partidos_del_dia()
        respuesta.message(resumen)
    elif "mundial" in cuerpo or "clubes" in cuerpo:
        resumen = obtener_partidos_mundial_clubes()
        respuesta.message(resumen)
    elif "marcador" in cuerpo:
        equipo = cuerpo.replace("marcador", "").strip()
        resumen = obtener_resumen_equipo(equipo)
        respuesta.message(resumen)
    else:
        respuesta.message(
            "Hola 👋. Puedes escribir:\n"
            "- partidos (para lista completa)\n"
            "- mundial (para partidos del Mundial de Clubes)\n"
            "- marcador [nombre equipo]\n"
            "Ejemplo: marcador Barcelona"
        )

    return str(respuesta)
