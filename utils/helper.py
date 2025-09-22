# utils/helper.py
import json
import re
from typing import Any, Dict, List
from google import genai
from google.genai import types
from .prompt import system_prompt

# ========== Cleaning ==========
def clean_description(text: str) -> str:
    if not text:
        return ""
    text = re.sub(r"\[\d+(?:,\s*\d+)*\]", "", text)
    text = re.sub(r"\*(.*?)\*", r"\1", text)
    text = re.sub(r"\"([^\"]+)\"", r"\1", text)
    return text.strip()

# ========== JSON Parsing ==========
def parse_json_block(text: str) -> Any:
    if not text:
        return None
    cleaned = re.sub(r"^```(?:json)?\s*", "", text.strip())
    cleaned = re.sub(r"\s*```$", "", cleaned)
    match = re.search(r"(\[\s*{.*?}\s*\]|\{.*?\})", cleaned, re.DOTALL)
    if not match:
        return None
    try:
        return json.loads(match.group(1))
    except Exception:
        return None

# ========== Prompt builder ==========
def create_metadata_prompt(row: Dict[str, Any]) -> str:
    return (
        f"START_OF_SHOW\n"
        f"SHOW_ID: {row.get('show_id','')}\n"
        f"SHOW_TITLE: {row.get('show_title','')}\n"
        f"ORIGINAL_TITLE: {row.get('original_title','')}\n"
        f"PRODUCTION_YEAR: {row.get('production_year','')}\n"
        f"SHOW_DESCRIPTION: Translate all content into fluent, professional English. Do NOT output any text in the original language.\n"
        f"GENRE: {row.get('genre','')}\n"
        f"DIRECTOR: {row.get('director','')}\n"
        f"PRODUCTION_COUNTRY: {row.get('production_country','')}\n"
        f"ACTOR: {row.get('actor','')}\n"
        f"ONEPLAY_ORIGINAL: {row.get('oneplay_original','')}\n"
        f"END_OF_SHOW\n"
        "IMPORTANT INSTRUCTIONS:\n"
        "- Translate all content to English.\n"
        "- Follow the strict narrative structure provided in the system prompt.\n"
        "- Produce a rich, detailed, professional English description.\n"
        "- Do NOT omit metadata categories."
    )

# ========== Batch generator ==========
def generate_metadata_for_batch(
    gclient: genai.Client,
    model: str,
    rows: List[Dict[str, Any]]
) -> List[str]:

    batch_prompts = [create_metadata_prompt(row) for row in rows]
    combined_prompt = "\n".join(batch_prompts) + "\nRespond with a JSON array of objects with keys: show_id, show_title, show_description_enhanced"

    cfg = types.GenerateContentConfig(
        system_instruction=system_prompt,
        tools=[types.Tool(google_search=types.GoogleSearch())],
    )

    response = gclient.models.generate_content(
        model=model,
        contents=combined_prompt,
        config=cfg,
    )

    text = response.text or ""
    parsed = parse_json_block(text)
    if not parsed or not isinstance(parsed, list):
        return [row.get("show_description","") for row in rows]

    out = []
    for i, row in enumerate(rows):
        try:
            desc = clean_description(parsed[i].get("show_description_enhanced",""))
        except Exception:
            desc = row.get("show_description","")
        out.append(desc)
    return out