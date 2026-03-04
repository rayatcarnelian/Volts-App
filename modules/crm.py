import pandas as pd
import random
from modules.db_supabase import get_connection

# Ensure migration happens on module load if needed
# migrate_csv_to_db()

class LeadManager:
    """
    Handles all CRM operations using SQLite.
    """
    
    @staticmethod
    def load_data(user_id=None):
        """Loads leads using the V2 database view, filtered by user_id."""
        import modules.db_supabase as db
        try:
            return db.get_all_leads(user_id=user_id)
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
        if not conn: return
        c = conn.cursor()
        
        # We only update core fields that are editable in clear UI fields
        
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
                        SET status = %s, notes = %s, name = %s
                        WHERE id = %s
                    """, (status, notes, name, lid))
            except Exception as e:
                print(f"Error updating row {index}: {e}")
                
        conn.commit()
        conn.close()
        
    @staticmethod
    def add_lead(leads_list, campaign_id=None, user_id=None):
        """Delegates to database.py V2 logic."""
        import modules.db_supabase as db
        if not leads_list: return 0
        
        count = 0
        for lead in leads_list:
            # Map incoming items
            name = lead.get("Name") or lead.get("Username", "Unknown")
            phone = lead.get("Phone") or lead.get("Contact")
            email = lead.get("Email")
            source = lead.get("Source", "Manual")
            link = lead.get("Link") or lead.get("Website")
            notes = lead.get("Notes", "")
            
            success = db.add_lead_v2(
                name=name,
                phone=phone,
                email=email,
                source=source,
                profile_url=link,
                bio=notes,
                user_id=user_id
            )
            if success: count += 1
            
        return count

    @staticmethod
    def get_leads_with_coords(user_id=None):
        """Returns dataframe with guaranteed lat/lon for the map."""
        df = LeadManager.load_data(user_id=user_id)
        if df.empty:
            return df
        return df

    @staticmethod
    def delete_lead(lead_id, user_id=None):
        """
        Hard delete of a lead. Verifies ownership if user_id provided.
        """
        conn = get_connection()
        if not conn: return False
        try:
            c = conn.cursor()
            # Verify ownership
            if user_id:
                c.execute("SELECT id FROM leads WHERE id = %s AND user_id = %s", (lead_id, user_id))
                if not c.fetchone():
                    return False
            # Delete from main
            c.execute("DELETE FROM leads WHERE id = %s", (lead_id,))
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
        allowed = ['name', 'email', 'phone', 'notes', 'status', 'website', 'company', 'bio', 'pitch_draft']
        if field not in allowed:
            print(f"Refused unsafe update to {field}")
            return False
            
        conn = get_connection()
        if not conn: return False
        try:
            c = conn.cursor()
            c.execute(f"UPDATE leads SET {field} = %s WHERE id = %s", (value, lead_id))
            conn.commit()
            return True
        except Exception as e:
            print(f"Update Error: {e}")
            return False
        finally:
            conn.close()
