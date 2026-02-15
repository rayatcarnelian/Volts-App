
import os
import time
from datetime import datetime
from fpdf import FPDF

class DigitalAnalyst:
    """
    The Analyst: Autonomous Technical Auditor.
    Scans websites for objective errors (SEO, Speed, Security) and generates PDF reports.
    """
    
    def __init__(self, output_dir="assets/reports"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
        
    def audit_site(self, url, driver):
        """
        Performs a rapid technical audit using the running Selenium driver.
        Returns a dictionary of findings.
        """
        audit_data = {
            "url": url,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "checks": [],
            "score": 100,
            "critical_issues": 0
        }
        
        try:
            # 1. SSL Check
            if url.startswith("https"):
                audit_data["checks"].append({"name": "SSL Security", "status": "PASS", "details": "Site is secured via HTTPS."})
            else:
                audit_data["checks"].append({"name": "SSL Security", "status": "FAIL", "details": "Site is NOT secure (HTTP only)."})
                audit_data["score"] -= 20
                audit_data["critical_issues"] += 1

            # 2. Page Title (SEO)
            try:
                title = driver.title
                if title and len(title) > 0:
                    audit_data["checks"].append({"name": "Meta Title", "status": "PASS", "details": f"Found: '{title[:30]}...'"})
                else:
                    audit_data["checks"].append({"name": "Meta Title", "status": "FAIL", "details": "Missing Meta Title."})
                    audit_data["score"] -= 10
            except:
                audit_data["checks"].append({"name": "Meta Title", "status": "FAIL", "details": "Could not extract title."})

            # 3. H1 Tag (Structure)
            try:
                h1s = driver.find_elements("tag name", "h1")
                if len(h1s) == 1:
                    audit_data["checks"].append({"name": "H1 Structure", "status": "PASS", "details": "Excellent. Single H1 tag found."})
                elif len(h1s) == 0:
                    audit_data["checks"].append({"name": "H1 Structure", "status": "FAIL", "details": "No H1 tag found (Bad for SEO)."})
                    audit_data["score"] -= 15
                else:
                    audit_data["checks"].append({"name": "H1 Structure", "status": "WARN", "details": f"Found {len(h1s)} H1 tags. Should only be 1."})
                    audit_data["score"] -= 5
            except:
                pass

            # 4. Mobile Responsiveness (Viewport)
            try:
                meta_viewport = driver.find_elements("css selector", "meta[name='viewport']")
                if meta_viewport:
                    audit_data["checks"].append({"name": "Mobile Optimization", "status": "PASS", "details": "Viewport tag present."})
                else:
                    audit_data["checks"].append({"name": "Mobile Optimization", "status": "FAIL", "details": "Not mobile optimized (Missing Viewport)."})
                    audit_data["score"] -= 20
                    audit_data["critical_issues"] += 1
            except:
                pass

            # 5. Load Speed (Simulated/Heuristic)
            # Since we are using 'eager' load strategy, accurate timing is hard, but we can check page size text
            try:
                body_text = driver.find_element("tag name", "body").text
                if len(body_text) < 200:
                    audit_data["checks"].append({"name": "Content Depth", "status": "WARN", "details": "Page content is very thin (<200 chars)."})
                    audit_data["score"] -= 10
                else:
                    audit_data["checks"].append({"name": "Content Depth", "status": "PASS", "details": "Good content volume."})
            except:
                pass

        except Exception as e:
            print(f"Audit Error: {e}")
            audit_data["checks"].append({"name": "System Audit", "status": "ERROR", "details": str(e)})

        # Final Score Logic
        if audit_data["score"] < 0: audit_data["score"] = 0
        
        return audit_data

    def generate_report(self, business_name, audit_data):
        """
        Generates a PDF report from the audit data.
        """
        try:
            pdf = FPDF()
            pdf.add_page()
            
            # -- HEADER --
            pdf.set_font("Helvetica", "B", 24)
            pdf.cell(0, 10, "CONFIDENTIAL AUDIT REPORT", new_x="LMARGIN", new_y="NEXT", align="C")
            pdf.ln(5)
            
            pdf.set_font("Helvetica", "", 12)
            pdf.set_text_color(100, 100, 100)
            pdf.cell(0, 10, f"Prepared for: {business_name}", new_x="LMARGIN", new_y="NEXT", align="C")
            pdf.cell(0, 10, f"Date: {audit_data['timestamp']}", new_x="LMARGIN", new_y="NEXT", align="C")
            pdf.ln(10)
            
            # -- SCORE CARD --
            pdf.set_font("Helvetica", "B", 16)
            pdf.set_text_color(0, 0, 0)
            pdf.cell(0, 10, "Digital Health Score:", new_x="LMARGIN", new_y="NEXT")
            
            score = audit_data["score"]
            color = (0, 200, 0) if score > 80 else (200, 160, 0) if score > 50 else (200, 0, 0)
            pdf.set_text_color(*color)
            pdf.set_font("Helvetica", "B", 40)
            pdf.cell(0, 20, f"{score}/100", new_x="LMARGIN", new_y="NEXT")
            pdf.ln(5)
            
            # -- FINDINGS --
            pdf.set_text_color(0, 0, 0)
            pdf.set_font("Helvetica", "B", 14)
            pdf.cell(0, 10, "Key Findings:", new_x="LMARGIN", new_y="NEXT")
            pdf.ln(2)
            
            pdf.set_font("Helvetica", "", 11)
            
            col_widths = [40, 30, 110] # Name, Status, Details
            
            # Header Row
            pdf.set_fill_color(240, 240, 240)
            pdf.set_font("Helvetica", "B", 11)
            pdf.cell(col_widths[0], 10, "Check", border=1, fill=True)
            pdf.cell(col_widths[1], 10, "Status", border=1, fill=True)
            pdf.cell(col_widths[2], 10, "Details", border=1, fill=True)
            pdf.ln()
            
            pdf.set_font("Helvetica", "", 11)
            for check in audit_data["checks"]:
                pdf.cell(col_widths[0], 10, check["name"], border=1)
                
                # Status Color
                status = check["status"]
                if status == "PASS": pdf.set_text_color(0, 150, 0)
                elif status == "FAIL": pdf.set_text_color(200, 0, 0)
                else: pdf.set_text_color(200, 150, 0)
                
                pdf.cell(col_widths[1], 10, status, border=1)
                
                pdf.set_text_color(0, 0, 0)
                pdf.cell(col_widths[2], 10, check["details"], border=1)
                pdf.ln()
                
            pdf.ln(10)
            
            # -- SUMMARY --
            pdf.set_font("Helvetica", "I", 10)
            pdf.multi_cell(0, 10, "This automated report was generated by Volts Intelligence. Critical errors (FAIL) usually impact conversion rates and Google rankings directly.")
            
            # Save
            safe_name = "".join([c for c in business_name if c.isalpha() or c.isdigit()]).rstrip()
            filename = f"Audit_{safe_name}_{int(time.time())}.pdf"
            filepath = os.path.join(self.output_dir, filename)
            
            pdf.output(filepath)
            
            # Return absolute path
            return os.path.abspath(filepath)
            
        except Exception as e:
            print(f"PDF Gen Error: {e}")
            return None

# Test
if __name__ == "__main__":
    analyst = DigitalAnalyst()
    # Mock data for testing
    mock_data = {
        "url": "https://example.com",
        "timestamp": "2026-01-31",
        "score": 45,
        "critical_issues": 2,
        "checks": [
            {"name": "SSL Security", "status": "PASS", "details": "Secure."},
            {"name": "Mobile Optimization", "status": "FAIL", "details": "Missing Viewport tag."},
            {"name": "H1 Structure", "status": "FAIL", "details": "No H1 tag found."}
        ]
    }
    path = analyst.generate_report("TestBusiness", mock_data)
    print(f"Report generated: {path}")
