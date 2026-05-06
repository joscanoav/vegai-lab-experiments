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

// --- LÓGICA DE ENVÍO Y CONEXIÓN CON FLASK ---
chatForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const text = userInput.value;
    if (!text.trim()) return;

    // 1. Añadir mensaje del usuario al chat
    addMessage(text, 'user');
    userInput.value = '';

    if (currentMode === 'chat') {
        // 2. Mostrar mensaje de "pensando"
        addMessage("Vega AI está pensando...", 'ia');
        const pensandoMsg = chatBox.lastElementChild;

        try {
            // 3. Llamada al servidor Flask (Backend)
            const response = await fetch('/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ mensaje: text })
            });

            const data = await response.json();
            
            // 4. Eliminar "pensando" y mostrar respuesta real
            pensandoMsg.remove();

            if (data.respuesta) {
                addMessage(data.respuesta, 'ia');
            } else {
                addMessage("Error: " + (data.error || "No hubo respuesta del servidor."), 'ia');
            }
        } catch (error) {
            pensandoMsg.remove();
            console.error(error);
            addMessage("Error de conexión. ¿Está el servidor Flask corriendo?", 'ia');
        }
    } else {
        // Placeholder para modo imagen
        addMessage("La función de imágenes está en desarrollo.", 'ia');
    }
});

// --- FUNCIONES DE UI ---
function addMessage(text, sender) {
    const bubble = document.createElement('div');
    bubble.classList.add('bubble', sender === 'user' ? 'bubble-user' : 'bubble-ia');
    
    // Si el mensaje es de sistema, añadimos clase especial
    if (sender === 'system') bubble.classList.add('bubble-system');
    
    bubble.innerText = text;
    chatBox.appendChild(bubble);
    
    scrollToBottom();
}

function scrollToBottom() {
    chatBox.scrollTop = chatBox.scrollHeight;
}

function nuevoChat() {
    // Limpiamos solo la interfaz
    chatBox.innerHTML = '';
    
    // Opcional: Llamar a /reset en el backend si quieres limpiar la memoria de la sesión también
    fetch('/reset', { method: 'POST' });
}

// --- MENÚ HAMBURGUESA ---
const btn = document.querySelector('.hamburger-btn');
const sidebar = document.querySelector('.sidebar');
btn.addEventListener('click', () => sidebar.classList.toggle('active'));