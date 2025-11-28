import argparse
import json
import os
from src.pipeline.core import ExtractionPipeline

def main():
    parser = argparse.ArgumentParser(description="Intelligent Bill Line-Item Extraction")
    parser.add_argument("--image_path", help="Path to local bill image")
    parser.add_argument("--url", help="URL of the bill (PDF or Image)")
    args = parser.parse_args()

    if not args.image_path and not args.url:
        print("Error: Must provide either --image_path or --url")
        return

    pipeline = ExtractionPipeline()
    
    if args.url:
        result = pipeline.process_url(args.url)
    else:
        # Fallback for local testing if needed, though process_url handles logic better now
        # For consistency, we might want to wrap local files in a similar flow
        # But for now let's just print a message if they use the old flag without logic update
        print("Local file processing not fully updated to new flow. Please use --url or update code.")
        return

    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
