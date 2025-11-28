ROW_RECONSTRUCTION_PROMPT = """You are an expert at extracting structured data from bill/invoice text.

Extract ALL line items from this bill text. Each line item should have:
- item_name: The product/service description
- item_rate: Price per unit (use 0.0 if not found)
- item_quantity: Quantity (use 1.0 if not found)
- item_amount: Total amount for this item (REQUIRED - this is the most important field)

IMPORTANT RULES:
1. Extract EVERY line item - don't skip any
2. item_amount is REQUIRED and must be a number
3. If you see subtotals or totals, DO NOT include them as line items
4. Return ONLY valid JSON array, no explanations
5. If a field is missing, use reasonable defaults (0.0 for rate/quantity, but item_amount must be present)

Bill Text:
{text_segment}

Return a JSON array like this:
[
  {{"item_name": "Product 1", "item_rate": 10.0, "item_quantity": 2.0, "item_amount": 20.0}},
  {{"item_name": "Product 2", "item_rate": 15.0, "item_quantity": 1.0, "item_amount": 15.0}}
]

JSON array:"""

AMBIGUITY_RESOLUTION_PROMPT = """You are an expert at correcting bill line item data.

Row Data:
{row_data}

Context:
{context}

Please correct any errors in the row data and return a valid JSON object with these fields:
- item_name (string)
- item_rate (float)
- item_quantity (float)  
- item_amount (float)

Return ONLY the JSON object, no explanations.

JSON object:"""
