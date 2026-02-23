from PIL import Image, ImageDraw, ImageOps
import random
import numpy as np
from typing import List, Tuple, Union, Optional

class StrokeRenderer:
    def __init__(self, width: int = 800, height: int = 1100, background_type: str = "line"):
        self.width = width
        self.height = height
        self.background_type = background_type
        # Load or create background
        self.background = self._create_background()

    def _create_background(self) -> Image.Image:
        img = Image.new("RGB", (self.width, self.height), "white")
        draw = ImageDraw.Draw(img)
        
        if self.background_type == "line":
            line_spacing = 30
            margin_left = 60
            
            # Vertical margin line
            draw.line([(margin_left, 0), (margin_left, self.height)], fill=(255, 100, 100), width=1)
            
            # Horizontal lines
            for y in range(80, self.height, line_spacing):
                draw.line([(0, y), (self.width, y)], fill=(200, 200, 255), width=1)
                
        elif self.background_type == "dotted":
            spacing = 30
            for y in range(0, self.height, spacing):
                for x in range(0, self.width, spacing):
                    if x % spacing == 0 and y % spacing == 0:
                        draw.ellipse((x-1, y-1, x+1, y+1), fill=(200, 200, 200))
        
        elif self.background_type == "blank":
            pass # Just white
                    
        return img

    def render_to_image(self, all_lines_strokes: List[Tuple[List[List[Tuple[float, float]]], int]]) -> Image.Image:
        """
        Renders multiple lines of strokes and returns the PIL image.
        """
        img = self.background.copy()
        draw = ImageDraw.Draw(img)
        
        margin_left = 60 + 10 # Start after margin
        
        for strokes, y_offset in all_lines_strokes:
            self._draw_line_strokes(draw, strokes, start_x=margin_left, start_y=y_offset)
            
        return img

    def render_strokes(self, all_lines_strokes: List[Tuple[List[List[Tuple[float, float]]], int]], output_path: str) -> str:
        """
        Renders multiple lines of strokes onto the page and saves to file.
        """
        img = self.render_to_image(all_lines_strokes)
        img.save(output_path)
        return output_path

    def _draw_line_strokes(self, draw: ImageDraw.ImageDraw, strokes: List[List[Tuple[float, float]]], start_x: float, start_y: float) -> None:
        """
        Draws a single line of text (set of strokes).
        """
        if not strokes: return

        all_x = [pt[0] for stroke in strokes for pt in stroke]
        all_y = [pt[1] for stroke in strokes for pt in stroke]
        
        if not all_x: return

        min_x = min(all_x)
        min_y = min(all_y)
        max_y = max(all_y)
        
        stroke_height = max_y - min_y
        target_height = 40 # Slightly larger than line spacing to allow ascenders/descenders
        
        # Dynamic scaling
        if stroke_height > 0:
            scale = min(target_height / stroke_height, 1.5) # Cap max scale to avoid tiny text blowing up
        else:
            scale = 0.5
        
        for stroke in strokes:
            points = []
            for x, y in stroke:
                # Apply scaling and offset
                px = (x - min_x) * scale + start_x
                py = (y - min_y) * scale + start_y
                points.append((px, py))
            
            if len(points) > 2:
                # Apply smoothing
                points = self._smooth_points(points)
            
            if len(points) > 1:
                draw.line(points, fill="black", width=2, joint="curve")

    def _smooth_points(self, points: List[Tuple[float, float]], iterations: int = 1) -> List[Tuple[float, float]]:
        """
        Applies Chaikin's algorithm to smooth the stroke.
        """
        if len(points) < 3: return points
        
        for _ in range(iterations):
            new_points = [points[0]]
            for i in range(len(points) - 1):
                p0 = points[i]
                p1 = points[i+1]
                
                # Q = 0.75 P0 + 0.25 P1
                Qx = 0.75 * p0[0] + 0.25 * p1[0]
                Qy = 0.75 * p0[1] + 0.25 * p1[1]
                
                # R = 0.25 P0 + 0.75 P1
                Rx = 0.25 * p0[0] + 0.75 * p1[0]
                Ry = 0.25 * p0[1] + 0.75 * p1[1]
                
                new_points.append((Qx, Qy))
                new_points.append((Rx, Ry))
            
            new_points.append(points[-1])
            points = new_points
            
        return points
