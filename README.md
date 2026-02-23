# InkNotes

InkNotes is a web application that converts PDF documents into handwritten-looking notes using a deep learning model (Graves LSTM).

## Features
- **PDF Upload**: Drag and drop PDF files.
- **Handwriting Synthesis**: Generates realistic handwriting strokes.
- **Customizable Styles**: Choose between "Neat", "Casual", and "Messy" styles.
- **Improved Rendering**: New `render_to_image` methods in `font_renderer.py` and `stroke_renderer.py` allow for easier integration, and new colors (green, pink) are supported.
- **Notebook Rendering**: Renders text onto lined or dotted notebook paper.
- **PDF Export**: Download the result as a multi-page PDF.

## Tech Stack
- **Frontend**: Next.js 14, TailwindCSS, shadcn/ui
- **Backend**: FastAPI, PyTorch, Pillow, ReportLab
- **Tools**: pdfplumber, pytesseract, pdf2image

## Prerequisites
- **Python 3.9+**
- **Node.js 18+**
- **System Dependencies**:
    - `poppler` (for PDF processing)
    - `tesseract` (for OCR)

### Installing System Dependencies (macOS)
```bash
brew install poppler tesseract
```

## Local Setup

### Backend
1. Navigate to the backend directory:
   ```bash
   cd InkNotes/backend
   ```
2. Create and activate a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
3. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```
   *Note: Ensure `torch` is installed correctly for your system.*

4. Run the server:
   ```bash
   python3 main.py
   ```
   The API will be available at `http://localhost:8001`.

### Frontend
1. Navigate to the frontend directory:
   ```bash
   cd InkNotes/frontend
   ```
2. Install Node dependencies:
   ```bash
   npm install
   ```
3. Run the development server:
   ```bash
   npm run dev
   ```
   The app will be available at `http://localhost:3000`.

## Deployment

### Backend (Render/Railway)
- Use the `InkNotes/backend` directory as the root.
- content of `Procfile` (if using Heroku/Railway):
  ```
  web: uvicorn main:app --host 0.0.0.0 --port $PORT
  ```
- **Environment Variables**:
  - `PYTHON_VERSION`: 3.9+
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `uvicorn main:app --host 0.0.0.0 --port 8000`

### Frontend (Vercel)
- Import the repository to Vercel.
- Set `Root Directory` to `InkNotes/frontend`.
- Vercel will automatically detect Next.js.
- **Build Command**: `npm run build`
- **Output Directory**: `.next`

## Troubleshooting
- **"Could not extract text from PDF"**: Ensure `poppler` and `tesseract` are installed on the server.
- **Model loading error**: Verify `handwriting_model/repo/checkpoints` exists and contains the model file.
