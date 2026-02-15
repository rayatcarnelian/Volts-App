
try:
    import moviepy
    print(f"MoviePy Version: {moviepy.__version__}")
    
    # Try importing common symbols
    attrs = ["ImageClip", "ColorClip", "AudioFileClip", "CompositeVideoClip", "concatenate_videoclips", "VideoFileClip", "TextClip"]
    
    for attr in attrs:
        if hasattr(moviepy, attr):
            print(f"{attr} found in moviepy")
        else:
            print(f"{attr} NOT found in moviepy")
            
            # Try submodules if not found
            # This is a guess-and-check for v2 structure
            
except Exception as e:
    print(f"Error: {e}")
