import os
import io
import json
import pandas as pd
from flask import Flask, render_template, request, jsonify, session, send_file
from dotenv import load_dotenv
from google import genai
from google.genai import types
from pydantic import BaseModel, Field
from typing import List, Optional

load_dotenv()

app = Flask(__name__)
app.secret_key = "vega_ai_final_stable_diffusion_2026"

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# Definimos la estructura exacta que queremos que nos devuelva Gemini obligatoriamente
class VegaTablaSchema(BaseModel):
    texto_introductorio: str = Field(description="Texto, saludo o explicación antes de mostrar los datos.")
    tiene_datos_tabulares: bool = Field(description="True si el usuario pidió una lista, ranking, comparativa o datos organizables en tabla.")
    columnas: List[str] = Field(description="Lista con los nombres de las columnas para la tabla. Vacío si no hay datos.")
    filas: List[List[str]] = Field(description="Lista de filas, donde cada fila es una lista de strings con el contenido de las celdas en el mismo orden que las columnas.")

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
            prompt_limpio = mensaje_usuario.lower()
            for d in disparadores:
                prompt_limpio = prompt_limpio.replace(d, "")
            prompt_limpio = prompt_limpio.strip()
            prompt_final = "cyberpunk futuristic car" if not prompt_limpio else prompt_limpio
            prompt_url = prompt_final.replace(" ", "%20")
            url_imagen = f"https://image.pollinations.ai/prompt/{prompt_url}?width=800&height=800&model=turbo&nologo=true"
            
            respuesta_html = (
                f'<div><p>¡Aquí tienes tu imagen generada por IA!</p>'
                f'<img src="{url_imagen}" style="width:100%; max-width:500px; display:block; border-radius:10px; margin-top:10px;" alt="Imagen Vega AI"></div>'
            )
            return jsonify({"respuesta": respuesta_html})

        # --- MODO CHAT TEXTO INTELIGENTE CON RESPUESTA ESTRUCTURADA ---
        if "historial_textos" not in session:
            session["historial_textos"] = [
                {"role": "user", "text": "Eres Vega AI, un asistente experto en análisis y visualización de datos de mercado de alta precisión."},
                {"role": "model", "text": "Entendido. Procesaré la información solicitada de forma profesional."}
            ]

        session["historial_textos"].append({"role": "user", "text": mensaje_usuario})

        # Reconstruimos el formato nativo para enviar la petición estructurada
        contents_input = []
        for h in session["historial_textos"]:
            contents_input.append(types.Content(role=h["role"], parts=[types.Part.from_text(text=h["text"])]))

        # Forzamos a Gemini 2.5 Flash a responder siguiendo nuestro esquema estricto de Pydantic
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=contents_input,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=VegaTablaSchema,
            ),
        )

        # Parseamos la respuesta JSON estructurada que nos da el modelo
        datos_ia = json.loads(response.text)
        
        texto_pantalla = datos_ia.get("texto_introductorio", "")
        tiene_tabla = datos_ia.get("tiene_datos_tabulares", False)
        columnas = datos_ia.get("columnas", [])
        filas = datos_ia.get("filas", [])

        # Guardamos la versión en texto en la sesión para el contexto del chat continuo
        session["historial_textos"].append({"role": "model", "text": texto_pantalla})
        session.modified = True

        tabla_markdown_cruda = ""
        
        # Si Gemini estructuró una tabla de datos, montamos el HTML e internamente el Markdown para el botón
        if tiene_tabla and columnas and filas:
            # 1. Generamos el HTML real de la tabla para que el navegador lo dibuje perfecto
            html_tabla = "<table><thead><tr>"
            for col in columnas:
                html_tabla += f"<th>{col}</th>"
            html_tabla += "</tr></thead><tbody>"
            
            for fila in filas:
                html_tabla += "<tr>"
                for celda in fila:
                    html_tabla += f"<td>{celda}</td>"
                html_tabla += "</tr>"
            html_tabla += "</tbody></table>"
            
            # Unimos la intro con el diseño de la tabla armada
            texto_pantalla = f"<div><p>{texto_pantalla}</p>{html_tabla}</div>"
            
            # 2. Reconstruimos un string Markdown limpio exclusivamente para pasarle a Pandas al descargar
            lineas_md = ["|" + "|".join(columnas) + "|"]
            lineas_md.append("|" + "|".join(["---"] * len(columnas)) + "|")
            for fila in filas:
                lineas_md.append("|" + "|".join(fila) + "|")
            tabla_markdown_cruda = "\n".join(lineas_md)

        return jsonify({
            "respuesta": texto_pantalla,
            "tiene_tabla": True if tabla_markdown_cruda else False,
            "tabla_html": tabla_markdown_cruda
        })

    except Exception as e:
        print(f"Error crítico en Gemini Estructurado: {str(e)}")
        return jsonify({"respuesta": "Error interno al procesar los datos estructurados en Vega AI."}), 500

@app.route("/exportar-excel", methods=["POST"])
def exportar_excel():
    try:
        tabla_md = request.form.get("tabla_data")
        if not tabla_md:
            return "No se encontraron datos para exportar", 400

        lineas = [l.strip() for l in tabla_md.strip().split("\n") if l.strip() and "|" in l]
        
        if len(lineas) > 1 and "---" in lineas[1]:
            lineas.pop(1)

        datos_finales = []
        for linea in lineas:
            celdas = [c.strip() for c in linea.split("|")[1:-1]]
            if celdas:
                datos_finales.append(celdas)

        df = pd.DataFrame(datos_finales[1:], columns=datos_finales[0])
        
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Vega AI Datos')
        output.seek(0)

        return send_file(
            output,
            mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            as_attachment=True,
            download_name="tabla_vega_ai.xlsx"
        )
    except Exception as e:
        print(f"Error al exportar: {str(e)}")
        return "Error al generar el archivo Excel", 500

@app.route("/reset", methods=["POST"])
def reset():
    session.pop("historial_textos", None)
    return jsonify({"status": "ok"})

if __name__ == "__main__":
    app.run(port=5000, debug=True)