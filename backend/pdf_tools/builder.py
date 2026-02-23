from PIL import Image
import os

def create_pdf_from_images(image_paths, output_pdf_path):
    """
    Combines a list of image paths into a single PDF.
    
    Args:
        image_paths (list): List of paths to image files.
        output_pdf_path (str): Path to save the final PDF.
    """
    if not image_paths:
        return
        
    images = []
    first_image = None
    
    for path in image_paths:
        img = Image.open(path)
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        if first_image is None:
            first_image = img
        else:
            images.append(img)
            
    if first_image:
        first_image.save(output_pdf_path, save_all=True, append_images=images)
        print(f"PDF saved to {output_pdf_path}")
