// --- CONFIGURACIÓN E INICIALIZACIÓN ---
const chatBox = document.getElementById('chat-box');
const chatForm = document.getElementById('chat-form');
const userInput = document.getElementById('user-input');
let currentMode = 'chat';

// --- LÓGICA DE MODO (CHAT/IMAGEN) ---
function setMode(mode, btnElement) {
    currentMode = mode;
    
    // Cambiar estilo de botones
    document.querySelectorAll('.mode-btn').forEach(btn => btn.classList.remove('active'));
    btnElement.classList.add('active');
    
    // Cambiar placeholder
    userInput.placeholder = mode === 'chat' ? "Escribe tu pregunta..." : "Describe la imagen...";
    
    // Limpiar chat al cambiar modo
    chatBox.innerHTML = '';
    const systemMsg = document.createElement('div');
    systemMsg.classList.add('bubble', 'bubble-system');
    systemMsg.innerText = mode === 'chat' ? "--- Modo Chat activado ---" : "--- Modo Imagen activado ---";
    chatBox.appendChild(systemMsg);
}

// --- LÓGICA DE ENVÍO E INTERACCIÓN ---
chatForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    let text = userInput.value;
    if (!text.trim()) return;

    if (currentMode === 'image') {
        const disparadores = ["dibuja", "genera una imagen", "crea una imagen", "hazme un dibujo", "imagen de"];
        const yaTieneDisparador = disparadores.some(palabra => text.toLowerCase().includes(palabra));
        if (!yaTieneDisparador) {
            text = "dibuja " + text;
        }
    }

    addMessage(userInput.value, 'user');
    userInput.value = '';

    const textoPensando = currentMode === 'chat' ? "Vega AI está pensando..." : "Vega AI está generando tu imagen...";
    addMessage(textoPensando, 'ia');
    const pensandoMsg = chatBox.lastElementChild;

    try {
        const response = await fetch('/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ mensaje: text })
        });

        const data = await response.json();
        pensandoMsg.remove();

        if (data.respuesta) {
            addMessage(data.respuesta, 'ia');
            
            if (data.tiene_tabla && data.tabla_html) {
                const ultimaBurbujaIa = chatBox.lastElementChild;
                
                const wrapperBotones = document.createElement('div');
                wrapperBotones.className = 'export-container';
                wrapperBotones.style.cssText = 'display: flex; gap: 10px; margin-top: 15px; flex-wrap: wrap;';
                
                // ==========================================
                // 1. BOTÓN DE EXCEL
                // ==========================================
                const formExcel = document.createElement('form');
                formExcel.action = '/exportar-excel';
                formExcel.method = 'POST';
                formExcel.target = '_blank';
                formExcel.style.margin = '0';
                
                const inputData = document.createElement('input');
                inputData.type = 'hidden';
                inputData.name = 'tabla_data';
                inputData.value = data.tabla_html;
                
                const botonExcel = document.createElement('button');
                botonExcel.type = 'submit';
                botonExcel.className = 'btn-export btn-excel';
                botonExcel.style.cssText = 'background: #22c55e; color: white; border: none; padding: 10px 18px; border-radius: 8px; font-weight: 600; cursor: pointer; display: inline-flex; align-items: center; gap: 8px; transition: all 0.2s ease-in-out;';
                botonExcel.innerHTML = '📊 Descargar en Excel';
                
                botonExcel.onmouseover = () => { botonExcel.style.background = '#16a34a'; botonExcel.style.transform = 'translateY(-1px)'; };
                botonExcel.onmouseout = () => { botonExcel.style.background = '#22c55e'; botonExcel.style.transform = 'translateY(0)'; };
                
                formExcel.appendChild(inputData);
                formExcel.appendChild(botonExcel);
                wrapperBotones.appendChild(formExcel);

                // ==========================================
                // 2. BOTÓN DE PDF (MÁXIMA SEPARACIÓN ANTI-SOLAPAMIENTO)
                // ==========================================
                const botonPdf = document.createElement('button');
                botonPdf.type = 'button';
                botonPdf.className = 'btn-export btn-pdf';
                botonPdf.style.cssText = 'background: #ef4444; color: white; border: none; padding: 10px 18px; border-radius: 8px; font-weight: 600; cursor: pointer; display: inline-flex; align-items: center; gap: 8px; transition: all 0.2s ease-in-out;';
                botonPdf.innerHTML = '📄 Descargar en PDF';
                
                botonPdf.onmouseover = () => { botonPdf.style.background = '#dc2626'; botonPdf.style.transform = 'translateY(-1px)'; };
                botonPdf.onmouseout = () => { botonPdf.style.background = '#ef4444'; botonPdf.style.transform = 'translateY(0)'; };
                
                botonPdf.addEventListener('click', () => {
                    const tablaObjetivo = ultimaBurbujaIa.querySelector('table');
                    const parrafoIntro = ultimaBurbujaIa.querySelector('p');
                    const descripcionTexto = parrafoIntro ? parrafoIntro.innerText : "Reporte analítico de mercado estructurado.";

                    if (tablaObjetivo) {
                        const ventanaImpresion = window.open('', '_blank');
                        ventanaImpresion.document.write(`
                            <html>
                            <head>
                                <meta charset="UTF-8">
                                <title>Vega AI - Reporte Analítico</title>
                                <style>
                                    @media print {
                                        body {
                                            -webkit-print-color-adjust: exact;
                                            print-color-adjust: exact;
                                        }
                                    }
                                    body { 
                                        font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
                                        color: #0f172a; 
                                        margin: 50px; 
                                        line-height: 1.6;
                                        /* Correcciones críticas de tracking para el bug de la 'l' */
                                        letter-spacing: 0.03em !important;
                                        word-spacing: 0.05em;
                                        transform: translateZ(0);
                                        -webkit-transform: translateZ(0);
                                    }
                                    .header { border-bottom: 2px solid #1e3a8a; padding-bottom: 12px; margin-bottom: 25px; }
                                    h1 { color: #1e3a8a; font-size: 24px; margin: 0; font-weight: 700; letter-spacing: 0.02em; }
                                    .meta-tag { font-size: 10px; color: #64748b; text-transform: uppercase; letter-spacing: 0.1em; font-weight: bold; }
                                    .intro-text { color: #334155; font-size: 14px; margin-bottom: 30px; background: #f8fafc; padding: 15px; border-left: 4px solid #64748b; border-radius: 4px; }
                                    table { width: 100%; border-collapse: collapse; margin-top: 10px; font-size: 12px; text-align: left; }
                                    th { background-color: #0f172a; color: #ffffff; padding: 12px 14px; font-weight: 600; letter-spacing: 0.03em; }
                                    td { padding: 12px 14px; border-bottom: 1px solid #e2e8f0; color: #334155; letter-spacing: 0.03em; }
                                    tr:nth-child(even) td { background-color: #f8fafc; }
                                </style>
                            </head>
                            <body>
                                <div class="header">
                                    <span class="meta-tag">Vega AI • Documento Ejecutivo</span>
                                    <h1>Reporte de Datos Estructurados</h1>
                                </div>
                                <div class="intro-text">${descripcionTexto}</div>
                                ${tablaObjetivo.outerHTML}
                                <script>
                                    window.onload = function() { 
                                        setTimeout(() => { window.print(); window.close(); }, 350); 
                                    }
                                </script>
                            </body>
                            </html>
                        `);
                        ventanaImpresion.document.close();
                    }
                });
                
                wrapperBotones.appendChild(botonPdf);
                ultimaBurbujaIa.appendChild(wrapperBotones);
                scrollToBottom();
            }
        } else {
            addMessage("Error: " + (data.error || "No hubo respuesta del servidor."), 'ia');
        }
    } catch (error) {
        pensandoMsg.remove();
        console.error(error);
        addMessage("Error de conexión. ¿Está el servidor Flask corriendo?", 'ia');
    }
});

// --- FUNCIONES DE UI ---
function addMessage(text, sender) {
    const bubble = document.createElement('div');
    bubble.classList.add('bubble', sender === 'user' ? 'bubble-user' : 'bubble-ia');
    if (sender === 'system') bubble.classList.add('bubble-system');
    bubble.innerHTML = text;
    chatBox.appendChild(bubble);
    scrollToBottom();
}

function scrollToBottom() {
    chatBox.scrollTop = chatBox.scrollHeight;
}

function nuevoChat() {
    chatBox.innerHTML = '';
    fetch('/reset', { method: 'POST' });
}

const btn = document.querySelector('.hamburger-btn');
const sidebar = document.querySelector('.sidebar');
if(btn && sidebar) {
    btn.addEventListener('click', () => sidebar.classList.toggle('active'));
}

function toggleTheme() {
    const currentTheme = document.documentElement.getAttribute('data-theme');
    const themeButton = document.getElementById('theme-toggle');
    if (currentTheme === 'light') {
        document.documentElement.removeAttribute('data-theme');
        themeButton.innerHTML = '☀️ Modo Claro';
    } else {
        document.documentElement.setAttribute('data-theme', 'light');
        themeButton.innerHTML = '🌙 Modo Oscuro';
    }
}