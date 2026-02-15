from PIL import Image
import numpy as np

def process_logo(input_path, output_path):
    img = Image.open(input_path).convert("RGBA")
    data = np.array(img)

    # 1. Make White Background Transparent
    # Threshold for "White" (e.g. > 240, 240, 240)
    r, g, b, a = data.T
    white_areas = (r > 240) & (g > 240) & (b > 240)
    data[..., 3][white_areas.T] = 0

    # 2. Convert Black Text to Off-White (#EAEAEA - 234, 234, 234) for Dark Mode
    # Threshold for "Black" (e.g. < 50, 50, 50)
    black_areas = (r < 50) & (g < 50) & (b < 50)
    
    data[..., 0][black_areas.T] = 234 # R
    data[..., 1][black_areas.T] = 234 # G
    data[..., 2][black_areas.T] = 234 # B
    # Alpha remains 255 for text

    # 3. Save
    new_img = Image.fromarray(data)
    new_img.save(output_path)
    print(f"Processed logo saved to {output_path}")

if __name__ == "__main__":
    # Input is the uploaded file path (I'll need to copy it or ref it directly)
    # Since I can't easily guess the full path of the upload in the abstract, I'll assume I copy it first or use the path provided in metadata
    # The metadata path: C:/Users/rayat/.gemini/antigravity/brain/bd19ba53-5a29-490f-b7ce-6eff0c253935/uploaded_image_1768419105770.png
    
    input_p = r"C:/Users/rayat/.gemini/antigravity/brain/bd19ba53-5a29-490f-b7ce-6eff0c253935/uploaded_image_1768419105770.png"
    output_p = r"E:/Leads app/logo_transparent.png"
    process_logo(input_p, output_p)
