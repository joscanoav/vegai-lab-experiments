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
    let text = userInput.value;
    if (!text.trim()) return;

    // Si estás en modo imagen, nos aseguramos de que el texto lleve un disparador para el backend
    if (currentMode === 'image') {
        const disparadores = ["dibuja", "genera una imagen", "crea una imagen", "hazme un dibujo", "imagen de"];
        const yaTieneDisparador = disparadores.some(palabra => text.toLowerCase().includes(palabra));
        if (!yaTieneDisparador) {
            text = "dibuja " + text;
        }
    }

    // 1. Añadir mensaje del usuario al chat
    addMessage(userInput.value, 'user'); // Muestra el texto original que escribió el usuario
    userInput.value = '';

    // 2. Mostrar mensaje de "pensando" o "generando"
    const textoPensando = currentMode === 'chat' ? "Vega AI está pensando..." : "Vega AI está generando tu imagen...";
    addMessage(textoPensando, 'ia');
    const pensandoMsg = chatBox.lastElementChild;

    try {
        // 3. Llamada al servidor Flask (Backend)
        const response = await fetch('/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ mensaje: text }) // Enviamos el texto (con el "dibuja " si aplica)
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
});

// --- FUNCIONES DE UI ---
function addMessage(text, sender) {
    const bubble = document.createElement('div');
    bubble.classList.add('bubble', sender === 'user' ? 'bubble-user' : 'bubble-ia');
    
    // Si el mensaje es de sistema, añadimos clase especial
    if (sender === 'system') bubble.classList.add('bubble-system');
    
    // SOLUCIÓN CLAVE: innerHTML interpreta etiquetas <img> en lugar de tratarlas como texto plano
    bubble.innerHTML = text;
    chatBox.appendChild(bubble);
    
    scrollToBottom();
}

function scrollToBottom() {
    chatBox.scrollTop = chatBox.scrollHeight;
}

function nuevoChat() {
    // Limpiamos la interfaz
    chatBox.innerHTML = '';
    
    // Llamar a /reset en el backend para limpiar la memoria de la sesión también
    fetch('/reset', { method: 'POST' });
}

// --- MENÚ HAMBURGUESA ---
const btn = document.querySelector('.hamburger-btn');
const sidebar = document.querySelector('.sidebar');
btn.addEventListener('click', () => sidebar.classList.toggle('active'));