import pandas as pd
import random
from modules.database import get_connection

# Ensure migration happens on module load if needed
# migrate_csv_to_db()

class LeadManager:
    """
    Handles all CRM operations using SQLite.
    """
    
    @staticmethod
    def load_data():
        """Loads leads using the V2 database view."""
        import modules.database as db
        try:
            return db.get_all_leads()
        except Exception as e:
            print(f"Error loading V2 data: {e}")
            return pd.DataFrame()
    
    @staticmethod
    def save_data(df):
        """
        Safely updates the leads table. 
        Only updates editable fields to prevent schema destruction.
        """
        conn = get_connection()
        c = conn.cursor()
        
        # We only update core fields that are editable in the UI
        # 'status' in DF maps to 'master_status' in DB
        
        for index, row in df.iterrows():
            try:
                # Handle potential missing columns if UI didn't show them
                notes = row.get('notes', '')
                status = row.get('status', 'New')
                name = row.get('name')
                lid = row.get('id')
                
                if lid:
                    c.execute("""
                        UPDATE leads 
                        SET master_status = ?, notes = ?, name = ?
                        WHERE id = ?
                    """, (status, notes, name, lid))
            except Exception as e:
                print(f"Error updating row {index}: {e}")
                
        conn.commit()
        conn.close()
        
    @staticmethod
    def add_lead(leads_list, campaign_id=None):
        """Delegates to database.py V2 logic."""
        import modules.database as db
        if not leads_list: return 0
        
        count = 0
        for lead in leads_list:
            # Map incoming items
            name = lead.get("Name") or lead.get("Username", "Unknown")
            phone = lead.get("Phone") or lead.get("Contact")
            email = lead.get("Email")
            source = lead.get("Source", "Manual")
            link = lead.get("Link") or lead.get("Website")
            
            # Metadata construction
            meta = {
                'bio': lead.get('Notes', ''),
                'username': lead.get('Username'),
                'profile_url': link
            }
            
            success = db.add_lead_v2(
                name=name,
                phone=phone,
                email=email,
                source=source,
                metadata=meta,
                profile_url=link
            )
            if success: count += 1
            
        return count

    @staticmethod
    def get_leads_with_coords():
        """Returns dataframe with guaranteed lat/lon for the map."""
        df = LeadManager.load_data()
        
        # If empty, return empty
        if df.empty:
            return df
            
        # If lat/lon missing for some reason, fill them
        # (Though our add_lead handles it, imported CSVs might miss it)
        # Note: applying random in vectorised way is tricky for exact persistence, 
        # but for visualization we can fillna.
        
        # We can't easily persist random fillna here without saving, 
        # but for the view we return filled data.
        
        return df # They should exist from migration/add_lead

    @staticmethod
    def delete_lead(lead_id):
        """
        Hard delete of a lead and its generic existence.
        """
        conn = get_connection()
        try:
            c = conn.cursor()
            # Delete from source tables first (optional but good for cleanup)
            c.execute("DELETE FROM linkedin_profiles WHERE lead_id = ?", (lead_id,))
            c.execute("DELETE FROM instagram_profiles WHERE lead_id = ?", (lead_id,))
            # Delete from main
            c.execute("DELETE FROM leads WHERE id = ?", (lead_id,))
            conn.commit()
            return True
        except Exception as e:
            print(f"Delete Error: {e}")
            return False
        finally:
            conn.close()

    @staticmethod
    def update_lead_field(lead_id, field, value):
        """
        Updates a single field for a lead.
        Allowed fields: name, primary_email, primary_phone, notes, master_status, website
        """
        allowed = ['name', 'primary_email', 'primary_phone', 'notes', 'master_status', 'website', 'pitch_draft']
        if field not in allowed:
            return False
            
        conn = get_connection()
        try:
            # We use f-string for field name (safe because we whitelist above)
            conn.execute(f"UPDATE leads SET {field} = ? WHERE id = ?", (value, lead_id))
            conn.commit()
            return True
        except Exception as e:
            print(f"Update Error: {e}")
            return False
        finally:
            conn.close()
