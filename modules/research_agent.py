import requests
from bs4 import BeautifulSoup
import sqlite3
import json
from modules.ai_engine import AIGhostwriter
import modules.database as db
import urllib3
import time

# Suppress SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class ResearchAgent:
    def __init__(self):
        self.ai = AIGhostwriter()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

    def fetch_content(self, url):
        """Fetches text content from a URL safely."""
        try:
            if not url.startswith('http'):
                url = 'https://' + url
                
            response = requests.get(url, headers=self.headers, timeout=10, verify=False)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Remove scripts and styles
            for script in soup(["script", "style", "nav", "footer"]):
                script.decompose()
                
            text = soup.get_text()
            
            # Clean text
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            clean_text = '\n'.join(chunk for chunk in chunks if chunk)
            
            # Truncate to avoid token limits (approx 10k chars)
            return clean_text[:10000]
            
        except Exception as e:
            print(f"Fetch Error ({url}): {e}")
            return None

    def analyze_company(self, company_name, url=None, bio=None):
        """
        Main Analysis Pipeline.
        1. Scrape Website (if URL exists)
        2. Combine with Bio
        3. AI Analysis
        """
        
        context_text = f"Company: {company_name}\n"
        
        if bio:
            context_text += f"Bio/Profile: {bio}\n"
            
        if url:
            print(f"Surfing {url}...")
            web_content = self.fetch_content(url)
            if web_content:
                context_text += f"\nWEBSITE CONTENT:\n{web_content}"
            else:
                context_text += "\n(Website Unreachable)"
        
        # PROMPT FOR CLAY-LIKE INTELLIGENCE
        prompt = f"""
        ANALYZE THIS LEAD DATA:
        {context_text}
        
        TASK:
        Act as a Senior Sales Researcher. Extract 3 things in JSON format:
        1. "summary": A 1-sentence summary of what they actually do.
        2. "pain_points": 2-3 inferred problems they likely have (that a Design/Agency service could solve).
        3. "ice_breaker": A hyper-personalized customized first line for a cold email. Mention a specific project, achievement, or detail from the text. Do NOT be generic.
        
        OUTPUT JSON ONLY:
        {{
            "summary": "...",
            "pain_points": "...",
            "ice_breaker": "..."
        }}
        """
        
        try:
            response = self.ai.generate_content(prompt)
            # Clean JSON (Gemini sometimes wraps in markdown)
            response = response.replace("```json", "").replace("```", "").strip()
            data = json.loads(response)
            return data
        except Exception as e:
            print(f"AI Analysis Failed: {e}")
            return None

    def research_lead(self, lead_id):
        """Researches a specific lead from the DB and updates it."""
        conn = db.get_connection()
        conn.row_factory = sqlite3.Row
        
        # valid columns are checked in database.py
        lead = conn.execute("SELECT * FROM leads WHERE id = ?", (lead_id,)).fetchone()
        
        if not lead:
            conn.close()
            return False
            
        # Get URL from lead or profiles
        url = None
        # Try to find a website URL. 
        # Often profile_url is social media (LinkedIn/Insta). 
        # We need the COMPANY website ideally.
        # But for now, we'll try to use whatever link we have, or Google Search (Future).
        # Let's assume input might be in 'notes' or we check linkedin_profiles table for website if we scraped it.
        # For this v1, we will use the profile_url if it looks like a website, or search for it.
        
        # Simple Logic: If profile_url is NOT linkedin/instagram/facebook, use it.
        raw_url = lead['source'] # Sometimes source is domain? No.
        
        # Look in profiles
        # We need to JOIN queries or just simple heuristic
        # Let's use the 'profile_url' column if it exists in the unified view
        # or grab from the linked tables.
        
        # Actually, let's look at the lead record.
        # We did not add a `website_url` column. We usually use `profile_url`.
        # If `profile_url` is a social link, we might want to visit that too (LinkedIn Public Profile).
        
        target_url = None
        
        # Check LinkedIn/Insta tables for external links? 
        # For simplicity V1: We will analyze the available text (Bio) + Source.
        # If we want to scrape, we need a URL.
        
        # FUTURE: Use Google Search to find website.
        # For now, we will perform "Deep Analysis" on the TEXT we already have (Bio/Notes) 
        # PLUS try to visit the profile_url if it's actionable.
        
        # Let's fetch the Aggregated Data like in main.py
        q = """
             SELECT 
                l.name, 
                COALESCE(li.headline, i.bio_text, pa.specialty_area) as bio,
                COALESCE(li.profile_url, i.profile_url, pa.profile_url) as url
             FROM leads l
             LEFT JOIN linkedin_profiles li ON l.id = li.lead_id
             LEFT JOIN instagram_profiles i ON l.id = i.lead_id
             LEFT JOIN property_agents pa ON l.id = pa.lead_id
             WHERE l.id = ?
        """
        data = conn.execute(q, (lead_id,)).fetchone()
        
        if data:
            name = data['name']
            bio = data['bio']
            url = data['url']
            
            print(f"Researching {name}...")
            
            # RUN ANALYSIS
            result = self.analyze_company(name, url, bio)
            
            if result:
                # SAFE BINDING: Ensure all params are strings
                s_sum = result.get('summary', '')
                s_ice = result.get('ice_breaker', '')
                
                # Handle pain_points if list
                p_points = result.get('pain_points', '')
                if isinstance(p_points, list):
                    p_points = ", ".join(p_points)
                elif isinstance(p_points, dict):
                    p_points = json.dumps(p_points)
                
                # Update DB
                conn.execute("""
                    UPDATE leads 
                    SET website_summary = ?, 
                        ice_breaker = ?, 
                        pain_points = ?,
                        research_status = 'Done',
                        total_score = total_score + 10 -- Bonus for Enrichment
                    WHERE id = ?
                """, (s_sum, s_ice, p_points, lead_id))
                conn.commit()
                conn.close()
                return True
                
        conn.close()
        return False

if __name__ == "__main__":
    # Test
    agent = ResearchAgent()
    # Mock Research
    # print(agent.analyze_company("Volts Design", "https://volts.design"))
