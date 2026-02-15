"""
Script to clean main.py by removing old AI Avatar code
"""

# Read the file
with open("E:/Leads app/main.py", "r", encoding="utf-8") as f:
    lines = f.readlines()

# Find the line numbers
heygen_end_found = False
ken_burns_start = None

for i, line in enumerate(lines):
    # Find where "render_heygen_studio()" ends
    if "render_heygen_studio()" in line and not heygen_end_found:
        heygen_end = i + 1  # Line after render call
        heygen_end_found = True
   
    # Find where Ken Burns starts  
    if "else:  # Ken Burns Animation" in line:
        ken_burns_start = i
        break

if heygen_end_found and ken_burns_start:
    print(f"HeyGen ends at line {heygen_end}")
    print(f"Ken Burns starts at line {ken_burns_start}")
    print(f"Removing {ken_burns_start - heygen_end} lines of old code")
    
    # Keep everything up to heygen_end, skip old code, keep Ken Burns onwards
    new_lines = lines[:heygen_end +1] + ["\n        \n        "] + lines[ken_burns_start:]
    
    # Write back
    with open("E:/Leads app/main.py", "w", encoding="utf-8") as f:
        f.writelines(new_lines)
    
    print("✅ Done! Old code removed.")
else:
    print("❌ Could not find markers")
    print(f"HeyGen found: {heygen_end_found}")
    print(f"Ken Burns start: {ken_burns_start}")
