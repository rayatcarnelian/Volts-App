import streamlit as st
import pandas as pd
from modules import database_v2_schema as db

def render_admin_page():
    st.title("🛡️ Admin Command Center")
    
    # 1. User Management
    st.subheader("User Database")
    conn = db.get_connection()
    users = pd.read_sql("SELECT id, email, tier, credits_image, credits_video, call_minutes_used, last_login FROM users", conn)
    conn.close()
    
    edited_users = st.data_editor(
        users,
        column_config={
            "tier": st.column_config.SelectboxColumn("Tier", options=["FREE", "PRO", "ADMIN"]),
            "credits_image": st.column_config.NumberColumn("Img Creds"),
            "credits_video": st.column_config.NumberColumn("Vid Creds"),
        },
        use_container_width=True,
        hide_index=True
    )
    
    if st.button("💾 Save User Changes"):
        conn = db.get_connection()
        c = conn.cursor()
        for i, row in edited_users.iterrows():
            c.execute("UPDATE users SET tier=?, credits_image=?, credits_video=? WHERE id=?", 
                      (row['tier'], row['credits_image'], row['credits_video'], row['id']))
        conn.commit()
        conn.close()
        st.success("User database updated.")
        st.rerun()

    st.markdown("---")
    
    # 2. System Stats
    st.subheader("System Health")
    c1, c2, c3 = st.columns(3)
    c1.metric("Total Users", len(users))
    c2.metric("Pro Users", len(users[users['tier'] == 'PRO']))
    c3.metric("Free Users", len(users[users['tier'] == 'FREE']))
