"""Small helper to OCR an image with Google Vision REST API and parse it
with the Generative (Gemini) REST API.

This file provides two main helpers:
- ocr_with_vision_api(image_path): uses GOOGLE_API_KEY to call Vision API
- parse_trade_with_gemini(text): uses GOOGLE_API_KEY to call Generative API

Both functions raise RuntimeError with a clear message if credentials are
missing. These are lightweight REST clients using `requests` so no heavy
Google client libs are required.
"""
from __future__ import annotations
import base64
import json
import os
from pathlib import Path
from typing import Dict, Any

from dotenv import load_dotenv
import requests

# load environment from .env if present
load_dotenv()


def _clean_key(k: str | None) -> str | None:
    if not k:
        return None
    # remove surrounding whitespace and optional quotes
    return k.strip().strip('"').strip("'")


GOOGLE_API_KEY = _clean_key(os.environ.get("GOOGLE_API_KEY"))


def _require_api_key() -> str:
    if not GOOGLE_API_KEY:
        raise RuntimeError(
            "Missing GOOGLE_API_KEY env var. Set it to a Google Cloud API key "
            "with access to Vision API and Generative Models."
        )
    return GOOGLE_API_KEY


def ocr_with_vision_api(image_path: str) -> str:
    """Perform OCR on image using Google Vision REST API (TEXT_DETECTION).

    Requires environment variable GOOGLE_API_KEY.
    Returns the full detected text (string).
    """
    key = _require_api_key()
    url = f"https://vision.googleapis.com/v1/images:annotate?key={key}"
    img_bytes = Path(image_path).read_bytes()
    b64 = base64.b64encode(img_bytes).decode("utf-8")
    payload = {
        "requests": [
            {
                "image": {"content": b64},
                "features": [{"type": "TEXT_DETECTION", "maxResults": 1}],
            }
        ]
    }
    resp = requests.post(url, json=payload, timeout=30)
    if not resp.ok:
        raise RuntimeError(f"Vision API error: {resp.status_code} {resp.text}")
    data = resp.json()
    try:
        text = (
            data["responses"][0]
            .get("fullTextAnnotation", {})
            .get("text", "")
        )
        return text
    except Exception as e:
        raise RuntimeError(f"Unexpected Vision API response: {e}\n{data}")


def parse_trade_with_gemini(text: str) -> Dict[str, Any]:
    """Send extracted text to Gemini (Generative API) to extract trade details.

    This uses the Generative REST endpoint and GOOGLE_API_KEY. The function
    returns a dict with structured fields returned by the model.
    NOTE: You must enable the appropriate API and billing on your GCP project.
    """
    key = _require_api_key()
    # Model name can be adjusted; 'models/gemini-1.5' is an example. Check
    # Google docs for available model names and endpoints.
    model = os.environ.get("GEMINI_MODEL", "models/gemini-1.5")
    url = (
        "https://generativelanguage.googleapis.com/v1beta2/"
        f"{model}:generateText?key={key}"
    )

    # Strict prompt: request JSON-only output (single JSON object).
    # Include a short schema example to encourage well-formed output.
    schema_example = (
        '{"action": "BUY", "symbol": "BTC/USDT", "size": 0.5, '
        '"price": 30000, "order_type": "LIMIT", "sl": 29500, '
        '"tp": 31000, "leverage": null, "notes": ""}'
    )
    prompt = (
        "You are a parser. Extract trade details and return a single JSON "
        "object only. Use the following example as the exact JSON shape: "
        + schema_example
        + "\nRespond with JSON only, no explanation. Now parse the text:\n\n"
        + text
    )

    payload = {"prompt": {"text": prompt}, "candidate_count": 1}
    resp = requests.post(url, json=payload, timeout=30)
    if not resp.ok:
        raise RuntimeError(
            "Generative API error: %s %s" % (resp.status_code, resp.text)
        )
    data = resp.json()
    # Extract JSON object from model output robustly (balanced braces)
    
    def _extract_json_blob(s: str) -> str | None:
        if not s:
            return None
        start = s.find("{")
        if start == -1:
            return None
        depth = 0
        for i in range(start, len(s)):
            ch = s[i]
            if ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    return s[start:i + 1]
        return None

    try:
        candidates = data.get("candidates") or []
        if not candidates:
            return {
                "raw": data,
                "valid": False,
                "validation": ["no_candidates"],
            }
        out = candidates[0].get("output") or candidates[0].get("content") or ""
        blob = _extract_json_blob(out)
        if blob:
            try:
                parsed = json.loads(blob)
            except Exception:
                return {
                    "raw_output": out,
                    "valid": False,
                    "validation": ["json_parse_failed"],
                }
            # normalize numeric fields and symbol casing
            
            def _to_num(v):
                if v is None:
                    return None
                if isinstance(v, (int, float)):
                    return v
                s = str(v).strip()
                try:
                    if "." in s:
                        return float(s.replace(',', ''))
                    return int(s.replace(',', ''))
                except Exception:
                    try:
                        return float(s)
                    except Exception:
                        return s

            for k in ("size", "price", "sl", "tp", "leverage"):
                if k in parsed:
                    parsed[k] = _to_num(parsed[k])
            # normalize symbol to upper-case with slash if needed
            if parsed.get("symbol"):
                sym = str(parsed["symbol"]).upper()
                if "/" not in sym and len(sym) <= 6:
                    # heuristic: append /USDT if a plain symbol like BTC
                    sym = sym if "/" in sym else sym + "/USDT"
                parsed["symbol"] = sym
            # Validate parsed trade to avoid false alerts
            is_valid, reasons = validate_parsed_trade(parsed)
            parsed["valid"] = bool(is_valid)
            parsed["validation"] = reasons
            return parsed
        return {
            "raw_output": out,
            "valid": False,
            "validation": ["no_json_blob"],
        }
    except Exception as e:
        msg = "Unexpected Generative API response: %s\n%s" % (e, data)
        raise RuntimeError(msg)


def validate_parsed_trade(parsed: Dict[str, Any]) -> tuple[bool, list]:
    """Validate a parsed trade dict returned by Gemini.

    Returns (is_valid, reasons_list). The validation checks for presence
    of key fields and plausible numeric ranges to reduce false alerts.
    """
    reasons: list[str] = []
    if not isinstance(parsed, dict):
        return False, ["not_a_dict"]

    action = ""
    if parsed.get("action") is not None:
        action = str(parsed.get("action", "")).upper()
    if action not in ("BUY", "SELL"):
        reasons.append("invalid_action")

    symbol = parsed.get("symbol")
    if not symbol:
        reasons.append("missing_symbol")
    else:
        # Expect something like BTC or BTC/USDT or ETH/USDT
        sym = str(symbol).upper()
        import re

        if not re.match(r"^[A-Z0-9]{2,6}(?:/[A-Z0-9]{2,6})?$", sym):
            reasons.append("symbol_format")

    def _num_ok(key, min_val=0.0, max_val=1e9):
        v = parsed.get(key)
        if v is None:
            return True
        try:
            vv = float(v)
        except Exception:
            reasons.append(f"{key}_not_numeric")
            return False
        if vv <= min_val:
            reasons.append(f"{key}_not_positive")
            return False
        if vv > max_val:
            reasons.append(f"{key}_unrealistic")
            return False
        return True

    _num_ok("size", min_val=0.0, max_val=1e12)
    _num_ok("price", min_val=0.0, max_val=1e8)
    _num_ok("sl", min_val=0.0, max_val=1e8)
    _num_ok("tp", min_val=0.0, max_val=1e8)
    _num_ok("leverage", min_val=0.0, max_val=1000)

    # If both price and SL/TP present, check relative ordering
    try:
        price = parsed.get("price")
        sl = parsed.get("sl")
        tp = parsed.get("tp")
        if price is not None:
            p = float(price)
            if sl is not None and tp is not None:
                s = float(sl)
                t = float(tp)
                if action == "BUY":
                    if not (s < p < t):
                        reasons.append("sl_price_tp_inconsistent_for_buy")
                elif action == "SELL":
                    if not (s > p > t):
                        reasons.append("sl_price_tp_inconsistent_for_sell")
    except Exception:
        # non-fatal — numeric issues already captured above
        pass

    # order type basic check
    ot = parsed.get("order_type")
    if ot is not None and str(ot).upper() not in ("MARKET", "LIMIT"):
        reasons.append("unknown_order_type")

    is_valid = len(reasons) == 0
    return is_valid, reasons


if __name__ == "__main__":
    import argparse

    p = argparse.ArgumentParser()
    p.add_argument("image", help="Path to image to analyze")
    args = p.parse_args()
    txt = ocr_with_vision_api(args.image)
    print("OCR text:\n", txt)
    parsed = parse_trade_with_gemini(txt)
    print("Parsed result:\n", json.dumps(parsed, indent=2))
