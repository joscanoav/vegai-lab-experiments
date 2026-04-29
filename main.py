import os
from flask import Flask, render_template, request, jsonify, session
from groq import Groq
from dotenv import load_dotenv

# -----------------------------
# CONFIGURACIÓN INICIAL
# -----------------------------

app = Flask(__name__)
app.secret_key = "clave_secreta_super_segura"  # necesaria para sesiones

# -----------------------------
# FUNCIONES CORE
# -----------------------------

def cargar_api_key():
    load_dotenv()
    api_key = os.environ.get("GROQ_API_KEY")

    if not api_key:
        raise ValueError("❌ API KEY no encontrada en .env")

    return api_key


def crear_cliente_groq(api_key):
    return Groq(api_key=api_key)


def obtener_prompt_personalidad():
    """
    Aquí defines la personalidad de tu IA
    """
    return """
    Eres un asistente experto en desarrollo de software.

    Características:
    - Explicas paso a paso
    - Das ejemplos de código claros
    - Respondes siempre en español
    - Eres directo y sin rodeos
    - Corriges errores del usuario si los detectas

    Estilo:
    - Profesional pero cercano
    - Como un desarrollador senior mentor

    Objetivo:
    - Ayudar a aprender programación de forma práctica
    """


def obtener_respuesta_ia(cliente, historial):
    """
    Envía TODO el historial a la IA (memoria)
    """
    try:
        response = cliente.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=historial,
            temperature=0.7,
            max_tokens=1024
        )

        return response.choices[0].message.content

    except Exception as e:
        return f"⚠️ Error IA: {str(e)}"


# -----------------------------
# RUTAS
# -----------------------------

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json()
        mensaje_usuario = data.get("mensaje")

        if not mensaje_usuario:
            return jsonify({"error": "Mensaje vacío"}), 400

        # -------------------------
        # INICIALIZAR HISTORIAL
        # -------------------------
        if "historial" not in session:
            session["historial"] = [
                {"role": "system", "content": obtener_prompt_personalidad()}
            ]

        historial = session["historial"]

        # Agregar mensaje del usuario
        historial.append({
            "role": "user",
            "content": mensaje_usuario
        })

        # -------------------------
        # LLAMADA A IA
        # -------------------------
        api_key = cargar_api_key()
        cliente = crear_cliente_groq(api_key)

        respuesta_ia = obtener_respuesta_ia(cliente, historial)

        # Guardar respuesta en historial
        historial.append({
            "role": "assistant",
            "content": respuesta_ia
        })

        # Guardar sesión
        session["historial"] = historial

        return jsonify({"respuesta": respuesta_ia})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/reset", methods=["POST"])
def reset_chat():
    """
    Reinicia la conversación
    """
    session.pop("historial", None)
    return jsonify({"mensaje": "Chat reiniciado"})


# -----------------------------
# MAIN
# -----------------------------

def main():
    print("🚀 Servidor corriendo en http://127.0.0.1:5000")
    app.run(host="0.0.0.0", port=5000, debug=True)


if __name__ == "__main__":
    main()