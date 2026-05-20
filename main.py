import os
import base64
import requests
from flask import Flask, render_template, request, jsonify, session
from dotenv import load_dotenv

# Configuración de la aplicación Flask
app = Flask(__name__)
app.secret_key = "vega_ai_local_emergency"

load_dotenv()

# --- CONFIGURACIÓN DE INTEGRACIÓN ---
HF_API_KEY = os.getenv("HUGGINGFACE_API_KEY")
URL_IMAGEN = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"

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

        # --- 1. MODO: GENERACIÓN DE IMÁGENES (Sigue intentando conectar si lo pides) ---
        disparadores = ["dibuja", "genera una imagen", "crea una imagen", "hazme un dibujo", "imagen de"]
        pide_imagen = any(palabra in mensaje_usuario.lower() for palabra in disparadores)

        if pide_imagen:
            try:
                print(f"[IMAGEN] Intentando conectar a Hugging Face para: {mensaje_usuario}")
                headers_hf = {"Authorization": f"Bearer {HF_API_KEY}"}
                response_hf = requests.post(URL_IMAGEN, headers=headers_hf, json={"inputs": mensaje_usuario}, timeout=5)
                
                if response_hf.status_code == 200:
                    imagen_bytes = response_hf.content
                    imagen_base64 = base64.b64encode(imagen_bytes).decode('utf-8')
                    respuesta_html = (
                        f'<div>'
                        f'<p>¡Logré conectar! Aquí tienes tu imagen:</p>'
                        f'<img src="data:image/jpeg;base64,{imagen_base64}" style="width:100%; border-radius:10px; margin-top:10px; border: 2px solid #2ecc71;">'
                        f'</div>'
                    )
                    return jsonify({"respuesta": respuesta_html})
            except Exception:
                return jsonify({"respuesta": "El motor de imágenes no pudo salir a internet. Revisa tu conexión de red."})

        # --- 2. MODO: CHAT DE TEXTO (100% LOCAL / SIN INTERNET) ---
        print(f"[TEXTO LOCAL] Procesando: {mensaje_usuario}")
        
        # Respuestas automáticas preprogramadas para probar tu diseño gráfico
        saludos = ["hola", "buenas", "que tal", "saludos", "buenos dias"]
        if any(s in mensaje_usuario.lower() for s in saludos):
            respuesta_local = "¡Hola! Soy Vega AI en modo de diagnóstico local. Tu panel de control y diseño de chat funcionan correctamente a nivel de servidor. ¿Qué componente deseas probar hoy?"
        else:
            respuesta_local = f"Recibí tu mensaje: '{mensaje_usuario}'. El sistema de chat está respondiendo en modo local fuera de línea para verificar que el flujo de tu interfaz de usuario funciona sin bloqueos."

        return jsonify({"respuesta": respuesta_local})

    except Exception as e:
        print(f"Error crítico: {str(e)}")
        return jsonify({"respuesta": f"Error interno de Vega AI: {str(e)}"}), 500

@app.route("/reset", methods=["POST"])
def reset():
    session.pop("historial", None)
    return jsonify({"status": "ok"})

if __name__ == "__main__":
    app.run(port=5000, debug=True)