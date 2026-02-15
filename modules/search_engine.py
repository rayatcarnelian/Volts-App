import time
import random
import logging
import re
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

try:
    from googlesearch import search as gsearch
except ImportError:
    gsearch = None

try:
    from curl_cffi import requests as crequests
except ImportError:
    crequests = None

# Safer playwright_stealth import
try:
    import playwright_stealth
except ImportError:
    playwright_stealth = None

# Configure Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("SearchEngine")

class SearchEngine:
    """
    Enterprise-grade Hybrid Search Engine.
    Uses a rotating quad-provider strategy: 
    1. DDGS (Internal API)
    2. Google (googlesearch-python)
    3. TLS-Impersonated Scraping (curl_cffi + DDG Lite)
    4. Playwright Stealth (DDG Lite)
    """
    
    def __init__(self):
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        ]

    def search(self, query, limit=10):
        """
        Main search entry point. Tries all providers and aggregates results.
        """
        all_results = []
        seen_links = set()
        
        providers = [
            ("DDGS", self._search_ddgs),
            ("Google", self._search_google) if gsearch else None,
            ("curl_cffi", self._search_curl_cffi_lite) if crequests else None,
            ("Playwright", self._search_playwright_ddg_lite)
        ]
        
        for name, func in providers:
            if not func: continue
            if len(all_results) >= limit: break
            
            logger.info(f"Attempting {name} search...")
            remaining = limit - len(all_results)
            new_results = func(query, remaining)
            
            for r in new_results:
                link = r.get('link')
                if link and link not in seen_links:
                    seen_links.add(link)
                    all_results.append(r)
                    
        if not all_results:
            logger.error("All search providers failed to produce results.")
            
        return all_results[:limit]

    def _search_ddgs(self, query, limit):
        try:
            from ddgs import DDGS
            with DDGS() as ddgs:
                results = []
                for r in ddgs.text(query, max_results=limit):
                    results.append({
                        'title': r.get('title', ''),
                        'link': r.get('href', ''),
                        'snippet': r.get('body', '')
                    })
                return results
        except Exception as e:
            logger.error(f"DDGS Error: {e}")
            return []

    def _search_google(self, query, limit):
        try:
            results = []
            for url in gsearch(query, num_results=limit, sleep_interval=5):
                results.append({
                    'title': "LinkedIn Profile", 
                    'link': url,
                    'snippet': ""
                })
            return results
        except Exception as e:
            logger.error(f"Google Search Error: {e}")
            return []

    def _search_curl_cffi_lite(self, query, limit):
        try:
            # TLS Impersonation (impersonate Chrome)
            url = f"https://lite.duckduckgo.com/lite/?q={query}"
            headers = {"User-Agent": random.choice(self.user_agents)}
            
            # Use 'chrome110' impersonation to bypass TLS fingerprinting
            r = crequests.get(url, impersonate="chrome110", headers=headers, timeout=30)
            if r.status_code != 200:
                logger.error(f"curl_cffi Status Code: {r.status_code}")
                return []
            
            soup = BeautifulSoup(r.text, 'html.parser')
            results = []
            # Lite mode: each result is in a <tr> or similar in a table
            for row in soup.find_all('a', class_='result-link'):
                if len(results) >= limit: break
                results.append({
                    'title': row.get_text().strip(),
                    'link': row['href'],
                    'snippet': ""
                })
            return results
        except Exception as e:
            logger.error(f"curl_cffi Error: {e}")
            return []

    def _search_playwright_ddg_lite(self, query, limit):
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page(user_agent=random.choice(self.user_agents))
                
                if playwright_stealth:
                    try:
                        from playwright_stealth import stealth_sync
                        stealth_sync(page)
                    except: pass
                
                url = f"https://lite.duckduckgo.com/lite/?q={query}"
                page.goto(url, timeout=30000)
                
                # Result links in Lite are 'a.result-link'
                try:
                    page.wait_for_selector("a.result-link", timeout=30000)
                except:
                    logger.error("Playwright Lite: No results found or timed out.")
                    browser.close()
                    return []
                
                results = []
                elements = page.query_selector_all("a.result-link")
                for el in elements[:limit]:
                    link = el.get_attribute("href")
                    title = el.inner_text().strip()
                    if link and title:
                        results.append({'title': title, 'link': link, 'snippet': ""})
                
                browser.close()
                return results
        except Exception as e:
            logger.error(f"Playwright Lite Error: {e}")
            return []

# Singleton
engine = SearchEngine()
