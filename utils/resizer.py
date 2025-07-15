import os
from PIL import Image

# Directories
folders = ['C:\\Users\\dell\\MainPlay\\tails\\sit', 'C:\\Users\\dell\\MainPlay\\tails\\sit']
target_height = 204

def resize_image_keep_aspect(img_path):
    with Image.open(img_path) as img:
        w, h = img.size
        new_height = target_height
        new_width = int(w * (new_height / h))
        resized_img = img.resize((new_width, new_height), Image.LANCZOS)
        resized_img.save(img_path)

def process_folder(folder):
    for filename in os.listdir(folder):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
            full_path = os.path.join(folder, filename)
            resize_image_keep_aspect(full_path)
            print(f"Resized: {full_path}")

if __name__ == "__main__":
    for folder in folders:
        process_folder(folder)
    print("Done resizing all images.")
