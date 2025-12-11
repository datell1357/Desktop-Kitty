import os
import shutil
import glob

brain_dir = r"C:/Users/datel/.gemini/antigravity/brain/cb60a48c-955a-4e10-961c-cf7239282d60"
target_dir = r"c:/Mini/Study/Vibe Project/Desktop Kitty/assets/sprites/walk"

if not os.path.exists(target_dir):
    os.makedirs(target_dir)

# Clear target
for f in os.listdir(target_dir):
    os.remove(os.path.join(target_dir, f))

# Find latest frame for each index
for i in range(8):
    pattern = os.path.join(brain_dir, f"walk_8_frame_{i:02d}_*.png")
    files = glob.glob(pattern)
    if not files:
        # Fallback to single digit if needed, or just warn
        pattern_single = os.path.join(brain_dir, f"walk_8_frame_{i}_*.png")
        files = glob.glob(pattern_single)
        
    if not files:
        print(f"Error: No file found for frame {i}")
        continue
    
    # Sort by modification time to get latest
    latest_file = max(files, key=os.path.getmtime)
    
    target_path = os.path.join(target_dir, f"{i}.png")
    shutil.copy2(latest_file, target_path)
    print(f"Deployed {latest_file} -> {target_path}")

print("Deployment complete.")
