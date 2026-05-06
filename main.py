import os
from flask import Flask, render_template, request, jsonify, session
import google.generativeai as genai
from dotenv import load_dotenv

app = Flask(__name__)
app.secret_key = "clave_secreta_super_segura"

load_dotenv()
genai.configure(api_key=os.environ.get("GOOGLE_API_KEY"))

def obtener_prompt_personalidad():
    return "Eres un asistente experto en software, directo y profesional."

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    mensaje = data.get("mensaje")
    
    if "historial" not in session:
        session["historial"] = []
    
    historial = session["historial"]
    historial.append({"role": "user", "parts": [mensaje]})

    model = genai.GenerativeModel("gemini-1.0-pro", system_instruction=obtener_prompt_personalidad())
    chat_session = model.start_chat(history=historial[:-1])
    
    response = chat_session.send_message(mensaje)
    historial.append({"role": "model", "parts": [response.text]})
    session["historial"] = historial
    
    return jsonify({"respuesta": response.text})

@app.route("/reset", methods=["POST"])
def reset():
    session.pop("historial", None)
    return jsonify({"status": "ok"})

if __name__ == "__main__":
    app.run(port=5000, debug=True)