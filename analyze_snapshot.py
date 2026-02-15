import json
import re

filename = "iproperty_debug.html"

try:
    with open(filename, "r", encoding="utf-8") as f:
        content = f.read()

    print(f"File Size: {len(content)} bytes")

    # 2. Search for Date & Pagination
    print("\n--- PATTERN ANALYSIS ---")
    patterns = [
        "Posted", "Updated", "days ago", "hours ago", "today", "yesterday", # Dates
        "pagination", "next-page", "Go to next page", "page-item"           # Pagination
    ]
    
    for p in patterns:
        count = content.count(p)
        print(f"'{p}': found {count} times")
        if count > 0:
            pos = content.find(p)
            snippet = content[max(0, pos-100):min(len(content), pos+100)]
            print(f"   Context: ...{snippet}...")

    # 4. Analyze Contact & Agent Links
    print("\n--- CONTACT & LINK ANALYSIS ---")
    
    # Find "Contact" buttons parent href
    base = 0
    for i in range(5):
        pos = content.find("Contact Agent", base)
        if pos == -1: break
        
        # Look backwards for the start of the wrapping <a href="...">
        # This is a bit rough but effective for a snapshot check
        start_scan = max(0, pos-150)
        snippet = content[start_scan:pos+50]
        
        hrefs = re.findall(r'href="([^"]+)"', snippet)
        
        print(f"\n[CONTACT LINK {i+1}]")
        print(f"Index: {pos}")
        print(f"Hrefs found nearby: {hrefs}")
        
        base = pos + 1

    # 5. Deep Regex Search
    print("\n--- DEEP DATA HUNT ---")
    
    # Phone numbers (Malaysia: +60 or 01...)
    # Regex: (01\d{1}-?\d{7,8}) or (\+?601\d{1}-?\d{7,8})
    phone_pattern = r'(?:\+?6?01\d{1}[-\s]?\d{7,8})'
    phones = re.findall(phone_pattern, content)
    print(f"Potential Phones found: {len(phones)}")
    print(f"Sample: {phones[:10]}")
    
    # Emails
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    emails = re.findall(email_pattern, content)
    print(f"Emails found: {len(emails)}")
    print(f"Sample: {emails[:10]}")
    
    # Check for whatsapp links specifically again
    whatsapp = re.findall(r'wa\.me/(\d+)', content)
    print(f"WhatsApp Links: {len(whatsapp)}")
    print(f"Sample: {whatsapp[:10]}")

except Exception as e:
    print(f"Error: {e}")
