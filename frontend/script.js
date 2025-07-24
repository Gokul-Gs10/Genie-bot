const chatForm = document.getElementById('chat-form');
const chatInput = document.getElementById('chat-input');
const chatMessages = document.getElementById('chatbot-messages');
const typingIndicator = document.getElementById('typing-indicator');
const quickReplies = document.getElementById('quick-replies');
const BOT_AVATAR = "genie_avatar.png";
const GENIE_AVATAR = "genie_avatar.png";
const USER_AVATAR = "user_avatar.png";
const chatbotContainer = document.getElementById('chatbot-container');
const chatbotTrigger = document.getElementById('chatbot-trigger');
const chatbotClose = document.getElementById('closeChatbot');
const lampImg = document.querySelector('.lamp-img');
const genieSound = document.getElementById('genie-sound');
const chatHistory = [];

// --- SOUND and VIBRATION logic ---
function playGenieSound() {
    try {
        genieSound.currentTime = 0;
        genieSound.play();
    } catch(_) {}
}
function shakeLamp() {
    lampImg.classList.add('shaking');
    setTimeout(()=>lampImg.classList.remove('shaking'), 500);
}

// Citation removal & rendering logic unchanged...
function removeCitations(content) {
    return content.replace(/\s*\[\d+\]/g, "");
}

function appendMessage(content, sender = 'bot', time = null) {
    if (sender === 'bot') content = removeCitations(content);
    const htmlContent = marked.parse(content);
    chatHistory.push({
        sender,
        content: htmlContent,
        time: time || (new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'}))
    });
    const row = document.createElement('div');
    row.classList.add('message-row', sender === 'bot' ? 'bot-row' : 'user-row');
    const avatar = document.createElement('img');
    avatar.src = sender === 'bot' ? BOT_AVATAR : USER_AVATAR;
    avatar.className = 'avatar';
    const bubble = document.createElement('div');
    bubble.classList.add('message-bubble', sender === 'bot' ? 'bot-bubble' : 'user-bubble');
    bubble.innerHTML = htmlContent;
    const stamp = document.createElement('div');
    stamp.className = "time-stamp";
    stamp.textContent = time || (new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'}));
    if (sender === 'bot') {
        row.appendChild(avatar); row.appendChild(bubble); row.appendChild(stamp);
    } else {
        row.appendChild(stamp); row.appendChild(bubble); row.appendChild(avatar);
    }
    chatMessages.appendChild(row);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Export to Word
function exportChatToWord() {
    let chatContent = "<html><head><meta charset='utf-8'><title>StartGenie Chat Export</title></head><body>";
    chatContent += "<h2>StartGenie Chat Conversation</h2>";
    chatHistory.forEach(msg => {
        let who = msg.sender === 'user' ? "You" : "StartGenie Bot";
        chatContent += `<p><strong>${who} [${msg.time}]:</strong></p>`;
        chatContent += msg.content;
    });
    chatContent += "</body></html>";
    let blob = new Blob([chatContent], { type: "application/msword" });
    let url = URL.createObjectURL(blob);
    let a = document.createElement("a");
    a.href = url;
    a.download = "startgenie_chat.doc";
    document.body.appendChild(a);
    a.click();
    setTimeout(() => {
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
    }, 0);
}

// Toggle chatbot pop-up/modal
function openChatbot() {
    chatbotContainer.style.display = 'flex';
    document.body.classList.add('chatbot-open');
    chatbotTrigger.style.display = 'none';
    chatInput.focus();
}
function closeChatbot() {
    chatbotContainer.style.display = 'none';
    document.body.classList.remove('chatbot-open');
    chatbotTrigger.style.display = 'flex';
}

window.onload = () => {
    appendMessage("<strong>Welcome to Genie! ✨</strong><br>How can I assist you today?");
    chatInput.focus();
    document.getElementById('exportChatBtn').addEventListener('click', exportChatToWord);

    chatbotContainer.style.display = 'none';
    chatbotTrigger.style.display = 'flex';
    document.body.classList.remove('chatbot-open');

    chatbotTrigger.onclick = () => {
        shakeLamp(); // vibration/animation on open
        playGenieSound();
        setTimeout(openChatbot, 400);
    };
    chatbotClose.onclick = closeChatbot;

    // Lamp sound and shake on hover (works for mouse)
    lampImg.addEventListener('mouseenter', () => {
        shakeLamp();
        playGenieSound();
    });

    // Optional: play sound on touchstart for touchscreen
    lampImg.addEventListener('touchstart', playGenieSound);

    // Lamp shake & sound on tap/click (in addition to .chatbotTrigger.onclick)
    lampImg.addEventListener('click', () => {
        shakeLamp();
        playGenieSound();
    });
};
window.quickReply = (text) => {
    chatInput.value = text;
    chatForm.dispatchEvent(new Event('submit', {cancelable:true, bubbles:true}));
};

function showTyping() { typingIndicator.style.display = 'flex'; }
function hideTyping() { typingIndicator.style.display = 'none'; }

chatForm.addEventListener('submit', async function(e) {
    e.preventDefault();
    const msg = chatInput.value.trim();
    if (!msg) return;
    appendMessage(msg, 'user');
    chatInput.value = '';
    showTyping();

    try {
        const response = await fetch("http://127.0.0.1:8000/ask_ai", {
            method: "POST",
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                prompt: msg,
                company_name: "TestCompany"
            }),
        });
        const data = await response.json();
        hideTyping();
        if (data && data.response) {
            appendMessage(data.response, 'bot');
        } else {
            appendMessage("Sorry, something went wrong.", 'bot');
        }
    } catch (err) {
        hideTyping();
        appendMessage("Network error. Please try again.", 'bot');
    }
});
