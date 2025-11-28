import os
import json
from typing import List, Dict, Any, Optional, Tuple
from groq import Groq
from .prompts import ROW_RECONSTRUCTION_PROMPT, AMBIGUITY_RESOLUTION_PROMPT
from ..validation.models import TokenUsage

class LLMClient:
    def __init__(self, api_key: Optional[str] = None):
        self.client = Groq(api_key=api_key or os.environ.get("GROQ_API_KEY"))
        # Using Llama 3.3 70B - fast and accurate
        self.model = "llama-3.3-70b-versatile"
        self.token_usage = TokenUsage()

    def _update_usage(self, input_tokens: int, output_tokens: int):
        self.token_usage.input_tokens += input_tokens
        self.token_usage.output_tokens += output_tokens
        self.token_usage.total_tokens += (input_tokens + output_tokens)

    def reconstruct_table(self, text_segment: str) -> List[Dict[str, Any]]:
        """
        Send text segment to LLM to reconstruct table rows.
        """
        prompt = ROW_RECONSTRUCTION_PROMPT.format(text_segment=text_segment)
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert at extracting structured bill data. Always return valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=4096,
            )
            
            # Update usage
            self._update_usage(response.usage.prompt_tokens, response.usage.completion_tokens)
            
            # Basic parsing, assuming the LLM returns pure JSON or JSON block
            content = response.choices[0].message.content.strip()
            
            # Find JSON start/end if there's extra text
            start = content.find('[')
            end = content.rfind(']') + 1
            if start != -1 and end != -1:
                json_str = content[start:end]
                items = json.loads(json_str)
                
                # Validate and clean items
                valid_items = []
                for item in items:
                    if isinstance(item, dict) and 'item_name' in item and 'item_amount' in item:
                        # Ensure all required fields exist
                        valid_item = {
                            'item_name': str(item.get('item_name', '')).strip(),
                            'item_rate': float(item.get('item_rate', 0.0)),
                            'item_quantity': float(item.get('item_quantity', 1.0)),
                            'item_amount': float(item.get('item_amount', 0.0))
                        }
                        if valid_item['item_name'] and valid_item['item_amount'] > 0:
                            valid_items.append(valid_item)
                
                return valid_items
            
            return []
        except Exception as e:
            print(f"Error in reconstruct_table: {e}")
            import traceback
            traceback.print_exc()
            return []

    def resolve_ambiguity(self, row_data: Dict[str, Any], context: str) -> Dict[str, Any]:
        """
        Resolve ambiguity in a specific row.
        """
        prompt = AMBIGUITY_RESOLUTION_PROMPT.format(row_data=row_data, context=context)
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert at correcting bill data. Always return valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=1024,
            )
            
            # Update usage
            self._update_usage(response.usage.prompt_tokens, response.usage.completion_tokens)
            
            content = response.choices[0].message.content.strip()
            start = content.find('{')
            end = content.rfind('}') + 1
            if start != -1 and end != -1:
                return json.loads(content[start:end])
            return row_data
        except Exception as e:
            print(f"Error in resolve_ambiguity: {e}")
            return row_data
            
    def get_usage(self) -> TokenUsage:
        return self.token_usage
