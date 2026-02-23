import os
import json
from openai import OpenAI
from typing import List

# Initialize client
# Ensure OPENAI_API_KEY is set in environment
try:
    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
except Exception as e:
    print(f"Warning: OpenAI client init failed: {e}")
    client = None

SYSTEM_PROMPT = """You are a text formatter. Take raw PDF text and output a JSON object with a key "lines" containing a list of clean lines (35–55 chars each).
Keep math equations, bullets, headings, and definitions.
Do not lose any content.
Break long paragraphs into multiple lines.
If there is a heading, make it a separate line.

Output JSON format:
{
  "lines": [
    "Heading Text",
    "Line 1 of content...",
    "Line 2 of content..."
  ]
}
"""

def preprocess_text(text: str) -> List[str]:
    """
    Uses OpenAI to clean text and split it into handwriting-ready lines.
    """
    if not text or not text.strip():
        return []

    if not client or not os.environ.get("OPENAI_API_KEY"):
        print("Warning: No OpenAI API Key found. Using simple fallback.")
        return simple_chunk_text(text)

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo", # Use 3.5-turbo for cost/speed unless user has 4
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"Format this text:\n\n{text[:12000]}"} # Truncate to avoid context limit
            ],
            response_format={ "type": "json_object" },
            temperature=0.3
        )
        
        content = response.choices[0].message.content
        data = json.loads(content)
        
        if "lines" in data:
            return data["lines"]
        else:
            return simple_chunk_text(text)

    except Exception as e:
        print(f"AI Preprocessing failed: {e}")
        return simple_chunk_text(text)

def simple_chunk_text(text: str, chunk_size=50) -> List[str]:
    """Fallback if OpenAI fails or no key"""
    lines = []
    # Basic paragraph splitting
    paragraphs = text.replace('\r', '').split('\n')
    for p in paragraphs:
        if not p.strip():
            continue
        # Split long lines
        while len(p) > chunk_size:
            # Find last space within chunk_size
            split_idx = p[:chunk_size].rfind(' ')
            if split_idx == -1: split_idx = chunk_size
            lines.append(p[:split_idx])
            p = p[split_idx:].strip()
        if p:
            lines.append(p)
    return lines
