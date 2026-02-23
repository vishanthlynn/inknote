import sys
import os

# Add backend to sys.path
sys.path.append(os.path.dirname(__file__))

from handwriting_model.wrapper import HandwritingModel
from renderer.stroke_renderer import StrokeRenderer

def test_generation():
    print("Initializing model...")
    try:
        model = HandwritingModel()
    except Exception as e:
        print(f"Failed to load model: {e}")
        return

    text = "Hello, this is a test of InkNotes!"
    print(f"Generating strokes for: '{text}'")
    
    try:
        strokes = model.generate_strokes(text, bias=0.8)
        print(f"Generated {len(strokes)} strokes.")
    except Exception as e:
        print(f"Failed to generate strokes: {e}")
        return

    print("Initializing renderer...")
    renderer = StrokeRenderer()
    
    # Create a dummy line layout (strokes, y_offset)
    lines = [(strokes, 100)]
    
    output_path = "test_output.png"
    print(f"Rendering to {output_path}...")
    try:
        renderer.render_strokes(lines, output_path)
        print("Success!")
    except Exception as e:
        print(f"Failed to render: {e}")

if __name__ == "__main__":
    test_generation()
