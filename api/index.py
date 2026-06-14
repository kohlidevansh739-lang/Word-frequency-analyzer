import sys
import os
from pathlib import Path

# Add the root directory to sys.path to allow importing word_frequency_analyzer
sys.path.append(str(Path(__file__).parent.parent))

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
try:
    from word_frequency_analyzer import analyze
except ImportError:
    # Fallback if running directly in root or via uvicorn in different dir
    sys.path.append(os.getcwd())
    from word_frequency_analyzer import analyze

app = FastAPI()

class AnalyzeRequest(BaseModel):
    text: str
    top_n: int = 20
    min_length: int = 3
    case_sensitive: bool = False
    exclude_stopwords: bool = True

@app.post("/api/analyze")
async def analyze_text(request: AnalyzeRequest):
    if not request.text.strip():
        raise HTTPException(status_code=400, detail="Input text is empty.")
    
    try:
        results = analyze(
            text=request.text,
            top_n=request.top_n,
            case_sensitive=request.case_sensitive,
            exclude_stopwords=request.exclude_stopwords,
            min_length=request.min_length,
            quiet=True
        )
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
