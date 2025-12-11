from PIL import Image
import os

# Paths
source_img_path = r"C:/Users/datel/.gemini/antigravity/brain/cb60a48c-955a-4e10-961c-cf7239282d60/cat_walk_set_v3_1765400567088.png"
target_dir = r"c:/Mini/Study/Vibe Project/Desktop Kitty/assets/sprites/walk"

# Ensure target dir exists
if not os.path.exists(target_dir):
    os.makedirs(target_dir)

# Clean target dir (remove old frames)
for filename in os.listdir(target_dir):
    file_path = os.path.join(target_dir, filename)
    if os.path.isfile(file_path):
        os.unlink(file_path)

# Open image
img = Image.open(source_img_path)
width, height = img.size
print(f"Image Size: {width}x{height}")

# New image prompt requested "single row" explicitly, but generate_image might still do grid.
# Let's verify aspect ratio again.
# "6 frames sequence in a single row" might result in very wide image.
aspect = width / height
print(f"Aspect Ratio: {aspect:.2f}")

if aspect > 4.5:
    rows = 1
    cols = 6
    print("Detected 6x1 layout")
else:
    # Heuristic for grid
    if width > height:
        cols = 3
        rows = 2
        print("Detected 3x2 layout")
    else:
        cols = 2
        rows = 3
        print("Detected 2x3 layout")

frame_width = width // cols
frame_height = height // rows

count = 0
for r in range(rows):
    for c in range(cols):
        if count >= 6:
            break
        
        left = c * frame_width
        top = r * frame_height
        right = left + frame_width
        bottom = top + frame_height
        
        frame = img.crop((left, top, right, bottom))
        
        save_path = os.path.join(target_dir, f"{count}.png")
        frame.save(save_path)
        print(f"Saved {save_path}")
        
        count += 1

print("Done slicing.")
