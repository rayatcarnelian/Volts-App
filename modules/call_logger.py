import pandas as pd
import os
from datetime import datetime

LOG_FILE = "call_logs.xlsx"

class CallLogger:
    @staticmethod
    def save_logs(calls_data):
        """
        Saves a list of Vapi Call Objects to Excel.
        """
        records = []
        for call in calls_data:
            # Extract basic info
            call_id = call.get('id')
            timestamp = call.get('createdAt')
            status = call.get('status')
            cost = call.get('cost', 0)
            
            # Extract Phone Numbers
            customer_num = call.get('customer', {}).get('number', 'Unknown')
            
            # Extract Transcript (handle if it's missing or in different format)
            transcript = call.get('transcript', "")
            if not transcript and 'messages' in call:
                # Reconstruct transcript from messages if raw transcript is missing
                msgs = call.get('messages', [])
                transcript = "\n".join([f"{m.get('role')}: {m.get('message')}" for m in msgs]) # Vapi message format varies, simplistic fallback
            
            # Summary (Vapi sometimes provides analysis)
            summary = call.get('analysis', {}).get('summary', '')

            records.append({
                "Call ID": call_id,
                "Time": timestamp,
                "Status": status,
                "Customer": customer_num,
                "Cost ($)": cost,
                "Summary": summary,
                "Transcript": transcript
            })
            
        if not records:
            return "No data to save."

        new_df = pd.DataFrame(records)
        
        # Check if file exists to append or create
        if os.path.exists(LOG_FILE):
            try:
                existing_df = pd.read_excel(LOG_FILE)
                # Combine and remove duplicates based on Call ID
                combined_df = pd.concat([existing_df, new_df]).drop_duplicates(subset=['Call ID'], keep='last')
                combined_df.to_excel(LOG_FILE, index=False)
            except Exception as e:
                return f"Error updating file: {e}"
        else:
            new_df.to_excel(LOG_FILE, index=False)
            
        return f"Saved {len(new_df)} records to {LOG_FILE}"
