import requests
from bs4 import BeautifulSoup
import json
from modules.ai_engine import AIGhostwriter
import modules.db_supabase as db
from psycopg2.extras import RealDictCursor
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
            if response.startswith("Error:") or response.startswith("AI Error:"):
                print(f"AI Provider Error: {response}")
                return {"error": response}
                
            # Clean JSON (Gemini sometimes wraps in markdown)
            response = response.replace("```json", "").replace("```", "").strip()
            data = json.loads(response)
            return data
        except Exception as e:
            print(f"AI Analysis Failed. Response: {response[:100]}... Error: {e}")
            return None

    def research_lead(self, lead_id):
        """Researches a specific lead from the DB and updates it."""
        conn = db.get_connection()
        if not conn:
            print("[OFFLINE] Cannot research — Supabase is unreachable.")
            return False
        
        try:    
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            
            # Fetch lead from the flat V2 leads table
            cursor.execute("SELECT id, name, bio, notes, source, website FROM leads WHERE id = %s", (lead_id,))
            lead = cursor.fetchone()
            
            if not lead:
                return False
            
            name = lead.get('name', 'Unknown')
            bio = lead.get('bio') or lead.get('notes') or ''
            url = lead.get('website')
            
            print(f"Researching {name}...")
            
            # RUN ANALYSIS
            result = self.analyze_company(name, url, bio)
            
            if result:
                if "error" in result:
                    return result["error"]
                
                s_sum = result.get('summary', '')
                s_ice = result.get('ice_breaker', '')
                
                # Handle pain_points if list
                p_points = result.get('pain_points', '')
                if isinstance(p_points, list):
                    p_points = ", ".join(p_points)
                elif isinstance(p_points, dict):
                    p_points = json.dumps(p_points)
                
                # Update lead in Supabase — store research in notes/ice_breaker/pain_points
                cursor.execute("""
                    UPDATE leads 
                    SET notes = %s, 
                        ice_breaker = %s, 
                        pain_points = %s,
                        score = COALESCE(score, 0) + 10
                    WHERE id = %s
                """, (s_sum, s_ice, p_points, lead_id))
                conn.commit()
                return True
            
            return False
                
        except Exception as e:
            print(f"Research error: {e}")
            if conn:
                conn.rollback()
            return False
        finally:
            if conn:
                conn.close()

    def get_pending_leads(self, limit=5, user_id=None):
        """Gets leads that haven't been researched yet (no ice_breaker)."""
        conn = db.get_connection()
        if not conn:
            return []
        try:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            if user_id:
                cursor.execute("""
                    SELECT id, name FROM leads 
                    WHERE (ice_breaker IS NULL OR ice_breaker = '') 
                    AND user_id = %s
                    ORDER BY id DESC LIMIT %s
                """, (user_id, limit))
            else:
                cursor.execute("""
                    SELECT id, name FROM leads 
                    WHERE ice_breaker IS NULL OR ice_breaker = ''
                    ORDER BY id DESC LIMIT %s
                """, (limit,))
            return cursor.fetchall()
        except Exception as e:
            print(f"Error fetching pending leads: {e}")
            return []
        finally:
            conn.close()

if __name__ == "__main__":
    agent = ResearchAgent()
