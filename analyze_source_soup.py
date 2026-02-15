
from bs4 import BeautifulSoup
import os

filepath = "e:\\Leads app\\fb_debug_source.html"

if not os.path.exists(filepath):
    print(f"File not found: {filepath}")
    exit()

print(f"Parsing {filepath}...")
with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
    soup = BeautifulSoup(f, "html.parser")

print("--- Searching for 'Like' buttons ---")
# Find elements with aria-label="Like"
likes = soup.find_all(attrs={"aria-label": "Like"})
print(f"Found {len(likes)} elements with aria-label='Like'")

for i, like in enumerate(likes[:3]):
    print(f"\n[Like Button {i+1}]")
    print(f"  Tag: {like.name}")
    print(f"  Class: {like.get('class')}")
    
    # Walk up
    parent = like.parent
    level = 0
    while parent and level < 20:
        level += 1
        role = parent.get("role")
        cls = parent.get("class")
        
        prefix = "  " * level
        print(f"{prefix}L{level}: <{parent.name}> Attrs: {parent.attrs}")
        
        if role == "article":
            print(f"{prefix}>>> MATCH: Found role='article' at Level {level}")
            # Is there any other distinguishing feature?
            # Check for "aria-posinset" or "aria-setsize" which are common in lists
            print(f"{prefix}    Attributes: {parent.attrs}")
            break
        
        parent = parent.parent

print("\n--- Searching for 'role=feed' ---")
feeds = soup.find_all(attrs={"role": "feed"})
print(f"Found {len(feeds)} feeds.")
