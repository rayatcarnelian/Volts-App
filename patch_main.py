import os

def patch_file():
    target = "e:\\Leads app\\main.py"
    if not os.path.exists(target):
        print("Target not found.")
        return

    with open(target, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    start_idx = -1
    end_idx = -1

    for i, line in enumerate(lines):
        if "# --- MODULE 4: CALL CENTER (UNIFIED) ---" in line:
            start_idx = i
        if "# --- MODULE 5: THE SNIPER (Placeholder) ---" in line:
            end_idx = i
            break # Stop at Module 5 start

    if start_idx != -1 and end_idx != -1:
        print(f"Found block: {start_idx} to {end_idx}")
        
        new_content = [
            "# --- MODULE 4: CALL CENTER (UNIFIED) ---\n",
            "elif \"4. CALL CENTER\" in page:\n",
            "    from modules.call_center_ui import render_call_center_ui\n",
            "    render_call_center_ui()\n",
            "\n"
        ]
        
        # Slice and Dice
        final_lines = lines[:start_idx] + new_content + lines[end_idx:]
        
        with open(target, 'w', encoding='utf-8') as f:
            f.writelines(final_lines)
            
        print("Success: File patched.")
    else:
        print(f"Indices not found. Start: {start_idx}, End: {end_idx}")
        # Debug print snippet
        if start_idx != -1:
             print("Start found.")
        else:
             print("Start NOT found.")

patch_file()
