import os
import streamlit as st

class StudioGallery:
    """
    Manages visual assets (images) for The Studio.
    """
    def __init__(self, asset_dir="assets/concepts"):
        self.asset_dir = asset_dir
        if not os.path.exists(self.asset_dir):
            os.makedirs(self.asset_dir)

    def save_uploads(self, uploaded_files):
        """Saves a list of uploaded files to the asset directory."""
        count = 0
        for uploaded_ref in uploaded_files:
            try:
                save_path = os.path.join(self.asset_dir, uploaded_ref.name)
                with open(save_path, "wb") as f:
                    f.write(uploaded_ref.getbuffer())
                count += 1
            except Exception as e:
                st.error(f"Failed to save {uploaded_ref.name}: {e}")
        return count

    def get_images(self):
        """Returns a list of image filenames in the gallery."""
        if not os.path.exists(self.asset_dir):
            return []
        return [f for f in os.listdir(self.asset_dir) if f.lower().endswith(('jpg', 'png', 'jpeg'))]

    def render_grid(self):
        """Displays the gallery in a grid."""
        files = self.get_images()
        if files:
            cols = st.columns(3)
            for idx, file in enumerate(files):
                with cols[idx % 3]:
                    st.image(os.path.join(self.asset_dir, file), caption=file, use_container_width=True)
        else:
            st.info("Gallery empty. Generate or Upload images.")
