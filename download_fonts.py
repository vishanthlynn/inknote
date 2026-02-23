import os
import requests
import shutil

FONTS_DIR = "backend/assets/fonts"
os.makedirs(FONTS_DIR, exist_ok=True)

# Using raw.githubusercontent.com which is more reliable for raw files
FONTS = {
    "Caveat-Regular.ttf": "https://raw.githubusercontent.com/google/fonts/main/ofl/caveat/Caveat-Regular.ttf",
    "Caveat-Bold.ttf": "https://raw.githubusercontent.com/google/fonts/main/ofl/caveat/Caveat-Bold.ttf",
    "PatrickHand-Regular.ttf": "https://raw.githubusercontent.com/google/fonts/main/ofl/patrickhand/PatrickHand-Regular.ttf",
    "Kalam-Regular.ttf": "https://raw.githubusercontent.com/google/fonts/main/ofl/kalam/Kalam-Regular.ttf",
    "IndieFlower-Regular.ttf": "https://raw.githubusercontent.com/google/fonts/main/ofl/indieflower/IndieFlower-Regular.ttf",
    "ShadowsIntoLight-Regular.ttf": "https://raw.githubusercontent.com/google/fonts/main/ofl/shadowsintolight/ShadowsIntoLight-Regular.ttf",
    "HomemadeApple-Regular.ttf": "https://raw.githubusercontent.com/google/fonts/main/ofl/homemadeapple/HomemadeApple-Regular.ttf",
    "Handlee-Regular.ttf": "https://raw.githubusercontent.com/google/fonts/main/ofl/handlee/Handlee-Regular.ttf",
    "GloriaHallelujah-Regular.ttf": "https://raw.githubusercontent.com/google/fonts/main/ofl/gloriahallelujah/GloriaHallelujah-Regular.ttf",
}

SYSTEM_FONTS = {
    "Noteworthy-Light.ttf": "/System/Library/Fonts/Supplemental/Noteworthy.ttc", # It's a collection, might need index
    "MarkerFelt.ttc": "/System/Library/Fonts/Supplemental/Marker Felt.ttc"
}

def download_fonts():
    print(f"Downloading fonts to {FONTS_DIR}...")
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36'
    }
    
    for filename, url in FONTS.items():
        path = os.path.join(FONTS_DIR, filename)
        if os.path.exists(path) and os.path.getsize(path) > 1000:
            print(f"  - {filename} already exists.")
            continue
        
        print(f"  - Downloading {filename}...")
        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                with open(path, "wb") as f:
                    f.write(response.content)
                print("    Success!")
            else:
                print(f"    Failed with status {response.status_code}")
        except Exception as e:
            print(f"    Failed: {e}")

    # Fallback: Copy system fonts if available
    print("\nChecking for system fonts...")
    for target_name, src_path in SYSTEM_FONTS.items():
        dst_path = os.path.join(FONTS_DIR, target_name)
        if os.path.exists(src_path) and not os.path.exists(dst_path):
             print(f"  - Copying system font {src_path}...")
             try:
                 shutil.copy(src_path, dst_path)
                 print("    Success!")
             except Exception as e:
                 print(f"    Failed to copy system font: {e}")

if __name__ == "__main__":
    download_fonts()
