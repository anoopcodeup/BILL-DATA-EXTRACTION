from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, HttpUrl
from typing import Optional
import traceback

from .pipeline.core import ExtractionPipeline
from .validation.models import APIResponse, ExtractedData, TokenUsage

app = FastAPI(
    title="Bill Extraction API",
    description="Intelligent Bill Line-Item Extraction Pipeline",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class BillRequest(BaseModel):
    document: str  # URL to the document

@app.get("/")
async def root():
    return {
        "message": "Bill Extraction API",
        "endpoints": {
            "POST /extract-bill-data": "Extract line items from a bill"
        }
    }

@app.post("/extract-bill-data", response_model=APIResponse)
async def extract_bill_data(request: BillRequest):
    """
    Extract line items and totals from a bill document.
    
    Args:
        request: BillRequest with document URL
        
    Returns:
        APIResponse with extracted data and token usage
    """
    try:
        # Initialize pipeline
        pipeline = ExtractionPipeline()
        
        # Process the document
        result = pipeline.process_url(request.document)
        
        # Check for errors
        if "error" in result:
            return APIResponse(
                is_success=False,
                token_usage=result.get("token_usage", TokenUsage()),
                error=result["error"]
            )
        
        # Extract invoice and token usage
        invoice = result["invoice"]
        token_usage = result["token_usage"]
        
        # Build response
        extracted_data = ExtractedData(
            pagewise_line_items=invoice.pages,
            total_item_count=len(invoice.all_items)
        )
        
        return APIResponse(
            is_success=True,
            token_usage=token_usage,
            data=extracted_data
        )
        
    except Exception as e:
        print(f"API Error: {e}")
        traceback.print_exc()
        return APIResponse(
            is_success=False,
            token_usage=TokenUsage(),
            error=str(e)
        )

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
