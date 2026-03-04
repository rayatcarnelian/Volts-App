import streamlit as st
import time

def render_landing_page():
    """Renders the public facing landing page with Login/Signup embedded."""
    
    # Custom CSS for Landing Page
    st.markdown("""
        <style>
        .hero-header {
            font-size: 3rem;
            font-weight: 800;
            background: -webkit-linear-gradient(45deg, #C5A55A, #D4AF37);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 0px;
        }
        .hero-sub {
            font-size: 1.2rem;
            color: #888;
            margin-bottom: 30px;
        }
        .feature-card {
            background-color: #1E1E1E;
            padding: 20px;
            border-radius: 10px;
            border: 1px solid #333;
            text-align: center;
            height: 100%;
        }
        .feature-icon {
            font-size: 2rem;
            margin-bottom: 15px;
        }
        </style>
    """, unsafe_allow_html=True)

    # --- HERO SECTION ---
    c1, c2 = st.columns([1.5, 1])
    
    with c1:
        st.markdown('<h1 class="hero-header">VOLTS</h1>', unsafe_allow_html=True)
        st.markdown("# The Ultimate AI Growth Engine")
        st.markdown('<p class="hero-sub">Automate your entire sales pipeline. Scrape leads, send AI emails, and close deals with autonomous agents.</p>', unsafe_allow_html=True)
        
        st.markdown("### Why Volts?")
        fc1, fc2 = st.columns(2)
        with fc1:
            st.info("**Unlimited Lead Scraping**\n\nGoogle Maps, LinkedIn, Instagram, & more.")
            st.info("**AI Voice Agents**\n\nHuman-like cold calling & appointment setting.")
        with fc2:
            st.info("**Content Studio**\n\nGenerate viral videos & posts in seconds.")
            st.info("**CRM & Pipeline**\n\nTrack every deal automatically.")

    # --- LOGIN / SIGNUP SECTION (Right Side) ---
    with c2:
        st.markdown(" ")
        st.markdown(" ")
        with st.container(border=True):
            st.subheader("Get Started")
            
            # We return this container so main.py can render the form into it
            from modules.legal_docs import render_legal_modal
            render_legal_modal()
            return st.container()

def render_features_grid():
    st.markdown("---")
    st.markdown("<h2 style='text-align:center;'>Everything You Need to Scale</h2>", unsafe_allow_html=True)
    st.markdown(" ")
    
    c1, c2, c3 = st.columns(3)
    
    with c1:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon"></div>
            <h3>Deep Scraping</h3>
            <p>Extract thousands of targeted leads from Maps, LinkedIn, and Social Media with clean metadata.</p>
        </div>
        """, unsafe_allow_html=True)
        
    with c2:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon"></div>
            <h3>AI Dialer</h3>
            <p>Deploy autonomous voice agents that call, qualify, and book meetings 24/7.</p>
        </div>
        """, unsafe_allow_html=True)
        
    with c3:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon"></div>
            <h3>Creative Studio</h3>
            <p>Create high-converting video ads and social posts using cutting-edge Generative AI.</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown(" ")
    st.markdown(" ")
