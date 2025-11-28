from typing import List
from .models import LineItem, Invoice, PageData
import difflib

class Validator:
    def deduplicate_rows(self, items: List[LineItem]) -> List[LineItem]:
        """
        Remove duplicate rows based on content similarity.
        Uses fuzzy matching on item_name.
        """
        unique_items = []
        seen_names = []
        
        for item in items:
            # Normalize name for comparison
            name_key = item.item_name.lower().strip()
            
            # Check for fuzzy match with existing items
            is_duplicate = False
            for seen_name in seen_names:
                similarity = difflib.SequenceMatcher(None, name_key, seen_name).ratio()
                if similarity > 0.9:  # 90% similarity threshold
                    is_duplicate = True
                    break
            
            if not is_duplicate:
                unique_items.append(item)
                seen_names.append(name_key)
        
        return unique_items

    def validate_math(self, invoice: Invoice) -> bool:
        """
        Check if calculated total matches extracted total.
        """
        if not invoice.total_amount:
            return False
            
        calculated = invoice.calculated_total
        # Allow small floating point difference
        return abs(calculated - invoice.total_amount) < 0.05
