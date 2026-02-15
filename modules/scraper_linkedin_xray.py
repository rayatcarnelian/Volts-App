import logging
import streamlit as st
from modules.search_engine import engine
from modules import database as db

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("LinkedInXRay")

class LinkedInXRay:
    """
    Enterprise-grade LinkedIn X-Ray scraper using multi-provider Hybrid Engine.
    """
    
    def hunt_targets(self, role="Property Developer", location="Kuala Lumpur", limit=10):
        """
        Main entry point for hunting leads via search engines.
        """
        query = f'"{role}" "{location}" LinkedIn profile'
        st.info(f"🔍 Hunting for {role} in {location} using Hybrid Engine...")
        
        try:
            # Over-fetch by 50% to account for non-profile filtering
            search_limit = int(limit * 1.5)
            results = engine.search(query, limit=search_limit)
            
            if not results:
                st.warning("⚠️ No targets found. Try broader terms or check connection.")
                return 0
                
            saved_count = 0
            for r in results:
                if saved_count >= limit:
                    break
                    
                title = r.get('title', 'LinkedIn Profile')
                link = r.get('link', '')
                snippet = r.get('snippet', '')
                
                if "linkedin.com/in/" not in link:
                    continue
                
                # Check for duplicates
                if db.get_lead_by_link(link):
                    continue
                
                # Extract clean name from title (e.g., "John Doe - Property Developer | LinkedIn")
                name = title.split(' - ')[0].replace(' | LinkedIn', '').replace('LinkedIn', '').strip()
                if not name or len(name) > 100:
                    name = "LinkedIn Member"
                
                # Save to DB
                success = db.add_lead(
                    name=name,
                    company="Unknown",
                    role=role,
                    location=location,
                    link=link,
                    source="LinkedIn X-Ray",
                    bio=snippet
                )
                
                if success:
                    saved_count += 1
                    try:
                        # Clean name for console logs
                        safe_name = name.encode('ascii', 'ignore').decode('ascii')
                        logger.info(f"Saved candidate: {safe_name}")
                    except:
                        logger.info("Saved candidate with special characters.")
                    st.toast(f"Target Acquired: {name}", icon="🎯")
            
            st.success(f"✅ Successfully acquired {saved_count} new leads!")
            return saved_count
            
        except Exception as e:
            st.error(f"❌ Critical Search Error: {e}")
            logger.error(f"Search Error: {e}")
            return 0

    def close(self):
        """Placeholder for backward compatibility."""
        pass
