// Mazeo Neural Core v2.5 - Interaction Engine

const authOverlay = document.getElementById('auth-overlay');
const loginForm = document.getElementById('login-form');
const signupForm = document.getElementById('signup-form');
const loginContainer = document.getElementById('login-form-container');
const signupContainer = document.getElementById('signup-form-container');

const chatForm = document.getElementById('main-chat-form');
const chatInput = document.getElementById('user-query');
const chatViewport = document.getElementById('chat-viewport');
const processingMsg = document.getElementById('processing-msg');

const userDisplay = document.getElementById('user-display');
const usernameText = document.getElementById('username-display');
const userAvatarChar = document.getElementById('user-avatar-char');

// --- GOOGLE AUTH HANDLER ---
function handleCredentialResponse(response) {
    const responsePayload = decodeJwtResponse(response.credential);
    console.log("Google Login Attempt:", responsePayload);

    fetch('/api/google-login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            email: responsePayload.email,
            name: responsePayload.name,
            picture: responsePayload.picture
        })
    }).then(res => res.json()).then(data => {
        if (data.success) {
            completeAuth(data.user);
        }
    });
}

function decodeJwtResponse(token) {
    var base64Url = token.split('.')[1];
    var base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
    var jsonPayload = decodeURIComponent(atob(base64).split('').map(function (c) {
        return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2);
    }).join(''));
    return JSON.parse(jsonPayload);
}

// --- STANDARD AUTH LOGIC ---
function switchAuth(mode) {
    if (mode === 'signup') {
        loginContainer.style.display = 'none';
        signupContainer.style.display = 'block';
    } else {
        loginContainer.style.display = 'block';
        signupContainer.style.display = 'none';
    }
}

loginForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const username = document.getElementById('login-username').value;
    const password = document.getElementById('login-password').value;

    const res = await fetch('/api/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password })
    });
    const data = await res.json();

    if (data.success) {
        completeAuth(data.user);
    } else {
        showNeuralAlert(data.message);
    }
});

signupForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const username = document.getElementById('signup-username').value;
    const email = document.getElementById('signup-email').value;
    const password = document.getElementById('signup-password').value;

    const res = await fetch('/api/signup', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, email, password })
    });
    const data = await res.json();

    if (data.success) {
        showNeuralAlert("Neural identity initialized. Please authorize.");
        switchAuth('login');
    } else {
        showNeuralAlert(data.message);
    }
});

function completeAuth(user) {
    authOverlay.style.opacity = '0';
    setTimeout(() => authOverlay.style.display = 'none', 800);

    userDisplay.style.display = 'flex';
    usernameText.innerText = user.username;
    userAvatarChar.innerText = user.username[0].toUpperCase();
}

function showNeuralAlert(msg) {
    alert(`[SYSTEM]: ${msg}`);
}

async function logout() {
    window.location.reload();
}

// --- CHAT LOGIC ---
chatForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const query = chatInput.value.trim();
    if (!query) return;

    appendNeuralMessage('user', query);
    chatInput.value = '';
    processingMsg.style.display = 'block';

    try {
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: query })
        });
        const data = await response.json();
        appendNeuralMessage('ai', data.response);
    } catch (err) {
        appendNeuralMessage('ai', "**Neural Sync Failed.** Check source connection.");
    } finally {
        processingMsg.style.display = 'none';
        scrollViewport();
    }
});

function appendNeuralMessage(role, text) {
    const msgDiv = document.createElement('div');
    msgDiv.className = `msg ${role}`;
    const displayAvatar = role === 'ai' ? 'M' : usernameText.innerText[0].toUpperCase();
    const contentHtml = role === 'ai' ? marked.parse(text) : text;

    msgDiv.innerHTML = `
        <div class="tag-avatar">${displayAvatar}</div>
        <div class="bubble">${contentHtml}</div>
    `;
    chatViewport.appendChild(msgDiv);
    scrollViewport();
}

function scrollViewport() {
    chatViewport.scrollTo({ top: chatViewport.scrollHeight, behavior: 'smooth' });
}

// --- PWA INSTALLATION ---
let deferredPrompt;
window.addEventListener('beforeinstallprompt', (e) => {
    e.preventDefault();
    deferredPrompt = e;
    document.getElementById('mobile-install-banner').style.display = 'block';
});

async function installPWA() {
    if (deferredPrompt) {
        deferredPrompt.prompt();
        const { outcome } = await deferredPrompt.userChoice;
        if (outcome === 'accepted') {
            document.getElementById('mobile-install-banner').style.display = 'none';
        }
        deferredPrompt = null;
    }
}
// --- INITIALIZATION ---
window.addEventListener('load', async () => {
    try {
        const res = await fetch('/api/check_auth');
        const data = await res.json();
        if (data.authenticated) {
            completeAuth(data.user);
        }
    } catch (e) {
        console.log("Auth sync skipped.");
    }
});
