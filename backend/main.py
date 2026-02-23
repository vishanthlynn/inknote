from fastapi import FastAPI, UploadFile, File, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import os
import uuid
import shutil
from pathlib import Path

# Import our modules
import sys
# Add backend directory to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from pdf_tools.extractor import extract_text, split_text_into_chunks
# from handwriting_model.wrapper import HandwritingModel # Removed
# from renderer.stroke_renderer import StrokeRenderer # Removed
from pdf_tools.builder import create_pdf_from_images

app = FastAPI(title="InkNotes API")

# CORS setup for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Directories
UPLOAD_DIR = "uploads"
OUTPUT_DIR = "outputs"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Global model instance - REMOVED for Font Renderer
# model = None
# def get_model(): ...

# Job status store (in-memory for MVP)
jobs = {}

@app.get("/")
async def root():
    return {"message": "InkNotes API is running"}

from pydantic import BaseModel
from fastapi.responses import Response

class GenerateRequest(BaseModel):
    text: str
    font_style: str = "default"
    ink_color: str = "blue"
    font_size: int = 28
    line_spacing: int = 40
    paper_type: str = "blank"

@app.post("/generate-preview")
async def generate_preview(req: GenerateRequest):
    from renderer.font_renderer import FontRenderer
    import io
    
    # Initialize renderer with custom params
    renderer = FontRenderer(
        background_type=req.paper_type,
        font_size=req.font_size,
        line_spacing=req.line_spacing,
        ink_color=req.ink_color
    )
    
    # Render to temp file (renderer currently saves to file)
    # Optimization: Refactor renderer to return BytesIO, but for now use temp
    tmp_path = f"{OUTPUT_DIR}/preview_{uuid.uuid4()}.png"
    renderer.render_text(req.text, tmp_path, style=req.font_style)
    
    with open(tmp_path, "rb") as f:
        img_bytes = f.read()
    
    # Cleanup
    os.remove(tmp_path)
    
    return Response(content=img_bytes, media_type="image/png")

@app.post("/upload")
async def upload_pdf(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    style: str = "default",
    color: str = "blue",
    paper: str = "blank",
    size: int = 28
):
    job_id = str(uuid.uuid4())
    file_location = f"{UPLOAD_DIR}/{job_id}.pdf"
    
    with open(file_location, "wb+") as file_object:
        shutil.copyfileobj(file.file, file_object)
    
    jobs[job_id] = {"status": "queued", "progress": 0}
    
    background_tasks.add_task(process_pdf_task, job_id, file_location, style, color, paper, size)
    
    return {"job_id": job_id, "status": "queued"}

def process_pdf_task(job_id: str, file_path: str, style: str, color: str, paper: str, size: int):
    from renderer.font_renderer import FontRenderer
    
    try:
        jobs[job_id] = {"status": "processing", "progress": 10}
        
        # 1. Extract Text
        print(f"Job {job_id}: Extracting text...")
        text = extract_text(file_path)
        if not text:
            jobs[job_id] = {"status": "failed", "error": "Could not extract text from PDF"}
            return
        
        jobs[job_id]["progress"] = 30
        
        jobs[job_id]["progress"] = 30
        
        # 2. Split into pages (Smart AI Processing)
        # Use OpenAI to format text into lines, then chunk into pages
        from ai.processor import preprocess_text
        
        print(f"Job {job_id}: AI Preprocessing...")
        # Get list of clean lines
        lines = preprocess_text(text)
        
        # Group lines into pages (approx 25 lines per page)
        lines_per_page = 25
        page_texts = []
        current_page = []
        
        for line in lines:
            current_page.append(line)
            if len(current_page) >= lines_per_page:
                page_texts.append("\n".join(current_page))
                current_page = []
        
        if current_page:
            page_texts.append("\n".join(current_page))
            
        chunks = page_texts if page_texts else [" "]
        
        # 3. Render Pages
        print(f"Job {job_id}: Rendering pages...")
        # Use user params
        renderer = FontRenderer(
            background_type=paper,
            font_size=size,
            line_spacing=int(size * 1.5), # Auto-calc spacing
            ink_color=color
        )
        
        page_images = []
        total_chunks = len(chunks)
        
        for i, chunk in enumerate(chunks):
            page_output_path = f"{OUTPUT_DIR}/{job_id}_page_{i}.png"
            
            renderer.render_text(chunk, page_output_path, style=style, color_override=color)
            page_images.append(page_output_path)
            
            # Update progress
            jobs[job_id]["progress"] = 30 + int(60 * (i+1) / total_chunks)

        # 4. Create PDF
        print(f"Job {job_id}: Creating PDF...")
        final_pdf_path = f"{OUTPUT_DIR}/{job_id}.pdf"
        create_pdf_from_images(page_images, final_pdf_path)
        
        jobs[job_id] = {"status": "completed", "progress": 100, "result_url": f"/download/{job_id}"}
        
    except Exception as e:
        print(f"Job {job_id} failed: {e}")
        import traceback
        traceback.print_exc()
        jobs[job_id] = {"status": "failed", "error": str(e)}
@app.get("/status/{job_id}")
async def get_status(job_id: str):
    if job_id not in jobs:
        return {"error": "Job not found"}
    return jobs[job_id]

@app.get("/download/{job_id}")
async def download_pdf(job_id: str):
    file_path = f"{OUTPUT_DIR}/{job_id}.pdf"
    if os.path.exists(file_path):
        return FileResponse(file_path, media_type='application/pdf', filename="InkNotes_Export.pdf")
    return {"error": "File not found"}

if __name__ == "__main__":
    import uvicorn
    # Reload=True for dev
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True)
