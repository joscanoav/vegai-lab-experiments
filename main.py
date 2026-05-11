import os
from flask import Flask, render_template, request, jsonify, session
import google.generativeai as genai
from openai import OpenAI
from dotenv import load_dotenv

# Configuración de la aplicación Flask
app = Flask(__name__)
app.secret_key = "vega_ai_master_key_v4" # Cambiada para limpiar sesiones antiguas

load_dotenv()

# --- CONFIGURACIÓN DE MOTORES (CLIENTES) ---
# Motor de Texto: Google Gemini
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Motor de Imagen: OpenAI DALL-E 3
client_openai = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def obtener_personalidad():
    return "Eres Vega AI, un asistente experto en software, directo y profesional."

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json()
        mensaje_usuario = data.get("mensaje")
        
        if not mensaje_usuario:
            return jsonify({"respuesta": "No he recibido ningún mensaje."})

        # --- 1. DETECTOR DE GENERACIÓN DE IMÁGENES ---
        # Si el mensaje contiene palabras clave, usamos DALL-E 3
        disparadores = ["dibuja", "genera una imagen", "crea una imagen", "hazme un dibujo", "imagen de"]
        pide_imagen = any(palabra in mensaje_usuario.lower() for palabra in disparadores)

        if pide_imagen:
            try:
                print(f"Generando imagen para: {mensaje_usuario}")
                response = client_openai.images.generate(
                    model="dall-e-3",
                    prompt=mensaje_usuario, # DALL-E 3 funciona mejor con el mensaje directo
                    size="1024x1024",
                    quality="standard",
                    n=1,
                )
                url_imagen = response.data[0].url
                
                # Devolvemos la imagen formateada en HTML para tu interfaz
                respuesta_html = (
                    f'<div>'
                    f'<p>He generado esta imagen para ti:</p>'
                    f'<img src="{url_imagen}" style="width:100%; border-radius:10px; margin-top:10px; border: 2px solid #3498db;">'
                    f'</div>'
                )
                return jsonify({"respuesta": respuesta_html})
            
            except Exception as e_img:
                print(f"Error en DALL-E: {e_img}")
                return jsonify({"respuesta": f"Lo siento, hubo un error al crear la imagen: {str(e_img)}"})

        # --- 2. LÓGICA DE CHAT DE TEXTO (GEMINI) ---
        if "historial" not in session:
            # Inicialización con personalidad
            session["historial"] = [
                {"role": "user", "parts": [obtener_personalidad()]},
                {"role": "model", "parts": ["Entendido. Soy Vega AI. ¿En qué puedo ayudarte?"]}
            ]
        
        historial = session["historial"]
        
        # Limpieza de seguridad si el formato del historial fallara
        if historial and not isinstance(historial[0].get('parts'), list):
            session.pop("historial", None)
            return jsonify({"respuesta": "Sesión reiniciada. Por favor, repite tu mensaje."})

        model = genai.GenerativeModel("gemini-1.5-flash")
        chat_session = model.start_chat(history=historial)
        
        response = chat_session.send_message(mensaje_usuario)
        
        # Guardar el intercambio en la sesión
        historial.append({"role": "user", "parts": [mensaje_usuario]})
        historial.append({"role": "model", "parts": [response.text]})
        session["historial"] = historial
        
        return jsonify({"respuesta": response.text})

    except Exception as e:
        print(f"Error crítico en el servidor: {str(e)}")
        return jsonify({"respuesta": f"Error interno de Vega AI: {str(e)}"}), 500

@app.route("/reset", methods=["POST"])
def reset():
    session.pop("historial", None)
    return jsonify({"status": "ok"})

if __name__ == "__main__":
    app.run(port=5000, debug=True)