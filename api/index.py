import sys
import os
import traceback
from pathlib import Path
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel

# Ensure we can import from the root directory
current_dir = Path(__file__).parent
root_dir = current_dir.parent
sys.path.append(str(root_dir))
sys.path.append(str(current_dir))

app = FastAPI()

class AnalyzeRequest(BaseModel):
    text: str
    top_n: int = 20
    min_length: int = 3
    case_sensitive: bool = False
    exclude_stopwords: bool = True

@app.post("/api/analyze")
@app.post("/analyze")
async def analyze_text(request: AnalyzeRequest):
    if not request.text.strip():
        raise HTTPException(status_code=400, detail="Input text is empty.")
    
    try:
        from word_frequency_analyzer import analyze
        results = analyze(
            text=request.text,
            top_n=request.top_n,
            case_sensitive=request.case_sensitive,
            exclude_stopwords=request.exclude_stopwords,
            min_length=request.min_length,
            quiet=True
        )
        
        # Convert list of tuples to list of dicts for the React frontend
        formatted_top_words = [{"word": w, "count": c} for w, c in results["top_words"]]
        results["top_words"] = formatted_top_words
        
        return results
    except ImportError as ie:
        print(f"ImportError: {ie}")
        raise HTTPException(status_code=500, detail="Backend script not found on server.")
    except Exception as e:
        print(f"Error during analysis: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")

# Add a healthcheck endpoint
@app.get("/api/health")
@app.get("/health")
def health_check():
    return {"status": "ok"}

# Catch-all exception handler to return JSON instead of crashing silently
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": f"Unhandled error: {str(exc)}"},
    )
