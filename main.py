import os
from flask import Flask, render_template, request, jsonify, session
import google.generativeai as genai
from dotenv import load_dotenv

app = Flask(__name__)
app.secret_key = "llave_maestra_vega"

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=api_key)

# --- DIAGNÓSTICO EN TERMINAL ---
print("--- VERIFICANDO MODELOS DISPONIBLES ---")
try:
    available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
    print(f"Modelos que tu llave puede usar: {available_models}")
    # Intentamos elegir el primero de la lista si existe, si no, usamos uno por defecto
    MODELO_A_USAR = available_models[0] if available_models else "models/gemini-1.5-flash"
    print(f"Seleccionado automáticamente: {MODELO_A_USAR}")
except Exception as e:
    print(f"Error al listar modelos: {e}")
    MODELO_A_USAR = "models/gemini-1.5-flash"

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json()
        mensaje = data.get("mensaje")
        
        # Reiniciar historial si hay error de formato
        if "historial" not in session or not isinstance(session.get("historial"), list):
            session["historial"] = []
        
        model = genai.GenerativeModel(MODELO_A_USAR)
        chat_session = model.start_chat(history=session["historial"])
        response = chat_session.send_message(mensaje)
        
        # Actualizar historial
        nuevo_historial = session["historial"]
        nuevo_historial.append({"role": "user", "parts": [mensaje]})
        nuevo_historial.append({"role": "model", "parts": [response.text]})
        session["historial"] = nuevo_historial
        
        return jsonify({"respuesta": response.text})

    except Exception as e:
        return jsonify({"respuesta": f"Error crítico: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(port=5000, debug=True)