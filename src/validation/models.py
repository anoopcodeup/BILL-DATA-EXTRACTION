from pydantic import BaseModel, Field, validator
from typing import Optional, List, Literal

class TokenUsage(BaseModel):
    total_tokens: int = 0
    input_tokens: int = 0
    output_tokens: int = 0

class LineItem(BaseModel):
    item_name: str = Field(..., description="Exactly as mentioned in the bill")
    item_amount: float = Field(..., description="Net Amount of the item post discounts")
    item_rate: float = Field(..., description="Exactly as mentioned in the bill")
    item_quantity: float = Field(..., description="Exactly as mentioned in the bill")
    
    # Internal fields (excluded from API response if needed, or we map later)
    confidence: Optional[float] = Field(1.0, exclude=True)
    
    @validator('item_rate', 'item_quantity', 'item_amount', pre=True)
    def convert_to_float(cls, v):
        if v is None:
            return 0.0
        if isinstance(v, str):
            try:
                # Remove currency symbols and commas
                clean_v = v.replace(',', '').replace('$', '').replace('₹', '').strip()
                if not clean_v:
                    return 0.0
                return float(clean_v)
            except ValueError:
                return 0.0
        return v

class PageData(BaseModel):
    page_no: str
    page_type: Literal["Bill Detail", "Final Bill", "Pharmacy"] = "Bill Detail"
    bill_items: List[LineItem] = []

class ExtractedData(BaseModel):
    pagewise_line_items: List[PageData]
    total_item_count: int

class APIResponse(BaseModel):
    is_success: bool
    token_usage: TokenUsage
    data: Optional[ExtractedData] = None
    error: Optional[str] = None

# Internal model for Pipeline processing (superset of API models)
class Invoice(BaseModel):
    pages: List[PageData] = []
    subtotal: Optional[float] = 0.0
    tax: Optional[float] = 0.0
    total_amount: Optional[float] = 0.0 # Extracted total
    
    @property
    def all_items(self) -> List[LineItem]:
        items = []
        for page in self.pages:
            items.extend(page.bill_items)
        return items

    @property
    def calculated_total(self) -> float:
        return sum(item.item_amount for item in self.all_items)
