"""CLI to send an image to Google Vision and Gemini for structured trade parsing.

Requires environment variable GOOGLE_API_KEY to be set.
"""
from __future__ import annotations
import argparse
from pathlib import Path
import json

from dotenv import load_dotenv
load_dotenv()

from gemini_client import ocr_with_vision_api, parse_trade_with_gemini


def main():
    p = argparse.ArgumentParser()
    p.add_argument("image", help="Path to image to send")
    args = p.parse_args()
    image = Path(args.image)
    if not image.exists():
        raise SystemExit(f"Image not found: {image}")
    txt = ocr_with_vision_api(str(image))
    print("OCR text:\n", txt)
    parsed = parse_trade_with_gemini(txt)
    if isinstance(parsed, dict) and parsed.get('valid') is False:
        print('Parsed result failed validation:', parsed.get('validation'))
        print(json.dumps(parsed, indent=2))
    else:
        print("Parsed JSON:\n", json.dumps(parsed, indent=2))


if __name__ == "__main__":
    main()
