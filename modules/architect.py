import os
import glob
import google.generativeai as genai
import streamlit as st

class VoltsArchitect:
    def __init__(self):
        try:
            api_key = os.getenv("GEMINI_API_KEY")
            if not api_key:
                st.error("Architect Error: GEMINI_API_KEY not found.")
                return
            
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-2.0-flash') # Fast and smart
            self.context = self._load_codebase_context()
            
        except Exception as e:
            st.error(f"Architect Initialization Error: {e}")

    def _load_codebase_context(self):
        """Reads the app's own source code to understand itself."""
        context = "Here is the current codebase structure and content of the VOLTS application:\n\n"
        
        # Read Main File
        try:
            with open("main.py", "r", encoding="utf-8") as f:
                context += f"--- FILE: main.py ---\n{f.read()}\n\n"
        except: pass
        
        # Read Modules
        module_files = glob.glob("modules/*.py")
        for file_path in module_files:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    context += f"--- FILE: {file_path} ---\n{f.read()}\n\n"
            except: pass
            
        return context

    def ask(self, user_query, chat_history=[]):
        """
        Answers a user question using the codebase context.
        chat_history is a list of {"role": "user/model", "content": "text"}
        """
        if not hasattr(self, 'model'):
            return "I am offline. Check API Key."

        system_prompt = f"""
        You are THE ARCHITECT, the internal AI super-agent for the VOLTS Client Acquisition System.
        
        Your Capabilities:
        1. You have full access to the source code of this application (provided below).
        2. You are an expert in Python, Streamlit, Selenium, and Digital Marketing (Lead Gen).
        
        Your Mission:
        1. Answer technical questions about the app ("How does the scraper work?", "Fix this error").
        2. Answer strategic questions ("How do I target high-value clients?").
        3. If asked to modify code, provide the EXACT code block the user should copy-paste.
        
        Tone: Professional, highly intelligent, concise, and helpful. You are the 'Jarvis' to the user's 'Iron Man'.
        
        --- CURRENT CODEBASE CONTEXT ---
        {self.context}
        -------------------------------
        """
        
        # Construct Chat
        # For simple QA, we just send the full prompt.
        full_prompt = f"{system_prompt}\n\nCHAT HISTORY:\n{chat_history}\n\nUSER QUESTION: {user_query}"
        
        import time
        
        # 3-Layer Safety Net for 24/7 Uptime
        # 1. Try the "Smartest" (Pro)
        # 2. If busy, try the "Fastest" (Flash 2.0)
        # 3. If busy, try the "Reliable" (Flash 1.5)
        # 3. If busy, try the "Reliable" (Flash 1.5)
        models_to_try = ['gemini-pro-latest', 'gemini-2.0-flash-exp', 'gemini-flash-latest']
        
        last_error = None
        
        for model_name in models_to_try:
            try:
                # Attempt generation
                model = genai.GenerativeModel(model_name)
                response = model.generate_content(full_prompt)
                
                # If we are here, it worked.
                # If we fell back, maybe add a note? 
                prefix = ""
                if model_name != 'gemini-1.5-pro':
                   prefix = f"*[System Note: High traffic on Pro model. Switched to {model_name} for speed.]*\n\n"
                   
                return prefix + response.text
                
            except Exception as e:
                last_error = e
                error_str = str(e)
                # If it's a Rate Limit (429), Overloaded (503), or Not Found (404), continue to next model
                if "429" in error_str or "503" in error_str or "404" in error_str:
                    # Log it implicitly by continuing
                    last_error = f"{model_name} failed: {e}"
                    # Even for paid, a short breather is good for 503s. 
                    # For Free Tier 429s, we should wait longer, but let's just do a safe 2s
                    time.sleep(2) 
                    continue
                else:
                    # If it's a real error (auth, etc), stop.
                    return f"Architect Error ({model_name}): {e}"
        
        # If we ran out of models
        return f"System Overloaded. All AI models are currently busy. Please verify your API Key plan or try again in 1 minute. (Last Error: {last_error})"
