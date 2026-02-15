import os
import pypdf

def ingest_knowledge():
    profile_path = "assets/Volts Company Profile (1).pdf"
    knowledge_path = "assets/business_profile.txt"
    
    text_content = ""
    
    # 1. Read PDF
    if os.path.exists(profile_path):
        try:
            reader = pypdf.PdfReader(profile_path)
            for page in reader.pages:
                text_content += page.extract_text() + "\n"
            print(f"Extracted {len(text_content)} chars from PDF.")
        except Exception as e:
            print(f"Error reading PDF: {e}")
            return
    else:
        print("PDF not found.")
        return

    # 2. Append to Business Profile (if not already there)
    # We'll overwrite the [BUSINESS PROFILE] section or just append for now
    
    current_content = ""
    if os.path.exists(knowledge_path):
         with open(knowledge_path, "r") as f:
             current_content = f.read()
             
    new_knowledge = current_content + "\n\n[EXTRACTED FROM PDF]\n" + text_content
    
    with open(knowledge_path, "w", encoding="utf-8") as f:
        f.write(new_knowledge)
    
    print("Knowledge Base Updated.")

if __name__ == "__main__":
    ingest_knowledge()
