import os
import requests
from flask import Flask, render_template, request, jsonify, session
from dotenv import load_dotenv

app = Flask(__name__)
app.secret_key = "vega_ai_final_stable_diffusion_2026"

load_dotenv()

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

        # --- DETECTOR DE MODO IMAGEN ---
        disparadores = ["dibuja", "genera una imagen", "crea una imagen", "hazme un dibujo", "imagen de"]
        pide_imagen = any(palabra in mensaje_usuario.lower() for palabra in disparadores)

        if pide_imagen:
            print(f"[IA REAL] Generando imagen desde internet para: {mensaje_usuario}")
            
            # Limpiamos el texto para extraer solo la orden del usuario
            prompt_limpio = mensaje_usuario.lower()
            for d in disparadores:
                prompt_limpio = prompt_limpio.replace(d, "")
            prompt_limpio = prompt_limpio.strip()
            
            # Si detecta palabras clave en español, le damos un empujón en inglés para que la IA pinte perfecto
            if "coche" in prompt_limpio or "auto" in prompt_limpio:
                prompt_final = "cyberpunk futuristic car, neon lights, hyperrealistic, 4k resolution"
            else:
                prompt_final = prompt_limpio if prompt_limpio else "cyberpunk style landscape"

            # Formateamos los espacios para crear una URL web segura
            prompt_url = prompt_final.replace(" ", "%20")

            # ENDPOINT LIBRE DE POLLINATIONS PARA STABLE DIFFUSION (No requiere login)
            url_imagen = f"https://image.pollinations.ai/prompt/{prompt_url}?width=800&height=800&model=turbo&nologo=true"
            
            # Formateamos la respuesta HTML exacta que tu script.js inyectará directamente en el chat
            respuesta_html = (
                f'<div>'
                f'<p>¡Aquí tienes tu imagen generada por IA en tiempo real!</p>'
                f'<img src="{url_imagen}" style="width:100%; max-width:500px; display:block; border-radius:10px; margin-top:10px; border: 2px solid #3498db;" alt="Imagen Vega AI">'
                f'</div>'
            )
            return jsonify({"respuesta": respuesta_html})

        # --- MODO CHAT TEXTO ---
        saludos = ["hola", "buenas", "que tal"]
        if any(s in mensaje_usuario.lower() for s in saludos):
            respuesta_local = "¡Hola! Soy Vega AI. El motor gráfico por Inteligencia Artificial real está activo. Cambia al modo Imagen abajo y pídeme un coche futurista."
        else:
            respuesta_local = f"Procesando en modo texto: '{mensaje_usuario}'."
            
        return jsonify({"respuesta": respuesta_local})

    except Exception as e:
        print(f"Error crítico: {str(e)}")
        return jsonify({"respuesta": f"Error interno en el servidor."}), 500

@app.route("/reset", methods=["POST"])
def reset():
    session.pop("historial", None)
    return jsonify({"status": "ok"})

if __name__ == "__main__":
    app.run(port=5000, debug=True)