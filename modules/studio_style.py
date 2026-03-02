"""
STUDIO STYLE MODULE
Contains all the CSS and HTML assets to make Streamlit look like a Next.js App.
"""

import streamlit as st

def inject_high_end_css():
    st.markdown("""
        <style>
            /* --- FONTS --- */
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;800&family=JetBrains+Mono:wght@400;500&display=swap');
            
            /* --- RESET & GLOBAL --- */
            .stApp {
                background-color: #0A0A0A;
                font-family: 'Inter', sans-serif;
            }
            
            h1, h2, h3, h4, h5, h6 {
                font-family: 'Inter', sans-serif;
                letter-spacing: -0.02em;
            }
            
            /* Footer (Optional to hide) */
            footer {visibility: hidden;}
            
            /* Remove Padding for Full Screen Feel */
            .block-container {
                padding-top: 2rem !important;
                padding-bottom: 5rem !important;
                max-width: 1200px !important;
            }
            
            /* --- COMPONENTS --- */
            
            /* TextArea (The Prompt Box) */
            .stTextArea textarea {
                background-color: #111 !important;
                border: 1px solid #333 !important;
                color: #eee !important;
                font-family: 'Inter', sans-serif !important;
                font-size: 1.1rem !important;
                border-radius: 12px !important;
                padding: 1rem !important;
                transition: all 0.2s ease;
            }
            .stTextArea textarea:focus {
                border-color: #C5A55A !important; /* Warm Gold */
                box-shadow: 0 0 0 1px #C5A55A !important;
            }
            
            /* Buttons (Primary) */
            .stButton button[kind="primary"] {
                background: linear-gradient(135deg, #C5A55A 0%, #B8953F 100%) !important;
                border: none !important;
                color: #0A0A0A !important;
                font-weight: 600 !important;
                padding: 0.75rem 1.5rem !important;
                border-radius: 8px !important;
                letter-spacing: 0.02em;
                transition: all 0.2s;
                box-shadow: 0 4px 12px rgba(197, 165, 90, 0.3);
            }
            .stButton button[kind="primary"]:hover {
                transform: translateY(-1px);
                box-shadow: 0 6px 16px rgba(197, 165, 90, 0.4);
            }
            
            /* Buttons (Secondary) */
            .stButton button[kind="secondary"] {
                background-color: #141414 !important;
                border: 1px solid #222222 !important;
                color: #ccc !important;
            }
            
            /* Alerts / Info */
            .stAlert {
                background-color: #141414 !important;
                border: 1px solid #222222 !important;
                color: #ddd !important;
            }
            
            /* Sidebar */
            [data-testid="stSidebar"] {
                background-color: #000 !important;
                border-right: 1px solid #222 !important;
            }
            
        </style>
    """, unsafe_allow_html=True)

def render_landing_hero():
    st.markdown("""
        <div style="text-align: center; margin-bottom: 4rem; margin-top: 4rem;">
            <div style="
                display: inine-block;
                background: linear-gradient(90deg, #C5A55A, #D4AF37, #E8D5A3);
                -webkit-background-clip: text;
                color: transparent;
                font-weight: 800;
                font-size: 1rem;
                letter-spacing: 0.1em;
                margin-bottom: 1rem;
            ">VOLTS STUDIO AI</div>
            <h1 style="
                font-size: 4rem; 
                font-weight: 800; 
                color: white; 
                line-height: 1.1; 
                margin-bottom: 1.5rem;
            ">
                Dream it. <br>
                <span style="color: #666;">Generate it.</span>
            </h1>
            <p style="
                font-size: 1.25rem; 
                color: #888; 
                max-width: 600px; 
                margin: 0 auto 2rem auto;
            ">
                The professional creative suite powered by Flux 1.1 Pro and Luma Dream Machine.
            </p>
        </div>
    """, unsafe_allow_html=True)
