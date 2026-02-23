import sys
import os
import torch
import numpy as np

# Add repo to sys.path so we can import modules from it
REPO_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "repo"))
if REPO_PATH not in sys.path:
    sys.path.append(REPO_PATH)

from handwriting_synthesis.sampling import HandwritingSynthesizer
from handwriting_synthesis import utils

class HandwritingModel:
    def __init__(self, checkpoint_path=None):
        self.device = torch.device("cpu")
        if checkpoint_path is None:
             # Default to checkpoint 56 if available, otherwise find latest
             checkpoint_path = os.path.join(REPO_PATH, "checkpoints/Epoch_56")
             if not os.path.exists(checkpoint_path):
                 # Fallback to listing checkpoints
                 checkpoints_dir = os.path.join(REPO_PATH, "checkpoints")
                 if os.path.exists(checkpoints_dir):
                     subdirs = [os.path.join(checkpoints_dir, d) for d in os.listdir(checkpoints_dir) if d.startswith("Epoch")]
                     if subdirs:
                         checkpoint_path = sorted(subdirs)[-1]
        
        print(f"Loading model from {checkpoint_path}")
        self.synthesizer = HandwritingSynthesizer.load(checkpoint_path, self.device, bias=1.0)
    
    def generate_strokes(self, text, bias=1.0):
        """
        Generates handwriting strokes for a given text.
        
        Args:
            text (str): The text to write.
            bias (float): Controls neatness. Higher = neater, Lower = messier.
            
        Returns:
            list: A list of strokes, where each stroke is a list of (x, y) tuples.
        """
        # Update bias dynamically
        self.synthesizer.model.mixture.bias = bias
        
        # Prepare context with sentinel
        sentinel = ' ' 
        full_text = text + sentinel
        c = self.synthesizer._encode_text(full_text)
        
        # Estimate steps needed: ~25 steps per character is a heuristic
        # Ensure a minimum number of steps
        steps = max(len(text) * 30, 400)
        
        # Sample from the model
        # stochastic=True adds variation
        sampled_handwriting = self.synthesizer.model.sample_means(context=c, steps=steps, stochastic=True)
        # Convert to numpy for manual processing
        seq = sampled_handwriting.cpu().numpy()
        
        # Explicit reconstruction loop (User's logic)
        strokes = []
        current_stroke = []
        x, y = 0.0, 0.0
        scale = 8.0 # User recommended 6-12. Adjusted for model output.
        
        for point in seq:
            dx, dy, eos_flag = point
            
            # Clamp deltas to prevent scribbles
            dx = max(min(dx, 5.0), -5.0)
            dy = max(min(dy, 5.0), -5.0)
            
            # Accumulate (Deltas -> Absolute)
            x += dx * scale
            y += dy * scale
            
            current_stroke.append((x, y))
            
            # EOS flag (stochastic sampling already handled in models.py)
            if eos_flag > 0.5:
                if len(current_stroke) > 1:
                    strokes.append(current_stroke)
                current_stroke = []
                
        if len(current_stroke) > 1:
            strokes.append(current_stroke)
            
        return strokes
