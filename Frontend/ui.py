import streamlit as st
import streamlit.components.v1 as components
import json
import base64
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
BACKEND_URL = "http://127.0.0.1:8000/chat"
BG_FILENAME = os.path.join(current_dir, "campus_bg.png")
LOGO_FILENAME = os.path.join(current_dir, "logo.png")

st.set_page_config(page_title="LNMIIT Assistant", page_icon="🎓", layout="wide")

st.markdown("""
    <style>
        /* Fixed container pinned to the TOP RIGHT.
           This resolves the scrolling issue by keeping it in view at the top.
        */
        iframe[title="streamlit.components.v1.components.html_component"] {
            position: fixed;
            top: 20px;       /* Changed from bottom to top */
            right: 20px;
            width: 420px;
            height: 720px;
            z-index: 99999;
            border: none;
        }
    </style>
""", unsafe_allow_html=True)


if "messages" not in st.session_state:
    st.session_state.messages = []

def get_img_as_base64(file_path):
    """Reads an image file and returns a base64 string for HTML."""
    if not os.path.exists(file_path):
        return None
    with open(file_path, "rb") as f:
        data = f.read()
        encoded = base64.b64encode(data).decode()
    
    ext = os.path.splitext(file_path)[1].lower()
    mime = "image/png" if ext == ".png" else "image/jpeg"
    return f"data:{mime};base64,{encoded}"


def create_chat_widget(bg_base64=None, logo_base64=None):
    messages_json = json.dumps(st.session_state.messages)
    
    # Background Logic
    if bg_base64:
        card_bg_style = f"""
            background-image: linear-gradient(rgba(255, 255, 255, 0.1), rgba(255, 255, 255, 0.2)), url('{bg_base64}');
            background-size: cover;
            background-position: center;
        """
    else:
        card_bg_style = "background: #f8f9fa;"

    # Logo Logic
    if logo_base64:
        logo_html = f'<img src="{logo_base64}" class="header-logo" alt="Logo">'
    else:
        logo_html = '<span style="font-size: 24px;">🎓</span>'

    html_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;800&display=swap" rel="stylesheet">
        <style>
            /* --- COLORS & VARIABLES --- */
            :root {{
                --primary-blue: #0047AB;
                --accent-yellow: #FFC107;
                --text-dark: #1E293B;
            }}

            /* --- BASE SETTINGS --- */
            * {{ box-sizing: border-box; margin: 0; padding: 0; }}
            
            body {{
                font-family: 'Inter', sans-serif;
                background: transparent;
                height: 100vh;
                width: 100%;
                display: flex;
                flex-direction: column;
                justify-content: flex-start; /* CHANGED: Align to top */
                align-items: flex-end;     /* Align to right */
                padding: 10px;
                overflow: hidden;
            }}

            /* --- TRIGGER PILL --- */
            .trigger-pill {{
                background: var(--primary-blue);
                color: white;
                padding: 12px 24px;
                border-radius: 30px;
                cursor: pointer;
                box-shadow: 0 8px 20px rgba(0, 71, 171, 0.3);
                display: flex;
                align-items: center;
                gap: 12px;
                font-weight: 600;
                font-size: 16px;
                transition: all 0.3s ease;
                z-index: 20;
                pointer-events: auto;
                border: 2px solid transparent;
                /* Positioned relative to the flex container (top-right) */
                margin-top: 10px; 
                margin-right: 10px;
            }}

            .trigger-pill:hover {{
                transform: scale(1.05) translateY(2px); /* Animate down slightly */
                background: #003380;
                box-shadow: 0 12px 25px rgba(0, 71, 171, 0.4);
                border-color: var(--accent-yellow);
            }}

            .trigger-pill.hidden {{
                display: none;
            }}

            /* --- CHAT CARD --- */
            .chat-card {{
                width: 380px;
                height: 600px;
                border-radius: 24px;
                box-shadow: 0 20px 50px rgba(0,0,0,0.25);
                display: flex;
                flex-direction: column;
                overflow: hidden;
                transform-origin: top right; /* CHANGED: Animate from top-right */
                transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1);
                z-index: 10;
                opacity: 0;
                transform: scale(0.9) translateY(-20px); /* CHANGED: Start slightly above */
                pointer-events: none;
                {card_bg_style}
                border: 1px solid rgba(255,255,255,0.8);
                position: absolute;
                top: 70px; /* Spacing from top to account for where pill would be */
                right: 10px;
            }}

            .chat-card.open {{
                opacity: 1;
                transform: scale(1) translateY(0);
                pointer-events: auto;
            }}

            /* --- HEADER --- */
            .card-header {{
                padding: 16px 20px;
                background: var(--primary-blue);
                color: white;
                display: flex;
                justify-content: space-between;
                align-items: center;
                box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            }}

            .header-left {{ display: flex; align-items: center; gap: 12px; }}

            .header-logo {{
                height: 32px;
                width: auto;
                object-fit: contain;
                background: white;
                padding: 2px 6px;
                border-radius: 6px;
            }}

            .header-title {{ font-weight: 700; font-size: 16px; letter-spacing: 0.3px; }}

            .minimize-btn {{
                background: rgba(255,255,255,0.15);
                border: none;
                color: white;
                cursor: pointer;
                padding: 6px;
                border-radius: 50%;
                transition: 0.2s;
                width: 32px; height: 32px;
                display: flex; align-items: center; justify-content: center;
            }}
            .minimize-btn:hover {{ background: rgba(255,255,255,0.3); color: var(--accent-yellow); }}

            /* --- MESSAGES --- */
            .messages-area {{
                flex: 1;
                overflow-y: auto;
                padding: 20px;
                display: flex;
                flex-direction: column;
                gap: 16px;
            }}
            .messages-area::-webkit-scrollbar {{ width: 5px; }}
            .messages-area::-webkit-scrollbar-thumb {{ background: rgba(0,0,0,0.1); border-radius: 10px; }}

            .msg {{
                max-width: 85%;
                padding: 12px 16px;
                border-radius: 18px;
                font-size: 14px;
                line-height: 1.5;
                animation: slideIn 0.3s ease-out;
            }}
            
            @keyframes slideIn {{ from {{ opacity: 0; transform: translateY(10px); }} to {{ opacity: 1; transform: translateY(0); }} }}

            .msg.user {{
                align-self: flex-end;
                background: var(--primary-blue);
                color: white;
                border-bottom-right-radius: 4px;
                box-shadow: 0 4px 12px rgba(0, 71, 171, 0.2);
            }}

            .msg.bot {{
                align-self: flex-start;
                background: white;
                color: var(--text-dark);
                border-bottom-left-radius: 4px;
                box-shadow: 0 4px 12px rgba(0,0,0,0.05);
                border-left: 4px solid var(--accent-yellow);
            }}

            /* --- INPUT AREA --- */
            .input-area {{
                padding: 16px;
                background: white;
                border-top: 1px solid rgba(0,0,0,0.05);
                display: flex;
                gap: 10px;
                align-items: center;
            }}

            input {{
                flex: 1; padding: 12px 16px; border-radius: 24px; border: 2px solid #e2e8f0;
                outline: none; font-size: 14px; transition: 0.2s; background: #f8fafc;
            }}
            input:focus {{ border-color: var(--primary-blue); background: white; }}

            button.send-btn {{
                width: 42px; height: 42px; border-radius: 50%; border: none;
                background: var(--primary-blue); color: white; cursor: pointer;
                display: flex; align-items: center; justify-content: center;
                transition: 0.2s; box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            }}
            button.send-btn:hover {{ transform: scale(1.1); background: #003380; }}
            
            .typing {{ font-size: 12px; color: #94a3b8; margin-left: 10px; display: none; font-style: italic; }}
            .typing.active {{ display: block; margin-bottom: 10px; animation: pulse 1.5s infinite; }}
            @keyframes pulse {{ 0%, 100% {{ opacity: 0.5; }} 50% {{ opacity: 1; }} }}
        </style>
    </head>
    <body>

        <div class="trigger-pill" id="triggerBtn" onclick="toggleChat()">
            <span class="trigger-icon" style="color: var(--accent-yellow);">✨</span>
            <span>Ask LNMIIT</span>
        </div>

        <div class="chat-card" id="chatCard">
            <div class="card-header">
                <div class="header-left">
                    {logo_html}
                    <div class="header-title">LNMIIT Assistant</div>
                </div>
                <button class="minimize-btn" onclick="toggleChat()">
                    <!-- Close Icon -->
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>
                </button>
            </div>

            <div class="messages-area" id="msgContainer"></div>
            <div class="typing" id="typingIndicator">Thinking...</div>

            <div class="input-area">
                <input type="text" id="userInput" placeholder="Type your query..." onkeypress="handleEnter(event)">
                <button class="send-btn" onclick="sendMessage()">
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="22" y1="2" x2="11" y2="13"></line><polygon points="22 2 15 22 11 13 2 9 22 2"></polygon></svg>
                </button>
            </div>
        </div>

        <script>
            const API_URL = "{BACKEND_URL}";
            let messages = {messages_json};
            let isOpen = false;

            function toggleChat() {{
                isOpen = !isOpen;
                const card = document.getElementById('chatCard');
                const btn = document.getElementById('triggerBtn');
                
                if (isOpen) {{
                    card.classList.add('open');
                    btn.classList.add('hidden');
                    setTimeout(() => document.getElementById('userInput').focus(), 300);
                }} else {{
                    card.classList.remove('open');
                    btn.classList.remove('hidden');
                }}
            }}

            function render() {{
                const container = document.getElementById('msgContainer');
                container.innerHTML = '';
                
                if (messages.length === 0) {{
                    container.innerHTML = `
                        <div style="text-align:center; color: #64748b; margin-top: 60px; opacity: 0.8;">
                            <div style="font-size: 40px; margin-bottom: 10px;">👋</div>
                            <p style="font-weight: 500;">Welcome to LNMIIT!</p>
                            <p style="font-size: 13px;">How can I assist you today?</p>
                        </div>
                    `;
                }}

                messages.forEach(msg => {{
                    const div = document.createElement('div');
                    div.className = `msg ${{msg.role}}`;
                    div.textContent = msg.content;
                    container.appendChild(div);
                }});
                container.scrollTop = container.scrollHeight;
            }}

            async function sendMessage() {{
                const input = document.getElementById('userInput');
                const text = input.value.trim();
                if (!text) return;

                messages.push({{role: 'user', content: text}});
                input.value = '';
                render();
                document.getElementById('typingIndicator').classList.add('active');

                try {{
                    const res = await fetch(API_URL, {{
                        method: 'POST',
                        headers: {{'Content-Type': 'application/json'}},
                        body: JSON.stringify({{query: text}})
                    }});
                    
                    document.getElementById('typingIndicator').classList.remove('active');
                    if (res.ok) {{
                        const data = await res.json();
                        messages.push({{role: 'bot', content: data.response}});
                    }} else {{
                        messages.push({{role: 'bot', content: "⚠️ Backend connection failed."}});
                    }}
                }} catch (e) {{
                    document.getElementById('typingIndicator').classList.remove('active');
                    messages.push({{role: 'bot', content: " Server is offline."}});
                }}
                render();
                window.parent.postMessage({{ type: 'streamlit:setComponentValue', value: messages }}, '*');
            }}

            function handleEnter(e) {{ if (e.key === 'Enter') sendMessage(); }}

            render();
        </script>
    </body>
    </html>
    """
    return html_code




bg_data = get_img_as_base64(BG_FILENAME)
logo_data = get_img_as_base64(LOGO_FILENAME)


st.title(" LNMIIT Website")

st.markdown("""
    <div style="padding: 20px; border: 1px solid #ddd; border-radius: 10px; background: #f0f4f8; color: #333333;">
        <h3>Welcome to the LNMIIT Website.</h3>
        <p>This is your main dashboard. Ask anything regarding LNMIIT to the AI Assisted Chatbot located in the right corner.</p>
    </div>
""", unsafe_allow_html=True)

if bg_data is None:
    st.warning(f" Could not find background image: {BG_FILENAME}")
if logo_data is None:
    st.warning(f" Could not find logo image: {LOGO_FILENAME}")


widget_html = create_chat_widget(bg_data, logo_data)
components.html(widget_html, height=720, scrolling=False)