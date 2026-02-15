"""
HeyGen-Style Video Studio Interface
Professional avatar video generation with grid layout
"""

import streamlit as st
import os
import sys

# Fix imports for standalone execution
if __name__ == "__main__":
    # Add parent directory to path when running standalone
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.avatar_library import get_all_avatars, filter_avatars, AVATAR_CATEGORIES
from modules.voice_library import get_all_voices, filter_voices, VOICE_CATEGORIES, generate_voice_preview
from modules.talking_avatar import FreeTalkingAvatarStudio

def render_heygen_studio():
    """
    Render HeyGen-style video studio interface
    """
    
    # Custom CSS for HeyGen-style UI
    st.markdown("""
    <style>
        /* HeyGen Color Scheme */
        .heygen-container {
            background-color: #ffffff;
            padding: 20px;
            border-radius: 12px;
        }
        
        .avatar-grid-item {
            border: 2px solid #E5E7EB;
            border-radius: 8px;
            padding: 8px;
            cursor: pointer;
            transition: all 0.2s;
        }
        
        .avatar-grid-item:hover {
            border-color: #6366F1;
            box-shadow: 0 4px 12px rgba(99, 102, 241, 0.2);
        }
        
        .selected-avatar {
            border-color: #6366F1;
            background-color: #F5F5FF;
        }
        
        .generate-btn {
            background: linear-gradient(135deg, #6366F1 0%, #8B5CF6 100%);
            color: white;
            font-weight: 600;
            padding: 14px 24px;
            border-radius: 8px;
            border: none;
            width: 100%;
        }
    </style>
    """, unsafe_allow_html=True)
    
    st.title("🎬 AI Avatar Video Studio")
    st.caption("Create professional presenter videos with emotion-aware AI")
    st.markdown("---")
    
    # Main 3-column layout
    col_avatars, col_preview, col_controls = st.columns([1, 1.5, 1])
    
    # ============ LEFT: AVATAR SELECTION ============
    with col_avatars:
        st.markdown("### 👤 Select Avatar")
        
        # Category filter
        avatar_category = st.selectbox(
            "Category",
            ["All"] + list(AVATAR_CATEGORIES.keys()),
            key="avatar_category_filter"
        )
        
        # Gender filter
        avatar_gender = st.selectbox(
            "Gender",
            ["All", "Male", "Female"],
            key="avatar_gender_filter"
        )
        
        # Get filtered avatars
        if avatar_category == "All":
            avatars = get_all_avatars()
        else:
            avatars = AVATAR_CATEGORIES[avatar_category]
        
        if avatar_gender != "All":
            avatars = [a for a in avatars if a.gender == avatar_gender]
        
        # Display avatar grid (4 per row)
        st.markdown("**Available Avatars:**")
        selected_avatar_id = st.session_state.get("selected_avatar", avatars[0].id if avatars else None)
        
        # Create grid
        cols_per_row = 2
        for i in range(0, len(avatars), cols_per_row):
            row_avatars = avatars[i:i+cols_per_row]
            cols = st.columns(cols_per_row)
            
            for idx, avatar in enumerate(row_avatars):
                with cols[idx]:
                    # Avatar card
                    is_selected = avatar.id == selected_avatar_id
                    
                    if st.button(
                        f"{avatar.name}\n{avatar.occupation}",
                        key=f"avatar_{avatar.id}",
                        use_container_width=True,
                        type="primary" if is_selected else "secondary"
                    ):
                        st.session_state.selected_avatar = avatar.id
                        st.rerun()
                    
                    if is_selected:
                        st.caption(f"✓ Selected: {avatar.description}")
        
        st.caption(f"Showing {len(avatars)} avatars")
    
    # ============ CENTER: PREVIEW ============
    with col_preview:
        st.markdown("### 🎥 Preview")
        
        if selected_avatar_id:
            selected_avatar = next((a for a in get_all_avatars() if a.id == selected_avatar_id), None)
            
            if selected_avatar:
                # Show avatar info
                st.info(f"""
                **{selected_avatar.name}**  
                {selected_avatar.occupation} | {selected_avatar.style}  
                *{selected_avatar.description}*
                """)
                
                # Placeholder for generated video
                if st.session_state.get("generated_video"):
                    st.video(st.session_state.generated_video)
                    st.success("✅ Video generated successfully!")
                    
                    # Download button
                    with open(st.session_state.generated_video, "rb") as f:
                        st.download_button(
                            label="📥 Download Video",
                            data=f.read(),
                            file_name=f"avatar_video_{selected_avatar_id}.mp4",
                            mime="video/mp4",
                            use_container_width=True
                        )
                else:
                    st.info("Preview will appear here after generation")
        else:
            st.warning("Select an avatar to continue")
    
    # ============ RIGHT: CONTROLS ============
    with col_controls:
        st.markdown("### ⚙️ Configuration")
        
        # Script input
        script = st.text_area(
            "Script",
            placeholder="Enter your script here...\n\nExample: Hello, welcome to our professional video presentation. Today I'll guide you through our latest product features.",
            height=150,
            help="Write the text that your avatar will speak"
        )
        
        # Voice selection
        st.markdown("**Voice Settings**")
        
        voice_category = st.selectbox(
            "Voice Category",
            list(VOICE_CATEGORIES.keys()),
            key="voice_category"
        )
        
        voices_in_category = VOICE_CATEGORIES[voice_category]
        voice_names = [f"{v.name} ({v.style})" for v in voices_in_category]
        
        selected_voice_idx = st.selectbox(
            "Select Voice",
            range(len(voices_in_category)),
            format_func=lambda x: voice_names[x],
            key="selected_voice_idx"
        )
        
        selected_voice = voices_in_category[selected_voice_idx]
        
        # Voice preview
        if st.button("🔊 Preview Voice", use_container_width=True):
            with st.spinner("Generating preview..."):
                try:
                    preview_path = generate_voice_preview(selected_voice.id)
                    st.audio(preview_path)
                except Exception as e:
                    st.error(f"Preview error: {e}")
        
        # Background/Studio selection
        st.markdown("**Background**")
        st.caption("Basic backgrounds - Premium studio backgrounds coming soon")
        
        # Simple background selection (not using premium compositor)
        background_color = st.selectbox(
            "Background Color",
            ["Neutral Gray", "Warm Beige", "Cool Blue", "Professional Navy"],
            key="bg_color"
        )
        
        # Generate button
        st.markdown("---")
        
        can_generate = script and selected_avatar_id and selected_voice
        
        if st.button(
            "🎬 GENERATE VIDEO",
            disabled=not can_generate,
            use_container_width=True,
            type="primary"
        ):
            if not can_generate:
                st.error("Please complete all fields")
            else:
                with st.spinner("🎥 Creating professional video..."):
                    try:
                        # Initialize studio
                        studio = FreeTalkingAvatarStudio()
                        
                        # Generate talking video (basic mode without premium compositor)
                        result = studio.generate_talking_video(
                            script=script,
                            avatar_key=selected_avatar_id,
                            voice_key=selected_voice.id,
                            presenter_key=None,  # Don't use premium presenter
                            studio_key=None  # Don't use premium studio
                        )
                        
                        if result["success"]:
                            st.session_state.generated_video = result["video_path"]
                            st.success(f"✅ Video created! Provider: {result['provider']}")
                            st.rerun()
                        else:
                            st.error(f"❌ Generation failed: {result.get('error', 'Unknown error')}")
                            
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
        
        if not can_generate:
            st.caption("⚠️ Complete script and selections to generate")

if __name__ == "__main__":
    render_heygen_studio()
