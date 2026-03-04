"""
SOVEREIGN MODE: AUTONOMOUS HUNTER-KILLER AGENT
The "Brain" that orchestrates existing specialized agents into a continuous loop.
"""

import time
import os
import random
import streamlit as st
import pandas as pd
from datetime import datetime
import importlib

# Import specialized organs
from modules.sales_agents import SalesAgentTeam, ContentGenerationAgent
# from modules.outreach_voice import CallCenter
from modules.free_voice import FreeVoice
from modules.scraper_insta_api import InstagramHunterAPI
from modules.crm import LeadManager
import modules.db_supabase as db

class SovereignAgent:
    """
    The High-Command Agent that manages the entire acquisition lifecycle autonomously.
    """
    
    def __init__(self):
        self.sales_brain = SalesAgentTeam()
        self.visual_cortex = ContentGenerationAgent()
        # self.voice_module = CallCenter()
        self.voice_module = FreeVoice()
        self.running = False
        
    def log(self, message, icon="🤖"):
        """Emits a log to the Sovereign UI console."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        st.session_state.sovereign_logs.append(f"{timestamp} {icon} {message}")
        # Keep log size manageable
        if len(st.session_state.sovereign_logs) > 50:
            st.session_state.sovereign_logs.pop(0)
            
    def activate(self, target_hashtag, max_leads=10, safe_mode=True):
        """
        Main Autonomous Loop.
        """
        self.running = True
        self.log(f"SOVEREIGN AGENT ONLINE. Target: {target_hashtag}", "⚡")
        
        # 1. ACQUISITION PHASE
        self.log("Phase 1: Acquisition Initiated...", "📡")
        
        # We reuse the existing Instagram API hunter
        hunter = InstagramHunterAPI()
        
        # We wrap the existing scrape in a try/except to prevent crash
        try:
            leads = hunter.scrape_hashtag(target_hashtag, max_posts=max_leads)
            
            if not leads:
                self.log("Sector Clear. No targets found.", "❌")
                return
                
            self.log(f"Targets Acquired: {len(leads)} entities.", "🎯")
            
            # Save to DB immediately
            count = LeadManager.add_lead(leads)
            self.log(f"Database Enriched: {count} new profiles.", "💾")
            
        except Exception as e:
            self.log(f"CRITICAL ERROR in Acquisition: {e}", "💀")
            return
            
        # 2. ANALYSIS & ATTACK PHASE
        self.log("Phase 2: Analysis & Engagement...", "🧠")
        
        # Reload leads from DB to get IDs
        conn = db.get_connection()
        # Fetch the leads we just added (or recent ones)
        # Explicit Psycopg2 cursor fetch to prevent Pandas parameterization syntax errors.
        c = conn.cursor(cursor_factory=db.RealDictCursor)
        query = f"SELECT * FROM leads WHERE source LIKE '%%Instagram%%' ORDER BY id DESC LIMIT {max_leads}"
        c.execute(query)
        data = c.fetchall()
        recent_leads = pd.DataFrame(data)
        conn.close()
        
        for idx, lead in recent_leads.iterrows():
            if not self.running:
                self.log("Override Command Received. Shutting Down.", "🛑")
                break
                
            lead_name = lead['name']
            lead_id = lead['id']
            
            self.log(f"Analyzing Target: {lead_name}...", "👀")
            
            # A. VISUAL SENSING (Simulated for now, can be upgraded to snapshot analysis)
            # In a real scenario, we would browse their link_bio here.
            # For now, we use the 'bio' text to infer context.
            visual_context = lead.get('bio_text', '')  or "A luxury design profile."
            
            # B. STRATEGY GENERATION
            # Use the SalesTeam brain to decide what to do
            lead_dict = lead.to_dict()
            strategy = self.sales_brain.analyze_lead_intent(lead_dict)
            
            self.log(f"Strategy: {strategy.get('engagement_type').upper()} via {strategy.get('channel').upper()}", "💡")
            
            # C. EXECUTION
            if strategy.get('priority') == 'high' and not safe_mode:
                # KILLER MODE: Immediate Action
                self._execute_attack(lead_dict, strategy, visual_context)
            else:
                self.log(f"Lead queued for manual review (Safety Protocols Active).", "🛡️")
                
            # Random sleep to look human
            time.sleep(random.uniform(2, 5))
            
        self.log("Mission Complete. Standing by.", "✅")
        self.running = False

    def _execute_attack(self, lead, strategy, visual_context):
        """
        Executes the chosen engagement strategy.
        """
        channel = strategy.get('channel')
        
        if channel == 'phone':
            # VOICE ATTACK
            self.log("Synthesizing Neural Voice (FREE)...", "🗣️")
            
            # 1. Generate Hyper-Personalized Hook
            hook = f"Hi {lead['name']}, I'm calling because I saw your Instagram bio about {visual_context[:20]}... and I have a project for you."
            
            # 2. Generate Audio File
            try:
                # Use the lead ID as filename
                file_path = self.voice_module.generate(text=hook, text_id=lead['id'])
                if file_path:
                    self.log(f"Audio Drone Created: {os.path.basename(file_path)}", "💾")
                    self.log("Ready for WhatsApp Deployment.", "🚀")
                else:
                    self.log("Voice Synthesis Failed.", "⚠️")
            except Exception as e:
                self.log(f"Voice generation error: {e}", "⚠️")
            
            # 3. (Optional) Simulate Call Status for UI
            # self.log(f"Call Status: Queued for WhatsApp", "📶")
                
        elif channel == 'email':
            # VISION ATTACK (Send Video)
            self.log("Generating Visual Payload...", "🎨")
            
            # 1. Generate Image
            prompt = self.visual_cortex.generate_design_prompt(lead)
            img_path, _ = self.visual_cortex.generate_image(prompt, lead['id'])
            
            if img_path:
                self.log("Visual Asset Created.", "🖼️")
                # In real deployment, this would email the user.
                self.log(f"Email drafted with asset: {os.path.basename(img_path)}", "📧")
            else:
                self.log("Visual Generation Failed.", "⚠️")

    def ingest_leads(self, file_path):
        """
        Ingests a CSV/Excel file, normalizes columns, and saves to DB.
        """
        try:
            self.log("Ingesting Lead List...", "📥")
            
            # 1. Read File
            if hasattr(file_path, "name"):
                fname = file_path.name
            else:
                fname = str(file_path)
                
            if fname.endswith(".csv"):
                df = pd.read_csv(file_path)
            else:
                df = pd.read_excel(file_path)
                
            # 2. Add 'pitch_draft' column if missing in DB
            # We do this ad-hoc here to avoid full migration script for now
            try:
                conn = db.get_connection()
                conn.execute("ALTER TABLE leads ADD COLUMN pitch_draft TEXT")
                conn.execute("ALTER TABLE leads ADD COLUMN website TEXT")
                conn.close()
            except:
                pass # Columns likely exist
            
            # 3. Process & Save
            count = 0
            
            # Normalize column names to lowercase for easier matching
            df.columns = [c.strip().lower() for c in df.columns]
            
            self.log(f"Columns found: {list(df.columns)}", "🔎")
            
            # Setup Progress Bar
            progress_bar = st.progress(0, text="Initializing Research Engine...")
            total_rows = len(df)
            
            # Initialize Shared Driver
            driver = None
            try:
                from selenium import webdriver
                from selenium.webdriver.chrome.options import Options
                
                chrome_options = Options()
                chrome_options.add_argument("--headless")
                chrome_options.add_argument("--no-sandbox")
                chrome_options.add_argument("--disable-dev-shm-usage")
                chrome_options.page_load_strategy = 'eager'
                
                # Only spin up driver if we have leads to process
                if total_rows > 0:
                    driver = webdriver.Chrome(options=chrome_options)
                    driver.set_page_load_timeout(10)
            except Exception as driver_err:
                self.log(f"Driver Init Failed: {driver_err}", "⚠️")
            
            for index, row in df.iterrows():
                # Update Progress
                progress = (index + 1) / total_rows
                progress_bar.progress(progress, text=f"Analyzing Lead {index+1}/{total_rows}...")
                
                # Flexible Column Matching
                name = row.get('company') or row.get('name') or row.get('lead') or row.get('business')
                website = row.get('website') or row.get('url') or row.get('link') or row.get('site')
                email = row.get('email') or row.get('mail') or row.get('contact')
                
                if name:
                    # Save to DB
                    try:
                        conn = db.get_connection()
                        c = conn.cursor()
                        
                        # Check dupe AND check if it needs analysis
                        c.execute("SELECT id, notes FROM leads WHERE name = ?", (name,))
                        existing_row = c.fetchone()
                        
                        lid = None
                        should_research = False
                        
                        if not existing_row:
                            # NEW LEAD
                            c.execute("INSERT INTO leads (name, primary_email, notes) VALUES (?, ?, ?)", 
                                      (name, email, f"WEBSITE:{website}"))
                            lid = c.lastrowid
                            should_research = True
                            count += 1
                        else:
                            # EXISTING LEAD - RETRY CHECK
                            lid = existing_row['id']
                            notes = existing_row['notes'] or ""
                            
                            # If no pitch yet, or it was an error/analyzing placeholder that got stuck
                            if "PITCH:" not in notes:
                                self.log(f"Retrying Analysis for: {name}", "🔄")
                                should_research = True
                                count += 1
                            else:
                                self.log(f"Already Analyzed: {name}", "⏭️")
                        
                        conn.commit()
                        conn.close()

                        if should_research:
                             if website and str(website).startswith("http"):
                               # Pass shared driver
                               self._deep_research(lid, name, website, driver)
                             else:
                                self.log(f"Skipping Research for {name}: Invalid URL ({website})", "⏩")

                    except Exception as db_err:
                        self.log(f"DB Error on row {index}: {db_err}", "⚠️")
                else:
                    self.log(f"Skipping Row {index}: No 'Name/Company' column found.", "❓")
            
            # Cleanup Driver
            if driver:
                driver.quit()
                
            progress_bar.empty()
            
            if count == 0:
                 self.log("Zero leads imported/processed.", "⚠️")
            else:
                 self.log(f"Successfully Processed {count} Leads.", "✅")
            
            return count
        except Exception as e:
            self.log(f"Ingest Error: {e}", "⚠️")
            import traceback
            traceback.print_exc()
            return 0

    def _deep_research(self, lead_id, name, website, driver=None):
        """
        Visits the website using shared driver, extracts text, and generates a pitch.
        """
        self.log(f"Deep Research: {name} ({website})", "🕵️")
        
        # Update DB to show we are analyzing
        try:
            conn = db.get_connection()
            conn.execute("UPDATE leads SET notes = ? WHERE id = ?", ("ANALYZING...", lead_id))
            conn.commit()
            conn.close()
        except: pass
        
        text_content = ""
        report_path = None
        audit_findings = "No audit performed."
        
        # 1. Scrape Website
        if driver:
            try:
                self.log(f"Visiting {website}...", "🌐")
                try:
                    driver.get(website)
                except:
                    self.log("Timeout (proceeding with partial load)...", "⚠️")
                
                # --- NEW: TITAN AUDIT PROTOCOL ---
                from modules.analyst import DigitalAnalyst
                analyst = DigitalAnalyst()
                
                self.log("Running Technical Audit (Titan Protocol)...", "🕵️")
                audit_data = analyst.audit_site(website, driver)
                report_path = analyst.generate_report(name, audit_data)
                
                if report_path:
                    self.log(f"Audit Generated: {os.path.basename(report_path)}", "📄")
                    # Prepare context for AI
                    audit_findings = f"Audit Score: {audit_data['score']}/100. Issues: {len(audit_data['checks'])} checks run."
                    for check in audit_data['checks']:
                        if check['status'] != 'PASS':
                            audit_findings += f"\n- {check['name']}: {check['details']}"
                else:
                    self.log("Audit Generation Failed.", "⚠️")
                # ---------------------------------
                
                # Capture Text
                text_content = driver.find_element("tag name", "body").text[:2000] # First 2k chars
                
                self.log("Website Analysis Complete.", "✅")
                
            except Exception as e:
                self.log(f"Website Visit Failed: {e}", "❌")
                text_content = "Website unreachable."
        else:
             text_content = "Driver unavailable."
            
        # 2. Generate Pitch (Even if scrape failed, we try with name)
        self._generate_strategic_pitch(lead_id, name, text_content, website, audit_findings, report_path)

    def _generate_strategic_pitch(self, lead_id, business_name, website_text, website_url, audit_details="", report_path=None):
        """
        Uses Gemini to write a high-IQ sales pitch.
        """
        self.log(f"Drafting Pitch for {business_name}...", "✍️")
        
        try:
            from modules.ai_engine import AIGhostwriter
            ai = AIGhostwriter() 
            
            website_context = f"Website URL: {website_url}\nPage Content: {website_text}\n\nTECHNICAL AUDIT FINDINGS:\n{audit_details}"
            
            prompt = f"""
            Act as a World-Class Sales Strategist (Titan Protocol).
            PRODUCT: A high-end Tech Consultancy / AI Agency.
            LEAD: {business_name}
            CONTEXT: {website_context}
            
            TASK: Write a 1-Paragraph "High-Value Audit Email" to the owner.
            RULES:
            1. SUBJECT LINE: "Audit Report for {business_name}"
            2. OPENER: "I just ran a technical audit on your site and found {audit_details.count('FAIL')} critical errors."
            3. BODY: Mention specific failures from the Audit Findings (e.g. SSL, Mobile, SEO).
            4. OFFER: "I've attached the full confidential PDF report. Let me know if you want me to fix these for you."
            5. Tone: Urgent, Authoritative, Helpful.
            
            OUTPUT: The exact message text only.
            """
            
            pitch = ai.generate_content(prompt)
            
            # Save to DB
            if pitch:
                conn = db.get_connection()
                # We prepend PITCH: so UI knows it's ready
                store_val = f"PITCH:{pitch}"
                conn.execute("UPDATE leads SET notes = ? WHERE id = ?", (store_val, lead_id))
                conn.commit()
                conn.close()
                self.log("Pitch Drafted & Saved.", "💾")
            else:
                self.log("AI returned empty pitch.", "⚠️")
                
        except Exception as e:
            self.log(f"AI Pitch Generation Failed: {e}", "⚠️")
            # Save error to notes so it shows up
            try:
                conn = db.get_connection()
                conn.execute("UPDATE leads SET notes = ? WHERE id = ?", (f"ERROR: {str(e)}", lead_id))
                conn.commit()
                conn.close()
            except: pass

# Session State Initializer for main.py
def init_sovereign_state():
    if 'sovereign_logs' not in st.session_state:
        st.session_state.sovereign_logs = []
    if 'sovereign_active' not in st.session_state:
        st.session_state.sovereign_active = False
