import os
from PIL import Image

def remove_background(image_path, bg_color=(255,255,255), tolerance=10):
    image = Image.open(image_path).convert("RGBA")
    pixels = image.load()

    for y in range(image.height):
        for x in range(image.width):
            r, g, b, a = pixels[x, y]
            if all(abs(c - bc) <= tolerance for c, bc in zip((r, g, b), bg_color)):
                pixels[x, y] = (r, g, b, 0)  # Set transparent

    return image

def process_folder(input_folder, output_folder, bg_color=(255,255,255), tolerance=10):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for filename in os.listdir(input_folder):
        if filename.lower().endswith((".png", ".jpg", ".jpeg")):
            input_path = os.path.join(input_folder, filename)
            output_path = os.path.join(output_folder, os.path.splitext(filename)[0] + ".png")
            try:
                print(f"Processing: {filename}")
                result = remove_background(input_path, bg_color, tolerance)
                result.save(output_path)
            except Exception as e:
                print(f"Failed to process {filename}: {e}")

    print("Batch background removal complete.")

input_folder = "C:/Users/dell/Pictures/tails/sitBg"
output_folder = "C:/Users/dell/Pictures/tails/sit"
bg_color = (250,243,209)
tolerance = 7

process_folder(input_folder, output_folder, bg_color, tolerance)
