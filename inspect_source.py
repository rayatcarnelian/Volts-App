
import re

def inspect_file(filepath, keywords):
    try:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
            
        print(f"File Size: {len(content)} bytes")
        
        for keyword in keywords:
            print(f"\n--- Searching for: {keyword} ---")
            matches = [m.start() for m in re.finditer(re.escape(keyword), content)]
            print(f"Found {len(matches)} matches.")
            
            # Show context for first 5 matches
            for i, start_idx in enumerate(matches[:5]):
                start = max(0, start_idx - 100)
                end = min(len(content), start_idx + 300)
                snippet = content[start:end].replace("\n", " ")
                print(f"Match {i+1}: ...{snippet}...")
                
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    inspect_file("e:\\Leads app\\fb_debug_source.html", ["aria-label=\"Like\"", "role=\"feed\"", "role=\"article\"", "Join Group", "unavailable"])
