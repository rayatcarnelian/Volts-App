import logging
import streamlit as st
from modules.search_engine import engine
import modules.db_supabase as db

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("LinkedInXRayMinimal")

class LinkedInXRayMinimal:
    """
    A lightweight LinkedIn profile scraper using the centralized SearchEngine.
    """
    
    def hunt(self, role, location, limit=5):
        """
        Executes a LinkedIn X-Ray search using the robust SearchEngine.
        """
        query = f'"{role}" "{location}" LinkedIn profile'
        st.info(f"🔍 Hunting for {role} in {location} using Hybrid Engine...")
        
        try:
            # Over-fetch by 50% to account for filtering
            search_limit = int(limit * 1.5)
            results = engine.search(query, limit=search_limit)
            
            profiles = []
            for r in results:
                title = r.get('title', 'LinkedIn Profile')
                link = r.get('link', '')
                snippet = r.get('snippet', '')
                
                # Cleanup: LinkedIn links sometimes have DDG redirects, but DDGS handles it well.
                # If using Playwright, we might need more cleanup.
                
                if "linkedin.com/in/" in link:
                    profiles.append({
                        'name': title.split(' - ')[0].replace(' | LinkedIn', '').strip(),
                        'link': link,
                        'snippet': snippet,
                        'source': 'DuckDuckGo X-Ray'
                    })
            
            if not profiles:
                st.warning("⚠️ No valid LinkedIn profiles found in search results.")
                return []
                
            st.success(f"✅ Found {len(profiles)} targets!")
            return profiles
            
        except Exception as e:
            st.error(f"❌ Scraper Error: {e}")
            logger.error(f"Scraper Error: {e}")
            return []

    def process_leads(self, leads, role, location):
        """
        Saves found leads to the unified database.
        """
        if not leads:
            return 0
            
        count = 0
        for lead in leads:
            # Check for duplicates
            if db.get_lead_by_link(lead['link']):
                continue
                
            db.add_lead(
                name=lead['name'],
                company="Unknown",
                role=role,
                location=location,
                link=lead['link'],
                source=f"LinkedIn X-Ray ({location})"
            )
            count += 1
        return count
