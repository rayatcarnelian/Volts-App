import sys
try:
    import moviepy
    print(f"MoviePy Version: {moviepy.__version__}")
    
    print("Checking moviepy roots:")
    print(dir(moviepy))
    
    try:
        from moviepy import concatenate_videoclips
        print("SUCCESS: from moviepy import concatenate_videoclips")
    except ImportError:
        print("FAIL: from moviepy import concatenate_videoclips")

    import moviepy.video.compositing
    print("\nChecking moviepy.video.compositing:")
    print(dir(moviepy.video.compositing))
    
    try:
        from moviepy.video.compositing import concatenate_videoclips
        print("SUCCESS: from moviepy.video.compositing import concatenate_videoclips")
    except ImportError:
        print("FAIL: from moviepy.video.compositing import concatenate_videoclips")

except ImportError as e:
    print(f"ImportError: {e}")
except Exception as e:
    print(f"Error: {e}")
