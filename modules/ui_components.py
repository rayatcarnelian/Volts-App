import streamlit as st
import requests
from streamlit_lottie import st_lottie
import datetime

# --- ASSETS ---
def load_lottie_url(url: str):
    try:
        r = requests.get(url)
        if r.status_code != 200:
            return None
        return r.json()
    except:
        return None

def animation_radar():
    """Display Radar Scan animation"""
    # Sci-fi scanner/radar
    data = load_lottie_url("https://lottie.host/8802996d-7416-4303-b097-400d3d517c2a/2x9Q5u0y8i.json") 
    if data:
        st_lottie(data, height=120, key="radar")

def animation_brain():
    """Display Brain Pulse animation"""
    # Neural network / AI brain
    data = load_lottie_url("https://lottie.host/98606c11-9252-4752-9729-d0f1af40605a/3Yx4Q5u0y8.json")
    if data:
        st_lottie(data, height=120, key="brain")

# --- TERMINAL / LOGGING ---
def init_terminal():
    if "terminal_logs" not in st.session_state:
        st.session_state.terminal_logs = []

def log_message(msg):
    timestamp = datetime.datetime.now().strftime("%H:%M:%S")
    entry = f"[{timestamp}] {msg}"
    try:
        print(entry)
    except Exception:
        # Fallback for Windows consoles that choke on emojis
        try:
            print(entry.encode('utf-8').decode('utf-8', 'ignore'))
        except:
             # Last resort: strip non-ascii
            print(entry.encode('ascii', 'ignore').decode('ascii'))
            
    if "terminal_logs" not in st.session_state:
        st.session_state.terminal_logs = []
    st.session_state.terminal_logs.append(entry)
    if len(st.session_state.terminal_logs) > 50:
        st.session_state.terminal_logs.pop(0)

def render_terminal():
    """Renders the fixed bottom terminal."""
    st.markdown("""
        <style>
        .terminal-box {
            background-color: #09090b;
            border: 1px solid #3f3f46;
            color: #22c55e;
            font-family: 'JetBrains Mono', 'Courier New', monospace;
            padding: 12px;
            height: 150px;
            overflow-y: auto;
            font-size: 0.85rem;
            margin-top: 20px;
            border-radius: 4px; /* Slight rounded for 'high-tech' feel but keep it boxy */
        }
        .terminal-header {
            border-bottom: 1px solid #3f3f46;
            margin-bottom: 8px;
            padding-bottom: 4px;
            font-weight: bold;
            color: #71717a;
            font-size: 0.75rem;
            text-transform: uppercase;
        }
        </style>
    """, unsafe_allow_html=True)
    
    logs = st.session_state.get("terminal_logs", [])
    log_text = "<br>".join(logs)
    
    st.markdown(f"""
    <div class="terminal-box">
        <div class="terminal-header">/// SYSTEM_LOGS / LIVE_FEED</div>
        {log_text}
    </div>
    """, unsafe_allow_html=True)

# --- STYLING ---
def apply_custom_css():
    st.markdown("""
    <style>
        /* FONTS */
        @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;600;700&family=JetBrains+Mono:wght@400;600&display=swap');

        /* RESET & BASE */
        .stApp {
            background-color: #000000; /* True Black for depth */
            color: #e4e4e7; /* Zinc-200 */
        }
        
        /* HEADERS */
        h1, h2, h3 {
            font-family: 'Space Grotesk', sans-serif !important;
            text-transform: uppercase;
            font-weight: 700 !important;
            letter-spacing: -0.5px;
        }
        
        h1 { color: #ffffff !important; }
        h2 { color: #facc15 !important; /* Yellow-400 (Gold-ish but digital) */ }
        h3 { color: #a1a1aa !important; /* Zinc-400 */ }
        
        /* TEXT - Prevent overriding icons by avoiding global div/span */
        .stApp, p, label, button, input, .stMarkdown {
            font-family: 'Space Grotesk', sans-serif !important;
        }

        /* INPUTS (Text, Select, Areas) - Brutalist Boxy */
        .stTextInput>div>div>input, 
        .stTextArea>div>div>textarea, 
        .stSelectbox>div>div>div {
            background-color: #09090b !important; /* Zinc-950 */
            color: #ffffff !important;
            border: 1px solid #27272a !important; /* Zinc-800 */
            border-radius: 0px !important;
            font-family: 'JetBrains Mono', monospace !important;
        }
        
        /* Focus State */
        .stTextInput>div>div>input:focus, 
        .stTextArea>div>div>textarea:focus {
            border-color: #facc15 !important;
            box-shadow: none !important;
        }

        /* BUTTONS - Solid, Sharp, High Contrast */
        .stButton>button {
            background-color: #18181b !important; /* Zinc-900 */
            color: #facc15 !important;
            border: 1px solid #facc15 !important;
            border-radius: 0px !important;
            padding: 0.6rem 1.2rem;
            text-transform: uppercase;
            font-weight: 600;
            letter-spacing: 1px;
            transition: all 0.2s ease;
        }
        
        .stButton>button:hover {
            background-color: #facc15 !important;
            color: #000000 !important;
            border-color: #facc15 !important;
            font-weight: 700;
        }

        /* CARD CONTAINERS */
        [data-testid="stExpander"] {
            border: 1px solid #27272a !important;
            border-radius: 0px !important;
            background-color: #09090b !important;
        }

        /* SIDEBAR */
        [data-testid="stSidebar"] {
            background-color: #050505;
            border-right: 1px solid #27272a;
        }
        
        /* METRICS */
        [data-testid="stMetricValue"] {
            font-family: 'JetBrains Mono', monospace !important;
            color: #facc15 !important; 
        }

        /* Generic Streamlit elements removal - DISABLED DEBUG */
        /* #MainMenu {visibility: hidden;} */
        /* footer {visibility: hidden;} */
        /* header {visibility: hidden;} */
        
    </style>
    """, unsafe_allow_html=True)
