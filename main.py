import os
import json
import functions_framework
from typing import List, Dict
from google import genai
from utils.helper import generate_metadata_for_batch

MODEL = "gemini-2.5-pro"
api_key = os.environ.get("api_key")
gclient = genai.Client(api_key=api_key)

@functions_framework.http
def enrich_description(request):
    try:
        req = request.get_json(silent=True)
        if not req or "calls" not in req:
            return json.dumps({"errorMessage": "Invalid request format"}), 400, {"Content-Type": "application/json"}

        rows: List[Dict[str, str]] = []
        for args in req["calls"]:
            rows.append({
                "show_id": args[0],
                "show_title": args[1],
                "show_description": args[2],
                "original_title": args[3],
                "production_year": args[4],
                "actor": args[5],
                "director": args[6],
                "genre": args[7],
                "production_country": args[8],
                "oneplay_original": args[9],
            })

        replies = generate_metadata_for_batch(gclient, MODEL, rows)
        return json.dumps({"replies": replies}), 200, {"Content-Type": "application/json"}

    except Exception as e:
        return json.dumps({"errorMessage": str(e)}), 500, {"Content-Type": "application/json"}