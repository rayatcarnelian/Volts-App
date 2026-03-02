import streamlit as st
import datetime
import time as _time

# --- ASSETS ---
# No Lottie animations - keeping it clean and professional

# --- TERMINAL / LOGGING ---
def init_terminal():
    if "terminal_logs" not in st.session_state:
        st.session_state.terminal_logs = []

def log_message(msg):
    timestamp = datetime.datetime.now().strftime("%H:%M:%S")
    entry = f"[{timestamp}] {msg}"
    try:
        print(entry)
    except:
        pass
            
    if "terminal_logs" not in st.session_state:
        st.session_state.terminal_logs = []
    st.session_state.terminal_logs.append(entry)
    if len(st.session_state.terminal_logs) > 50:
        st.session_state.terminal_logs.pop(0)

# --- UI COMPONENTS ---

def card_system_status(title, status, description, key):
    """
    Render a premium system status badge (Dark Mode).
    """
    
    # Define colors based on status
    if status == "Active" or status == "ON":
        # Glowing Green
        color = "#10B981" # Emerald-500
        bg_color = "rgba(16, 185, 129, 0.1)" 
        border_color = "rgba(16, 185, 129, 0.2)"
        box_shadow = "0 0 10px rgba(16, 185, 129, 0.1)"
    elif status == "Loading":
        color = "#F59E0B" # Amber-500
        bg_color = "rgba(245, 158, 11, 0.1)"
        border_color = "rgba(245, 158, 11, 0.2)"
        box_shadow = "none"
    else:
        color = "#6B7280" # Gray-500
        bg_color = "rgba(39, 39, 42, 0.5)" # Zinc-800 low opacity
        border_color = "rgba(63, 63, 70, 0.5)" # Zinc-700
        box_shadow = "none"

    st.markdown(f"""
    <div style="
        border: 1px solid {border_color};
        background-color: {bg_color};
        border-radius: 8px;
        padding: 12px 16px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 10px;
        box-shadow: {box_shadow};
        backdrop-filter: blur(8px);
        transition: all 0.2s ease;
    ">
        <div style="display: flex; flex-direction: column;">
            <span style="
                font-size: 0.7rem; 
                text-transform: uppercase; 
                letter-spacing: 0.05em; 
                color: #A1A1AA; /* Zinc-400 */
                font-weight: 600;
            ">{title}</span>
            <span style="
                font-size: 0.85rem; 
                color: #F4F4F5; /* Zinc-100 */
                font-weight: 500;
            ">{description}</span>
        </div>
        <div style="display: flex; align-items: center; gap: 8px;">
            <div style="
                width: 6px; 
                height: 6px; 
                border-radius: 50%; 
                background-color: {color}; 
                box-shadow: 0 0 6px {color};
            "></div>
            <span style="
                font-size: 0.75rem; 
                font-weight: 600; 
                color: {color};
            ">{status}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

def metric_card(title, content, description, key):
    """
    Render a premium metric card (Dark Mode).
    """
    st.markdown(f"""
    <div style="
        border: 1px solid #27272A; /* Zinc-800 */
        background: linear-gradient(145deg, #18181B, #09090B); /* Zinc-900 to Zinc-950 */
        border-radius: 12px;
        padding: 24px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.3);
        display: flex; 
        flex-direction: column;
        height: 100%;
        transition: transform 0.2s ease;
    ">
        <span style="
            font-size: 0.75rem; 
            text-transform: uppercase; 
            letter-spacing: 0.05em; 
            color: #71717A; /* Zinc-500 */
            font-weight: 600;
            margin-bottom: 8px;
        ">{title}</span>
        <span style="
            font-size: 2rem; 
            font-weight: 700; 
            color: #FAFAFA; /* Zinc-50 */
            letter-spacing: -0.025em;
            background: -webkit-linear-gradient(eee, #999);
            -webkit-background-clip: text;
        ">{content}</span>
        <span style="
            font-size: 0.85rem; 
            color: #52525B; /* Zinc-600 */
            margin-top: auto;
            padding-top: 12px;
            border-top: 1px solid #27272A;
        ">{description}</span>
    </div>
    """, unsafe_allow_html=True)


# --- STYLING ---
def apply_custom_css():
    st.markdown("""
    <style>
        /* FONTS */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

        /* RESET & BASE - DARK MODE */
        .stApp {
            background-color: #0A0A0A; /* Deep Black (Volts Website) */
            color: #EAEAEA; /* Off-White */
            font-family: 'Inter', system-ui, -apple-system, sans-serif !important;
        }

        /* SIDEBAR */
        [data-testid="stSidebar"] {
            background-color: #000000 !important; /* Pure Black */
            border-right: 1px solid #222222; /* Dark Border */
        }
        
        [data-testid="stSidebar"] .stRadio > label {
            padding: 10px 12px;
            border-radius: 6px;
            font-size: 0.9rem;
            color: #888888; /* Warm Grey */
            font-weight: 500;
            transition: all 0.15s ease;
            margin-bottom: 4px;
            display: block;
            cursor: pointer;
            border: 1px solid transparent;
        }

        [data-testid="stSidebar"] .stRadio > label:hover {
            background-color: #141414; /* Charcoal */
            color: #EAEAEA;
            border-color: #222222;
        }

        /* Active Sidebar Item */
        [data-testid="stSidebar"] .stRadio > div[role="radiogroup"] > label[data-checked="true"] {
            background-color: #1A1708 !important; /* Dark Gold tint */
            color: #C5A55A !important; /* Warm Gold */
            border: 1px solid #3D3520 !important; /* Muted Gold border */
            box-shadow: 0 0 10px rgba(197, 165, 90, 0.15);
        }

        /* HEADERS */
        h1 {
            font-size: 2.25rem !important;
            font-weight: 700 !important;
            color: #ffffff !important;
            letter-spacing: -0.03em !important;
            margin-bottom: 0.5rem !important;
            text-shadow: 0 0 20px rgba(255,255,255,0.1);
        }
        
        h2 {
            font-size: 1.5rem !important;
            font-weight: 600 !important;
            color: #f4f4f5 !important;
            letter-spacing: -0.02em !important;
        }
        
        h3 {
            font-size: 1.1rem !important;
            font-weight: 600 !important;
            color: #d4d4d8 !important; /* Zinc-300 */
            margin-top: 1.5rem !important;
        }

        /* CARDS & CONTAINERS */
        [data-testid="stExpander"], [data-testid="stForm"], [data-testid="stContainer"] {
            border: 1px solid #222222 !important; /* Dark Border */
            border-radius: 12px !important;
            background-color: #141414 !important; /* Charcoal */
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.3) !important;
        }
        
        /* EXPANDER HEADER */
        [data-testid="stExpander"] summary {
            color: #e4e4e7 !important; /* Zinc-200 */
            font-weight: 500;
        }
        
        /* INPUTS */
        .stTextInput input, .stTextArea textarea, .stSelectbox [data-baseweb="select"] {
            border: 1px solid #222222 !important;
            border-radius: 8px !important;
            background-color: #0A0A0A !important; /* Deep Black */
            color: #EAEAEA !important;
            font-size: 0.9rem !important;
            padding: 0.6rem !important;
        }
        
        .stTextInput input:focus, .stTextArea textarea:focus, .stSelectbox [data-baseweb="select"]:focus-within {
            border-color: #C5A55A !important; /* Warm Gold */
            box-shadow: 0 0 0 1px rgba(197, 165, 90, 0.5) !important;
        }

        /* BUTTONS */
        .stButton button {
            border-radius: 8px !important;
            font-weight: 500 !important;
            padding: 0.5rem 1.25rem !important;
            border: 1px solid transparent !important;
            transition: all 0.2s ease !important;
        }
        
        /* Secondary Button (Default) */
        .stButton button:not([kind="primary"]) {
            background-color: #141414 !important;
            border: 1px solid #222222 !important;
            color: #CCCCCC !important;
        }
        
        .stButton button:not([kind="primary"]):hover {
            background-color: #1E1E1E !important;
            border-color: #333333 !important;
            color: #ffffff !important;
        }

        /* Primary Button */
        .stButton button[kind="primary"] {
            background-color: #C5A55A !important; /* Warm Gold */
            color: #0A0A0A !important;
            box-shadow: 0 0 15px rgba(197, 165, 90, 0.4);
        }
        
        .stButton button[kind="primary"]:hover {
            background-color: #D4AF37 !important; /* Bright Gold */
            box-shadow: 0 0 20px rgba(212, 175, 55, 0.6) !important;
        }
        
        /* TABS */
        .stTabs [data-baseweb="tab-list"] {
            gap: 2rem;
            border-bottom: 1px solid #222222;
            padding-bottom: 0px;
        }
        
        .stTabs [data-baseweb="tab"] {
            padding: 0.75rem 0rem;
            font-weight: 500;
            color: #666666; /* Muted Grey */
            border-bottom: 2px solid transparent;
        }
        
        .stTabs [aria-selected="true"] {
            color: #C5A55A !important; /* Warm Gold */
            border-bottom-color: #C5A55A !important;
        }
        
        /* DATAFRAME / TABLES */
        [data-testid="stDataFrame"] {
            border: 1px solid #222222;
        }
        
        /* SCROLLBARS */
        ::-webkit-scrollbar {
            width: 8px;
            height: 8px;
        }
        ::-webkit-scrollbar-track {
            background: #0A0A0A; 
        }
        ::-webkit-scrollbar-thumb {
            background: #3f3f46; 
            border-radius: 4px;
        }
        ::-webkit-scrollbar-thumb:hover {
            background: #52525b; 
        }

        /* HIDE UGLY STREAMLIT BITS */
        [data-testid="stToolbar"] { display: none; }
        footer { display: none; }
        #MainMenu {visibility: hidden;}
        header {visibility: hidden;}
        
        /* REDUCE TOP PADDING */
        .block-container {
            padding-top: 1rem !important;
            padding-bottom: 1rem !important;
        }

        /* SMOOTH TRANSITIONS */
        .stTabs [data-baseweb="tab-panel"] {
            transition: opacity 0.2s ease-in-out;
        }

        /* GLASSMORPHISM ON CONTAINERS */
        [data-testid="stVerticalBlock"] > [data-testid="stContainer"] {
            backdrop-filter: blur(12px) !important;
            -webkit-backdrop-filter: blur(12px) !important;
        }

        /* MICRO-ANIMATION ON METRIC CARDS */
        [data-testid="stMetric"] {
            transition: transform 0.15s ease;
        }
        [data-testid="stMetric"]:hover {
            transform: translateY(-2px);
        }

        /* LOADING SKELETON ANIMATION */
        @keyframes shimmer {
            0% { background-position: -200% 0; }
            100% { background-position: 200% 0; }
        }
        .skeleton-loader {
            background: linear-gradient(90deg, #141414 25%, #222222 50%, #141414 75%);
            background-size: 200% 100%;
            animation: shimmer 1.5s infinite;
            border-radius: 8px;
        }

        /* PULSE ANIMATION FOR RADAR */
        @keyframes pulse-ring {
            0% { transform: scale(0.5); opacity: 1; }
            100% { transform: scale(1.5); opacity: 0; }
        }
        @keyframes pulse-dot {
            0%, 100% { transform: scale(1); }
            50% { transform: scale(1.1); }
        }
        
    </style>
    """, unsafe_allow_html=True)

# --- NAVIGATION ---
def tabs(options, key):
    """
    Render shadcn-style tabs.
    Wrapper around streamlit_shadcn_ui for consistency.
    """
    import streamlit_shadcn_ui as ui
    return ui.tabs(options=options, default_value=options[0], key=key)

def apply_aggressive_css():
    """
    Remove Streamlit branding and apply 'Dark Glass' theme.
    """
    st.markdown("""
        <style>
            /* HIDE STREAMLIT BRANDING */
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            
            /* REMOVE PADDING */
            .block-container {
                padding-top: 1rem !important;
                padding-bottom: 1rem !important;
                max_width: 95% !important;
            }
            
            /* DARK GLASS THEME */
            .stApp {
                background-color: #000000;
            }
            
            /* INPUT FIELDS */
            .stTextArea textarea {
                background-color: #111111 !important;
                border: 1px solid #333 !important;
                color: #fff !important;
                border-radius: 12px !important;
            }
            .stTextArea textarea:focus {
                border-color: #666 !important;
                box-shadow: 0 0 10px rgba(255, 255, 255, 0.1) !important;
            }
            
            /* BUTTONS */
            .stButton button {
                border-radius: 12px !important;
                font-weight: 600 !important;
                transition: transform 0.1s ease;
            }
            .stButton button:active {
                transform: scale(0.98);
            }
        </style>
    """, unsafe_allow_html=True)

def pricing_card(title, price, features, button_text, key):
    """
    Render a SaaS-style pricing card.
    """
    feature_html = "".join([f'<li style="margin-bottom: 8px; display: flex; align-items: center;"><span style="color: #4ade80; margin-right: 8px;">✓</span>{f}</li>' for f in features])
    
    st.markdown(f"""
    <div style="
        border: 1px solid #3f3f46;
        background: linear-gradient(180deg, #18181b 0%, #09090b 100%);
        border-radius: 16px;
        padding: 32px;
        text-align: center;
        max-width: 400px;
        margin: 0 auto;
        box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.5), 0 8px 10px -6px rgba(0, 0, 0, 0.5);
    ">
        <h3 style="color: #f4f4f5; font-size: 1.5rem; font-weight: 700; margin-bottom: 8px;">{title}</h3>
        <div style="margin-bottom: 24px;">
            <span style="color: #ffffff; font-size: 3rem; font-weight: 800;">{price}</span>
            <span style="color: #a1a1aa; font-size: 1.1rem;">/mo</span>
        </div>
        <ul style="
            list-style: none;
            padding: 0;
            margin: 0 0 32px 0;
            text-align: left;
            color: #d4d4d8;
            font-size: 0.95rem;
        ">
            {feature_html}
        </ul>
        <button style="
            width: 100%;
            background-color: #ffffff;
            color: #000000;
            font-weight: 600;
            padding: 12px;
            border-radius: 8px;
            border: none;
            cursor: pointer;
            transition: all 0.2s;
            font-size: 1rem;
        " onclick="alert('Redirecting to Stripe...')">
            {button_text}
        </button>
        <p style="color: #71717a; font-size: 0.8rem; margin-top: 16px;">Secure payment via Stripe</p>
    </div>
    """, unsafe_allow_html=True)


def animation_radar():
    """
    Render an animated radar/pulse indicator for the Admin dashboard.
    Pure CSS animation — no JS dependencies.
    """
    st.markdown("""
    <div style="
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 24px 0;
    ">
        <div style="position: relative; width: 80px; height: 80px;">
            <!-- Outer ring pulse -->
            <div style="
                position: absolute;
                top: 50%; left: 50%;
                width: 60px; height: 60px;
                margin: -30px 0 0 -30px;
                border: 2px solid rgba(197, 165, 90, 0.4);
                border-radius: 50%;
                animation: pulse-ring 2s ease-out infinite;
            "></div>
            <!-- Middle ring -->
            <div style="
                position: absolute;
                top: 50%; left: 50%;
                width: 40px; height: 40px;
                margin: -20px 0 0 -20px;
                border: 1px solid rgba(197, 165, 90, 0.25);
                border-radius: 50%;
                animation: pulse-ring 2s ease-out 0.5s infinite;
            "></div>
            <!-- Center dot -->
            <div style="
                position: absolute;
                top: 50%; left: 50%;
                width: 12px; height: 12px;
                margin: -6px 0 0 -6px;
                background: #C5A55A;
                border-radius: 50%;
                box-shadow: 0 0 12px rgba(197, 165, 90, 0.6);
                animation: pulse-dot 2s ease infinite;
            "></div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def skeleton_loader(height=40, count=3):
    """
    Render loading skeleton placeholders.
    """
    for _ in range(count):
        st.markdown(f"""
        <div class="skeleton-loader" style="
            height: {height}px;
            margin-bottom: 8px;
            width: 100%;
        "></div>
        """, unsafe_allow_html=True)
