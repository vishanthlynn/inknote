import sys
import os
from PIL import Image

# Add backend to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "backend")))

from renderer.font_renderer import FontRenderer
from renderer.stroke_renderer import StrokeRenderer

def test_lil_changes():
    print("Testing FontRenderer new features...")
    fr = FontRenderer()
    
    # Test new colors
    text = "Testing green and pink colors."
    fr.render_text(text, "test_green.png", color_override="green")
    fr.render_text(text, "test_pink.png", color_override="pink")
    print("  - Saved test_green.png and test_pink.png")
    
    # Test render_to_image
    img = fr.render_to_image("Testing render_to_image function.")
    if isinstance(img, Image.Image):
        print("  - render_to_image returned a PIL Image.")
        img.save("test_render_to_image.png")
    else:
        print("  - Error: render_to_image did NOT return a PIL Image.")

    print("\nTesting StrokeRenderer new features...")
    sr = StrokeRenderer()
    
    # Mock strokes
    mock_strokes = [
        [[(10, 10), (20, 20), (30, 20), (40, 10)]], # A V-shape
        [[(10, 30), (40, 30)]] # A horizontal line
    ]
    lines = [(mock_strokes[0], 100), (mock_strokes[1], 150)]
    
    img_sr = sr.render_to_image(lines)
    if isinstance(img_sr, Image.Image):
        print("  - render_to_image (StrokeRenderer) returned a PIL Image.")
        img_sr.save("test_stroke_image.png")
    else:
        print("  - Error: render_to_image (StrokeRenderer) did NOT return a PIL Image.")

if __name__ == "__main__":
    test_lil_changes()
