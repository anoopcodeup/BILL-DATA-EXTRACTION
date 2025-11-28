from typing import List, Dict, Any, Optional
import numpy as np
import os
import re
from ..ocr.tesseract import TesseractOCR
from ..llm.client import LLMClient
from ..validation.models import Invoice, LineItem, PageData, TokenUsage
from ..validation.logic import Validator
from ..utils.input_handler import InputHandler
from ..utils.image_processing import ImagePreprocessor

class ExtractionPipeline:
    def __init__(self):
        self.ocr = TesseractOCR()
        self.llm = LLMClient()
        self.validator = Validator()
        self.input_handler = InputHandler()
        self.preprocessor = ImagePreprocessor()

    def process_url(self, url: str) -> Dict[str, Any]:
        """
        Main entry point for processing a bill from a URL.
        Returns dict with token_usage and invoice data.
        """
        print(f"Downloading from {url}...")
        file_path = None
        try:
            file_path = self.input_handler.download_file(url)
            images = self.input_handler.load_pages(file_path)
            
            pages_data = []
            
            for i, image in enumerate(images):
                page_num = i + 1
                print(f"Processing page {page_num}...")
                
                # Step 1: Preprocess
                processed_image = self.preprocessor.preprocess(image)
                
                # Step 2: OCR + Layout extraction
                ocr_data = self.ocr.extract_data(processed_image)
                raw_text = self.ocr.extract_text(processed_image)
                
                # Step 3: Table & row reconstruction (Fast Path)
                page_items = self._parse_ocr_to_items(ocr_data, page_num)
                
                # Step 4: Ambiguous row → Sonnet refinement (Slow Path)
                if not page_items:
                    print(f"Page {page_num}: No items found via OCR. Using LLM...")
                    llm_data = self.llm.reconstruct_table(raw_text)
                    for d in llm_data:
                        try:
                            page_items.append(LineItem(**d))
                        except Exception as e:
                            print(f"Error creating LineItem: {e}, data: {d}")
                
                # Classify page type
                page_type = self._classify_page_type(raw_text)
                
                pages_data.append(PageData(
                    page_no=str(page_num),
                    page_type=page_type,
                    bill_items=page_items
                ))

            # Construct Invoice
            invoice = Invoice(pages=pages_data)
            
            # Step 6: Deduplication + reconciliation
            all_items = invoice.all_items
            unique_items = self.validator.deduplicate_rows(all_items)
            
            # Rebuild pages with deduplicated items
            # For simplicity, we'll keep the page structure but note this is a simplified approach
            # In production, you'd want to track which page each item came from
            
            # Step 5: Extract totals from the document
            total_amount = self._extract_total(raw_text) if images else 0.0
            invoice.total_amount = total_amount
            
            return {
                "invoice": invoice,
                "token_usage": self.llm.get_usage()
            }
            
        except Exception as e:
            print(f"Pipeline Error: {e}")
            import traceback
            traceback.print_exc()
            return {
                "error": str(e),
                "token_usage": self.llm.get_usage()
            }
        finally:
            # Cleanup temp file
            if file_path and os.path.exists(file_path):
                try:
                    os.remove(file_path)
                except Exception as e:
                    print(f"Error removing temp file: {e}")

    def _parse_ocr_to_items(self, ocr_data: List[Dict[str, Any]], page_num: int) -> List[LineItem]:
        """
        Heuristic parser to extract line items from OCR data.
        This is a basic implementation that looks for patterns.
        """
        items = []
        
        # Group OCR data by vertical position (y-coordinate)
        lines = {}
        for word_data in ocr_data:
            text = word_data['text'].strip()
            if not text or len(text) < 2:
                continue
                
            bbox = word_data['bbox']
            y_pos = bbox[1]  # top position
            
            # Group words on similar y-positions (within 10 pixels)
            found_line = False
            for line_y in lines:
                if abs(line_y - y_pos) < 10:
                    lines[line_y].append(word_data)
                    found_line = True
                    break
            
            if not found_line:
                lines[y_pos] = [word_data]
        
        # Sort lines by y-position
        sorted_lines = sorted(lines.items(), key=lambda x: x[0])
        
        # Try to extract items from each line
        for y_pos, words in sorted_lines:
            # Sort words by x-position
            words.sort(key=lambda w: w['bbox'][0])
            line_text = ' '.join([w['text'] for w in words])
            
            # Look for patterns: item name, quantity, rate, amount
            # This is a simplified heuristic
            item = self._extract_item_from_line(line_text)
            if item:
                items.append(item)
        
        return items

    def _extract_item_from_line(self, line_text: str) -> Optional[LineItem]:
        """
        Extract item details from a single line of text.
        Returns None if no valid item found.
        """
        # Skip header lines
        if any(keyword in line_text.lower() for keyword in ['description', 'item', 'qty', 'rate', 'amount', 'total', 'subtotal']):
            return None
        
        # Look for numbers (potential quantities, rates, amounts)
        numbers = re.findall(r'\d+\.?\d*', line_text)
        
        if len(numbers) < 1:
            return None
        
        # Very basic heuristic: assume last number is amount
        # This is a placeholder - real implementation would be more sophisticated
        try:
            item_amount = float(numbers[-1])
            item_quantity = float(numbers[0]) if len(numbers) > 1 else 1.0
            item_rate = float(numbers[1]) if len(numbers) > 2 else item_amount
            
            # Extract item name (text before numbers)
            item_name = re.sub(r'\d+\.?\d*', '', line_text).strip()
            if not item_name or len(item_name) < 3:
                return None
            
            return LineItem(
                item_name=item_name,
                item_quantity=item_quantity,
                item_rate=item_rate,
                item_amount=item_amount
            )
        except:
            return None

    def _classify_page_type(self, text: str) -> str:
        """
        Classify page type based on content.
        """
        text_lower = text.lower()
        
        if 'pharmacy' in text_lower or 'medicine' in text_lower or 'drug' in text_lower:
            return "Pharmacy"
        elif 'final' in text_lower and 'total' in text_lower:
            return "Final Bill"
        else:
            return "Bill Detail"

    def _extract_total(self, text: str) -> float:
        """
        Extract the final total from bill text.
        """
        # Look for patterns like "Total: 1234.56" or "Grand Total: 1234.56"
        patterns = [
            r'(?:grand\s+)?total[:\s]+(?:rs\.?|₹)?\s*(\d+(?:,\d{3})*(?:\.\d{2})?)',
            r'(?:net\s+)?amount[:\s]+(?:rs\.?|₹)?\s*(\d+(?:,\d{3})*(?:\.\d{2})?)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text.lower())
            if match:
                amount_str = match.group(1).replace(',', '')
                try:
                    return float(amount_str)
                except:
                    pass
        
        return 0.0
