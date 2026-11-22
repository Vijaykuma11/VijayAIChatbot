
// =====================================
// VIJAY AI CHATBOT - FRONTEND JAVASCRIPT
// =====================================

const API_URL = "http://127.0.0.1:8000";

const newChatButton = document.getElementById("newChat");
const historyBox = document.getElementById("history");
const chatSearch = document.getElementById("chatSearch");
const messagesBox = document.getElementById("messages");
const chatForm = document.getElementById("chatForm");
const messageInput = document.getElementById("messageInput");
const sendButton = document.getElementById("sendButton");

const sidebar = document.querySelector(".sidebar");
const resizer = document.getElementById("sidebarResizer");

let conversationId = null;
let loadingElement = null;


// =====================================
// WELCOME SCREEN
// =====================================

function showWelcome() {
    messagesBox.innerHTML = `
        <div class="welcome">

            <div class="welcome-icon">🤖</div>

            <h1>Welcome to Vijay AI</h1>

            <p>Your intelligent assistant for learning, coding and productivity.</p>

            <div class="suggestion-grid">

                <button class="welcome-card"
                    data-prompt="Teach me Python programming from beginner level.">

                    <span>🐍</span>
                    <strong>Learn Python</strong>
                    <small>Learn programming step by step</small>

                </button>

                <button class="welcome-card"
                    data-prompt="Help me build a professional full-stack project.">

                    <span>💻</span>
                    <strong>Build a Project</strong>
                    <small>Create a web application</small>

                </button>

                <button class="welcome-card"
                    data-prompt="Help me prepare for a Software Developer interview.">

                    <span>🎯</span>
                    <strong>Interview Preparation</strong>
                    <small>Practice interview questions</small>

                </button>

                <button class="welcome-card"
                    data-prompt="Explain Artificial Intelligence in simple language.">

                    <span>🧠</span>
                    <strong>Explore AI</strong>
                    <small>Understand artificial intelligence</small>

                </button>

            </div>
        </div>
    `;
}


// =====================================
// WELCOME CARD CLICK
// =====================================

messagesBox.addEventListener("click", (event) => {

    const card = event.target.closest(".welcome-card");

    if (!card) return;

    messageInput.value = card.dataset.prompt;

    chatForm.requestSubmit();

});


// =====================================
// ADD MESSAGE
// =====================================

function addMessage(role, content) {

    const message = document.createElement("div");

    message.className = `message ${role}`;

    const heading = document.createElement("strong");

    heading.textContent = role === "user" ? "You" : "Vijay AI";

    const paragraph = document.createElement("p");

    paragraph.textContent = content || "";

    message.appendChild(heading);
    message.appendChild(paragraph);

    messagesBox.appendChild(message);

    messagesBox.scrollTop = messagesBox.scrollHeight;
}


// =====================================
// LOADING ANIMATION
// =====================================

function showLoading() {

    removeLoading();

    loadingElement = document.createElement("div");

    loadingElement.className = "message assistant loading";

    loadingElement.textContent = "Vijay AI is typing...";

    messagesBox.appendChild(loadingElement);

    messagesBox.scrollTop = messagesBox.scrollHeight;
}


function removeLoading() {

    if (loadingElement) {

        loadingElement.remove();

        loadingElement = null;
    }
}


// =====================================
// LOAD CHAT HISTORY
// =====================================

async function loadHistory() {

    try {

        const response = await fetch(`${API_URL}/conversations`);

        if (!response.ok) {
            throw new Error("History load failed");
        }

        const result = await response.json();

        const chats = Array.isArray(result)
            ? result
            : result.conversations || [];

        historyBox.innerHTML = "";

        const searchText = chatSearch.value.toLowerCase().trim();

        const filteredChats = chats.filter(chat =>
            (chat.title || "New Chat")
                .toLowerCase()
                .includes(searchText)
        );

        filteredChats.forEach(chat => {

            const item = document.createElement("div");

            item.className = "history-item";

            const title = document.createElement("button");

            title.className = "history-title";

            title.textContent = chat.title || "New Chat";

            title.onclick = () => openConversation(chat.id);


            const rename = document.createElement("button");

            rename.className = "rename-chat";

            rename.textContent = "Rename";

            rename.onclick = () => renameConversation(chat.id);


            const remove = document.createElement("button");

            remove.className = "delete-chat";

            remove.textContent = "Delete";

            remove.onclick = () => deleteConversation(chat.id);


            item.appendChild(title);
            item.appendChild(rename);
            item.appendChild(remove);

            historyBox.appendChild(item);

        });

    } catch (error) {

        console.error("History Error:", error);

    }
}


// =====================================
// OPEN CONVERSATION
// =====================================

async function openConversation(id) {

    try {

        const response = await fetch(
            `${API_URL}/conversations/${id}/messages`
        );

        if (!response.ok) {
            throw new Error("Messages load failed");
        }

        const result = await response.json();

        const chatMessages = Array.isArray(result)
            ? result
            : result.messages || [];

        conversationId = id;

        messagesBox.innerHTML = "";

        chatMessages.forEach(message => {

            addMessage(message.role, message.content);

        });

        messagesBox.scrollTop = messagesBox.scrollHeight;

    } catch (error) {

        console.error("Open Chat Error:", error);

        alert("Chat open nahi ho paya.");

    }
}


// =====================================
// RENAME CONVERSATION
// =====================================

async function renameConversation(id) {

    const newTitle = prompt("Naya chat name likhiye:");

    if (!newTitle || !newTitle.trim()) {
        return;
    }

    try {

        const response = await fetch(
            `${API_URL}/conversations/${id}/title`,
            {
                method: "PATCH",

                headers: {
                    "Content-Type": "application/json"
                },

                body: JSON.stringify({
                    title: newTitle.trim()
                })
            }
        );

        if (!response.ok) {
            throw new Error("Rename failed");
        }

        await loadHistory();

        alert("Chat renamed successfully!");

    } catch (error) {

        console.error("Rename Error:", error);

        alert("Chat rename nahi hua.");

    }
}


// =====================================
// DELETE CONVERSATION
// =====================================

async function deleteConversation(id) {

    const confirmDelete = confirm(
        "Kya aap is chat ko delete karna chahte hain?"
    );

    if (!confirmDelete) {
        return;
    }

    try {

        const response = await fetch(
            `${API_URL}/conversations/${id}`,
            {
                method: "DELETE"
            }
        );

        if (!response.ok) {
            throw new Error("Delete failed");
        }

        if (conversationId === id) {

            conversationId = null;

            showWelcome();

        }

        await loadHistory();

    } catch (error) {

        console.error("Delete Error:", error);

        alert("Chat delete nahi hui.");

    }
}


// =====================================
// NEW CHAT BUTTON
// =====================================

newChatButton.addEventListener("click", () => {

    conversationId = null;

    showWelcome();

    messageInput.focus();

});


// =====================================
// SEARCH CHAT
// =====================================

chatSearch.addEventListener("input", () => {

    loadHistory();

});


// =====================================
// SEND MESSAGE TO AI
// =====================================

chatForm.addEventListener("submit", async (event) => {

    event.preventDefault();

    const message = messageInput.value.trim();

    if (!message) {
        return;
    }

    addMessage("user", message);

    messageInput.value = "";

    sendButton.disabled = true;

    showLoading();

    try {

        const response = await fetch(`${API_URL}/chat`, {

            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({

                message: message,

                conversation_id: conversationId

            })

        });

        if (!response.ok) {
            throw new Error("Chat API failed");
        }

        const data = await response.json();

        if (data.conversation_id) {

            conversationId = data.conversation_id;

        }

        removeLoading();

        const aiReply =
            data.bot_response ||
            data.response ||
            data.reply ||
            data.message;

        if (!aiReply) {
            throw new Error("AI response field not found");
        }

        addMessage("assistant", aiReply);

        await loadHistory();

    } catch (error) {

        removeLoading();

        console.error("Chat Error:", error);

        addMessage(
            "assistant",
            "Server se connection nahi ho pa raha. Backend aur Ollama check karein."
        );

    } finally {

        removeLoading();

        sendButton.disabled = false;

        messageInput.focus();

    }

});


// =====================================
// RESIZABLE SIDEBAR
// =====================================

if (resizer && sidebar) {

    let isResizing = false;

    resizer.addEventListener("pointerdown", (event) => {

        isResizing = true;

        resizer.setPointerCapture(event.pointerId);

        document.body.style.cursor = "col-resize";

        document.body.style.userSelect = "none";

    });


    resizer.addEventListener("pointermove", (event) => {

        if (!isResizing) return;

        const minWidth = 200;

        const maxWidth = Math.min(450, window.innerWidth - 250);

        const newWidth = Math.max(
            minWidth,
            Math.min(maxWidth, event.clientX)
        );

        sidebar.style.width = `${newWidth}px`;

        sidebar.style.flexBasis = `${newWidth}px`;

    });


    function stopResizing() {

        isResizing = false;

        document.body.style.cursor = "";

        document.body.style.userSelect = "";

    }


    resizer.addEventListener("pointerup", stopResizing);

    resizer.addEventListener("pointercancel", stopResizing);

}


// =====================================
// START APPLICATION
// =====================================

console.log("VIJAY AI NEW VERSION LOADED");

showWelcome();

loadHistory();
