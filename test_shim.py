
import sys
import moviepy

# Shim
sys.modules["moviepy.editor"] = moviepy

# Test import
try:
    from moviepy.editor import VideoFileClip
    print("Shim successful: Imported VideoFileClip from moviepy.editor")
except ImportError as e:
    print(f"Shim failed: {e}")
