import requests
import json
import time

# Test URLs from the sample dataset
test_urls = [
    "https://hackrx.blob.core.windows.net/assets/datathon-IIT/sample_2.png",
    # Add more sample URLs here after downloading the training data
]

def test_api(document_url):
    """Test the API with a document URL"""
    api_url = "http://localhost:8000/extract-bill-data"
    
    print(f"\n{'='*80}")
    print(f"Testing: {document_url}")
    print(f"{'='*80}")
    
    payload = {"document": document_url}
    
    try:
        start_time = time.time()
        response = requests.post(api_url, json=payload, timeout=120)
        elapsed_time = time.time() - start_time
        
        print(f"\n✅ Status Code: {response.status_code}")
        print(f"⏱️  Processing Time: {elapsed_time:.2f} seconds")
        
        result = response.json()
        
        # Display results
        print(f"\n📊 Results:")
        print(f"  Success: {result.get('is_success', False)}")
        
        if 'token_usage' in result:
            usage = result['token_usage']
            print(f"\n🔢 Token Usage:")
            print(f"  Total Tokens: {usage.get('total_tokens', 0)}")
            print(f"  Input Tokens: {usage.get('input_tokens', 0)}")
            print(f"  Output Tokens: {usage.get('output_tokens', 0)}")
        
        if 'data' in result and result['data']:
            data = result['data']
            print(f"\n📄 Extracted Data:")
            print(f"  Total Items: {data.get('total_item_count', 0)}")
            print(f"  Pages: {len(data.get('pagewise_line_items', []))}")
            
            # Show items from each page
            for page in data.get('pagewise_line_items', []):
                print(f"\n  Page {page['page_no']} ({page['page_type']}):")
                print(f"    Items: {len(page['bill_items'])}")
                
                total_amount = 0
                for item in page['bill_items']:
                    print(f"      - {item['item_name']}: {item['item_quantity']} x {item['item_rate']} = {item['item_amount']}")
                    total_amount += item['item_amount']
                
                print(f"    Page Total: {total_amount:.2f}")
        
        if 'error' in result:
            print(f"\n❌ Error: {result['error']}")
        
        # Save full response
        output_file = f"test_result_{int(time.time())}.json"
        with open(output_file, 'w') as f:
            json.dump(result, f, indent=2)
        print(f"\n💾 Full response saved to: {output_file}")
        
        return result
        
    except requests.exceptions.ConnectionError:
        print("\n❌ Error: Could not connect to API server")
        print("Make sure the server is running: uvicorn src.api:app --reload --host 0.0.0.0 --port 8000")
        return None
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    print("🧪 Bill Extraction API - Test Suite")
    print("=" * 80)
    
    # Check if server is running
    try:
        health = requests.get("http://localhost:8000/health", timeout=5)
        print(f"✅ Server is running (Status: {health.json()['status']})")
    except:
        print("❌ Server is not running!")
        print("Start it with: uvicorn src.api:app --reload --host 0.0.0.0 --port 8000")
        exit(1)
    
    # Run tests
    results = []
    for url in test_urls:
        result = test_api(url)
        results.append(result)
        time.sleep(1)  # Small delay between tests
    
    # Summary
    print(f"\n{'='*80}")
    print("📊 Test Summary")
    print(f"{'='*80}")
    print(f"Total Tests: {len(results)}")
    print(f"Successful: {sum(1 for r in results if r and r.get('is_success'))}")
    print(f"Failed: {sum(1 for r in results if not r or not r.get('is_success'))}")
