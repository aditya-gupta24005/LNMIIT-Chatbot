import streamlit as st
import streamlit.components.v1 as components
import requests
import json

# ========== CONFIG ==========
BACKEND_URL = "http://127.0.0.1:8000/chat"

# ========== PAGE SETTINGS ==========
st.set_page_config(
    page_title="LNMIIT",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ========== INITIALIZE SESSION ==========
if "messages" not in st.session_state:
    st.session_state.messages = []

# ========== CHAT WIDGET HTML ==========
def create_chat_widget():
    messages_json = json.dumps(st.session_state.messages)
    
    html_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}
            
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
            }}
            
            .chat-widget {{
                width: 400px;
                height: 650px;
                background: white;
                border-radius: 20px;
                box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
                display: flex;
                flex-direction: column;
                overflow: hidden;
                animation: slideUp 0.4s ease-out;
            }}
            
            @keyframes slideUp {{
                from {{
                    transform: translateY(50px);
                    opacity: 0;
                }}
                to {{
                    transform: translateY(0);
                    opacity: 1;
                }}
            }}
            
            .chat-header {{
                background: linear-gradient(135deg, #002147 0%, #004080 100%);
                color: white;
                padding: 20px;
                display: flex;
                align-items: center;
                gap: 12px;
            }}
            
            .logo {{
                width: 45px;
                height: 45px;
                border-radius: 50%;
                background: white;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 24px;
                font-weight: bold;
                color: #002147;
            }}
            
            .chat-header-text h3 {{
                margin: 0;
                font-size: 1.15rem;
                font-weight: 600;
            }}
            
            .chat-header-text p {{
                margin: 0;
                font-size: 0.8rem;
                opacity: 0.9;
            }}
            
            .messages-container {{
                flex: 1;
                overflow-y: auto;
                padding: 20px;
                background: #f8f9fa;
                display: flex;
                flex-direction: column;
                gap: 12px;
            }}
            
            .messages-container::-webkit-scrollbar {{
                width: 6px;
            }}
            
            .messages-container::-webkit-scrollbar-track {{
                background: transparent;
            }}
            
            .messages-container::-webkit-scrollbar-thumb {{
                background: #cbd5e0;
                border-radius: 10px;
            }}
            
            .message {{
                display: flex;
                animation: fadeIn 0.3s ease-out;
            }}
            
            @keyframes fadeIn {{
                from {{
                    opacity: 0;
                    transform: translateY(10px);
                }}
                to {{
                    opacity: 1;
                    transform: translateY(0);
                }}
            }}
            
            .message.user {{
                justify-content: flex-end;
            }}
            
            .message.bot {{
                justify-content: flex-start;
            }}
            
            .message-content {{
                max-width: 75%;
                padding: 12px 16px;
                border-radius: 18px;
                font-size: 0.9rem;
                line-height: 1.5;
                word-wrap: break-word;
            }}
            
            .message.user .message-content {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                border-bottom-right-radius: 4px;
            }}
            
            .message.bot .message-content {{
                background: white;
                color: #2d3748;
                border-bottom-left-radius: 4px;
                box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
            }}
            
            .welcome-message {{
                text-align: center;
                color: #718096;
                font-size: 0.9rem;
                padding: 40px 20px;
            }}
            
            .welcome-message h4 {{
                color: #2d3748;
                margin-bottom: 10px;
                font-size: 1.1rem;
            }}
            
            .info-badge {{
                display: inline-block;
                background: #e6f2ff;
                color: #0066cc;
                padding: 6px 12px;
                border-radius: 12px;
                font-size: 0.75rem;
                margin: 4px;
            }}
            
            .typing-indicator {{
                display: flex;
                align-items: center;
                gap: 4px;
                padding: 12px 16px;
                background: white;
                border-radius: 18px;
                width: fit-content;
                box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
            }}
            
            .typing-indicator span {{
                width: 8px;
                height: 8px;
                background: #cbd5e0;
                border-radius: 50%;
                animation: typing 1.4s infinite;
            }}
            
            .typing-indicator span:nth-child(2) {{
                animation-delay: 0.2s;
            }}
            
            .typing-indicator span:nth-child(3) {{
                animation-delay: 0.4s;
            }}
            
            @keyframes typing {{
                0%, 60%, 100% {{
                    transform: translateY(0);
                }}
                30% {{
                    transform: translateY(-10px);
                }}
            }}
            
            .input-container {{
                padding: 16px;
                background: white;
                border-top: 1px solid #e2e8f0;
                display: flex;
                gap: 10px;
                align-items: center;
            }}
            
            #messageInput {{
                flex: 1;
                padding: 12px 16px;
                border: 2px solid #e2e8f0;
                border-radius: 25px;
                font-size: 0.9rem;
                outline: none;
                transition: border-color 0.3s;
            }}
            
            #messageInput:focus {{
                border-color: #667eea;
            }}
            
            #sendButton {{
                width: 44px;
                height: 44px;
                border: none;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                border-radius: 50%;
                cursor: pointer;
                display: flex;
                align-items: center;
                justify-content: center;
                transition: transform 0.2s;
                font-size: 20px;
            }}
            
            #sendButton:hover {{
                transform: scale(1.05);
            }}
            
            #sendButton:active {{
                transform: scale(0.95);
            }}
            
            #sendButton:disabled {{
                opacity: 0.5;
                cursor: not-allowed;
            }}
        </style>
    </head>
    <body>
        <div class="chat-widget">
            <div class="chat-header">
                <div class="logo">L</div>
                <div class="chat-header-text">
                    <h3>LNMIIT Assistant</h3>
                    <p>Ask me anything about LNMIIT</p>
                </div>
            </div>
            
            <div class="messages-container" id="messagesContainer">
                <div class="welcome-message" id="welcomeMessage">
                    <h4>👋 Welcome to LNMIIT!</h4>
                    <p>I'm here to help you with:</p>
                    <div>
                        <span class="info-badge">📚 Academics</span>
                        <span class="info-badge">🎓 Admissions</span>
                        <span class="info-badge">🎯 Clubs & Events</span>
                    </div>
                    <p style="margin-top: 16px;">Ask me anything!</p>
                </div>
            </div>
            
            <div class="input-container">
                <input 
                    type="text" 
                    id="messageInput" 
                    placeholder="Type your message..."
                    onkeypress="handleKeyPress(event)"
                />
                <button id="sendButton" onclick="sendMessage()">➤</button>
            </div>
        </div>
        
        <script>
            const BACKEND_URL = "{BACKEND_URL}";
            let messages = {messages_json};
            
            function renderMessages() {{
                const container = document.getElementById('messagesContainer');
                const welcomeMsg = document.getElementById('welcomeMessage');
                
                if (messages.length === 0) {{
                    if (welcomeMsg) welcomeMsg.style.display = 'block';
                    return;
                }}
                
                if (welcomeMsg) welcomeMsg.style.display = 'none';
                
                container.innerHTML = '';
                messages.forEach(msg => {{
                    const msgDiv = document.createElement('div');
                    msgDiv.className = `message ${{msg.role}}`;
                    msgDiv.innerHTML = `<div class="message-content">${{msg.content}}</div>`;
                    container.appendChild(msgDiv);
                }});
                
                container.scrollTop = container.scrollHeight;
            }}
            
            function showTypingIndicator() {{
                const container = document.getElementById('messagesContainer');
                const typingDiv = document.createElement('div');
                typingDiv.className = 'message bot';
                typingDiv.id = 'typingIndicator';
                typingDiv.innerHTML = `
                    <div class="typing-indicator">
                        <span></span>
                        <span></span>
                        <span></span>
                    </div>
                `;
                container.appendChild(typingDiv);
                container.scrollTop = container.scrollHeight;
            }}
            
            function hideTypingIndicator() {{
                const indicator = document.getElementById('typingIndicator');
                if (indicator) indicator.remove();
            }}
            
            async function sendMessage() {{
                const input = document.getElementById('messageInput');
                const sendBtn = document.getElementById('sendButton');
                const message = input.value.trim();
                
                if (!message) return;
                
                // Disable input
                input.disabled = true;
                sendBtn.disabled = true;
                
                // Add user message
                messages.push({{role: 'user', content: message}});
                renderMessages();
                input.value = '';
                
                // Show typing indicator
                showTypingIndicator();
                
                try {{
                    const response = await fetch(BACKEND_URL, {{
                        method: 'POST',
                        headers: {{'Content-Type': 'application/json'}},
                        body: JSON.stringify({{message: message}})
                    }});
                    
                    hideTypingIndicator();
                    
                    if (response.ok) {{
                        const data = await response.json();
                        const botReply = data.response || 'No reply from server.';
                        messages.push({{role: 'bot', content: botReply}});
                    }} else {{
                        messages.push({{role: 'bot', content: `⚠️ Server error (${{response.status}})`}});
                    }}
                }} catch (error) {{
                    hideTypingIndicator();
                    messages.push({{role: 'bot', content: `🚫 Unable to connect: ${{error.message}}`}});
                }}
                
                renderMessages();
                
                // Re-enable input
                input.disabled = false;
                sendBtn.disabled = false;
                input.focus();
                
                // Sync with Streamlit
                window.parent.postMessage({{
                    type: 'streamlit:setComponentValue',
                    value: messages
                }}, '*');
            }}
            
            function handleKeyPress(event) {{
                if (event.key === 'Enter') {{
                    sendMessage();
                }}
            }}
            
            // Initial render
            renderMessages();
            document.getElementById('messageInput').focus();
        </script>
    </body>
    </html>
    """
    
    return html_code

# ========== RENDER COMPONENT ==========
chat_html = create_chat_widget()
result = components.html(chat_html, height=700, scrolling=False)

# Update session state if component returns data
if result:
    st.session_state.messages = result