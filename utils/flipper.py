import os
from PIL import Image 

base_dir = "C:\\users\\dell\\pictures\\"
input_folder = os.path.join(base_dir, "sit")
output_folder = os.path.join(base_dir, "sit")
os.makedirs(output_folder, exist_ok=True)

for i in range(1, 11):
    input_path = os.path.join(input_folder, f"tailsSit{i}.png")
    output_path = os.path.join(output_folder, f"tailsSitB{i}.png")

    if not os.path.exists(input_path):
        print(f"Missing: {input_path}")
        continue

    img = Image.open(input_path).convert("RGBA")
    flipped = img.transpose(Image.FLIP_LEFT_RIGHT)
    flipped.save(output_path)

print("All images flipped and saved to:", output_folder)
