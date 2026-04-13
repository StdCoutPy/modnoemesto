// ==========================
// CONFIG
// ==========================
const CHAT_API_URL = "/chat/api/";
const MAX_MEMORY = 20;
let chatMemory = [];
let isSending = false;

// ==========================
// INIT
// ==========================
document.addEventListener("DOMContentLoaded", () => {
    initChat();
});

function initChat() {
    const sendBtn = document.getElementById("send-message");
    const input = document.getElementById("chat-input");
    const helpBtn = document.getElementById("help-btn");
    const closeBtn = document.getElementById("close-chat");
    const fabBtn = document.getElementById("chat-fab");



    if (sendBtn) sendBtn.addEventListener("click", sendMessage);

    if (fabBtn) {
    fabBtn.addEventListener("click", sendMessage);}

    if (input) input.addEventListener("keydown", (e) => {
        if (e.key === "Enter" && !isSending) {
            e.preventDefault();
            sendMessage();
        }
    });
    if (helpBtn) helpBtn.addEventListener("click", openChat);
    if (closeBtn) closeBtn.addEventListener("click", closeChat);
}

// ==========================
// SEND MESSAGE
// ==========================
async function sendMessage() {
    if (isSending) return;

    const input = document.getElementById("chat-input");
    const text = input.value.trim();
    if (!text) return;

    isSending = true;

    addUserMessage(text);
    input.value = "";
    saveToMemory("user", text);

    const typingId = showTyping();

    try {
        const response = await fetch(CHAT_API_URL, {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({
                message: text,
                memory: chatMemory // Передаем историю для контекста
            })
        });

        const data = await response.json();
        removeTyping(typingId);

        // Исправлено: берем текст или ставим заглушку, чтобы не было ошибки "запуталась"
        const reply = data.reply || "Секундочку, подбираю варианты... ✨";
        const links = data.links || [];

        // Выводим текст бота
        typeAssistantMessage(reply);
        saveToMemory("assistant", reply);

        // Создаём кнопки
        const buttonContainer = document.getElementById("chat-buttons");
        if (buttonContainer) {
            buttonContainer.innerHTML = ""; // очищаем старые кнопки
            links.forEach(linkObj => {
                const btn = document.createElement("button");
                btn.className = "link-btn";

                // Исправлено: берем заголовок из объекта, присланного с сервера
                btn.innerText = linkObj.title || "Перейти";

                btn.onclick = () => {
                    window.location.href = linkObj.url;
                };

                buttonContainer.appendChild(btn);
            });
            scrollToBottom();
        }

    } catch (error) {
        console.error(error);
        removeTyping(typingId);
        addAssistantMessage("Ошибка соединения. Попробуйте позже.");
    }

    isSending = false;
}



// ==========================
// MEMORY
// ==========================
function saveToMemory(role, content) {
    chatMemory.push({role, content});
    if (chatMemory.length > MAX_MEMORY) chatMemory.shift();
}

// ==========================
// UI FUNCTIONS
// ==========================
function addUserMessage(text) {
    const messages = getMessagesContainer();
    const div = createMessage("user", text);
    messages.appendChild(div);
    scrollToBottom();
}

function addAssistantMessage(text) {
    const messages = getMessagesContainer();
    const div = createMessage("assistant", text);
    messages.appendChild(div);
    scrollToBottom();
}

// typing animation (letter by letter)
function typeAssistantMessage(text) {
    const messages = getMessagesContainer();
    const div = createMessage("assistant", "");
    messages.appendChild(div);

    const textNode = div.querySelector(".message-text");
    let i = 0;
    const speed = 15;

    function type() {
        if (i < text.length) {
            textNode.textContent += text.charAt(i);
            i++;
            scrollToBottom();
            setTimeout(type, speed);
        }
    }
    type();
}

// ==========================
// TYPING INDICATOR
// ==========================
function showTyping() {
    const id = "typing-" + Date.now();
    const messages = getMessagesContainer();
    const div = document.createElement("div");
    div.className = "message assistant-message";
    div.id = id;
    div.innerHTML = `
        <div class="message-content">
            <div class="message-text typing">
                печатает...
            </div>
        </div>
    `;
    messages.appendChild(div);
    scrollToBottom();
    return id;
}

function removeTyping(id) {
    const el = document.getElementById(id);
    if (el) el.remove();
}

// ==========================
// HELPERS
// ==========================
function createMessage(role, text) {
    const div = document.createElement("div");
    div.className = `message ${role}-message`;
    const safeText = escapeHtml(text);
    div.innerHTML = `
        <div class="message-content">
            <div class="message-text">${safeText}</div>
            <span class="message-time">${getCurrentTime()}</span>
        </div>
    `;
    return div;
}

function getMessagesContainer() {
    return document.querySelector(".chat-messages");
}

function scrollToBottom() {
    const container = getMessagesContainer();
    container.scrollTop = container.scrollHeight;
}

function getCurrentTime() {
    const d = new Date();
    return d.getHours().toString().padStart(2, "0") + ":" +
           d.getMinutes().toString().padStart(2, "0");
}

function escapeHtml(text) {
    const div = document.createElement("div");
    div.innerText = text;
    return div.innerHTML;
}

// ==========================
// OPEN / CLOSE CHAT
// ==========================
function openChat() {
    const chat = document.getElementById("chat-assistant");
    if (chat) chat.classList.add("active");
}

function closeChat() {
    const chat = document.getElementById("chat-assistant");
    if (chat) chat.classList.remove("active");
}