from PIL import Image, ImageDraw, ImageFont, ImageOps
import random
import os
from typing import Dict, Tuple, Optional, Union

class FontRenderer:
    def __init__(self, width: int = 800, height: int = 1100, font_dir: str = "backend/assets/fonts", 
                 background_type: str = "blank", 
                 font_size: int = 28, 
                 line_spacing: int = 40,
                 margin_left: int = 50,
                 margin_top: int = 50,
                 ink_color: str = "blue"):
        self.width = width
        self.height = height
        self.font_dir = font_dir
        self.background_type = background_type
        self.font_size = font_size
        self.line_spacing = line_spacing
        self.margin_left = margin_left
        self.margin_top = margin_top
        self.ink_color_name = ink_color
        
        self.background = self._create_background()
        
        # Load fonts
        self.fonts: Dict[str, ImageFont.FreeTypeFont] = {}
        self._load_fonts()

    def _load_fonts(self) -> None:
        try:
            # Helper to find first available font
            def get_font_path(*names: str) -> Optional[str]:
                for name in names:
                    path = os.path.join(self.font_dir, name)
                    if os.path.exists(path): return path
                return None

            # 1. Try downloaded fonts
            default_path = get_font_path("PatrickHand-Regular.ttf", "Caveat-Regular.ttf")
            bold_path = get_font_path("Kalam-Bold.ttf", "Caveat-Bold.ttf")
            messy_path = get_font_path("IndieFlower-Regular.ttf", "Kalam-Regular.ttf") 
            cursive_path = get_font_path("HomemadeApple-Regular.ttf", "Sacramento-Regular.ttf")
            handlee_path = get_font_path("Handlee-Regular.ttf", "GloriaHallelujah-Regular.ttf")
            
            # 2. Try System fonts
            if not default_path:
                sys_path = get_font_path("Noteworthy-Light.ttf", "MarkerFelt.ttc")
                if sys_path: default_path = sys_path
                
            if not default_path: raise OSError("No fonts found")

            self.fonts["default"] = ImageFont.truetype(default_path, size=self.font_size)
            self.fonts["heading"] = ImageFont.truetype(bold_path or default_path, size=self.font_size + 10)
            self.fonts["messy"] = ImageFont.truetype(messy_path or default_path, size=self.font_size)
            self.fonts["cursive"] = ImageFont.truetype(cursive_path or default_path, size=self.font_size)
            self.fonts["handlee"] = ImageFont.truetype(handlee_path or default_path, size=self.font_size)
            
            print(f"Loaded font: {default_path}")

        except Exception as e:
            print(f"Warning: Fonts not found ({e}). Using default.")
            self.fonts["default"] = ImageFont.load_default() 
            self.fonts["heading"] = ImageFont.load_default()
            self.fonts["messy"] = ImageFont.load_default() 
            self.fonts["cursive"] = ImageFont.load_default()
            self.fonts["handlee"] = ImageFont.load_default()

    def _create_background(self) -> Image.Image:
        # White or Dark
        bg_color: Union[str, Tuple[int, int, int]] = "white"
        if self.background_type == "dark":
            bg_color = (30, 30, 30)
            
        img = Image.new("RGBA", (self.width, self.height), bg_color)
        draw = ImageDraw.Draw(img)
        
        if self.background_type == "line":
            draw.line([(self.margin_left + 10, 0), (self.margin_left + 10, self.height)], fill=(255, 100, 100), width=1)
            for y in range(self.margin_top, self.height, self.line_spacing):
                draw.line([(0, y), (self.width, y)], fill=(200, 200, 255), width=1)
                
        elif self.background_type == "grid":
            grid_size = self.line_spacing
            for x in range(0, self.width, grid_size):
                draw.line([(x, 0), (x, self.height)], fill=(230, 230, 230), width=1)
            for y in range(0, self.height, grid_size):
                draw.line([(0, y), (self.width, y)], fill=(230, 230, 230), width=1)
            
        return img

    def render_to_image(self, text: str, style: str = "default", color_override: Optional[str] = None) -> Image.Image:
        """Renders text and returns the PIL Image object."""
        img = self.background.copy()
        
        # Ink resolution
        color_name = color_override or self.ink_color_name
        colors = {
            "blue": (0, 50, 180),
            "black": (20, 20, 20),
            "red": (200, 0, 0),
            "green": (0, 100, 0),
            "pink": (255, 105, 180),
            "white": (230, 230, 230)
        }
        
        if color_name.startswith("#"):
            from PIL import ImageColor
            base_color = ImageColor.getrgb(color_name)
        else:
            base_color = colors.get(color_name, colors["blue"])

        font = self.fonts.get(style, self.fonts["default"])
        
        cursor_y = self.margin_top
        
        for line in text.splitlines():
            # Create a temporary transparent line image to draw words onto
            line_height = int(self.font_size * 2)
            line_width = self.width - (self.margin_left * 2) # content width
            
            line_img = Image.new('RGBA', (line_width, line_height), (255, 255, 255, 0))
            
            # Cursor within the line image
            line_cursor_x = 0
            
            # Word-level randomization
            words = line.split(" ")
            
            for word in words:
                word += " "
                
                # Render word char by char
                for char in word:
                    self._draw_char(line_img, char, line_cursor_x + 10, line_height//2, font, base_color)
                    
                    char_bbox = font.getbbox(char)
                    char_width = char_bbox[2] - char_bbox[0] if char_bbox else 10
                    
                    line_cursor_x += char_width + random.randint(0, 2) # kerning jitter relative
            
            # Line-level Rotation (Slope)
            line_angle = random.uniform(-0.5, 0.5)
            rotated_line = line_img.rotate(line_angle, resample=Image.BICUBIC, expand=1)
            
            # Paste line onto page
            x_drift = random.randint(-2, 5)
            paste_x = self.margin_left + x_drift
            
            # Paste
            img.alpha_composite(rotated_line, dest=(paste_x, cursor_y))
            
            cursor_y += self.line_spacing
            
            if cursor_y > self.height - 50:
                break

        return img

    def render_text(self, text: str, output_path: str, style: str = "default", color_override: Optional[str] = None) -> str:
        """
        Renders text and saves it to the specified output path.
        """
        img = self.render_to_image(text, style, color_override)
        img.save(output_path)
        return output_path

    def _draw_char(self, img: Image.Image, char: str, x: int, y: int, font: ImageFont.FreeTypeFont, base_color: Tuple) -> None:
        char_size = int(self.font_size * 3.5) # Scale temp canvas by font size
        txt_img = Image.new('RGBA', (char_size, char_size), (255, 255, 255, 0))
        d = ImageDraw.Draw(txt_img)
        
        # Draw char
        # Add random opacity variation
        opacity = 255 if len(base_color) == 3 else base_color[3]
        if opacity > 200: opacity = random.randint(220, 255)
        
        fill_color = base_color[:3] + (opacity,)
        
        d.text((char_size//2, char_size//2), char, font=font, fill=fill_color, anchor="mm")
        
        # Rotation
        angle = random.uniform(-1.5, 1.5) 
        rotated_txt = txt_img.rotate(angle, resample=Image.BICUBIC, expand=0)
        
        # Baseline Jitter
        y_offset = random.randint(-1, 2)
        
        paste_x = int(x - char_size//2)
        paste_y = int(y + y_offset - char_size//2 + self.font_size*0.4) 
        
        img.alpha_composite(rotated_txt, dest=(paste_x, paste_y))
