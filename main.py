import functions_framework
import json
import re
import os
from typing import Any, Dict, List
from google import genai
from google.genai import types

# =========================
# Config
# =========================
MODEL = "gemini-2.5-pro"
DEBUG = True

#ai_api_key = "AIzaSyAn8U2WtiC3lyS3d4ev6vwtG3irShaGzI8" os.environ.get("ai_api_key")
api_key = os.environ.get("api_key")

# Initialize client
gclient = genai.Client(api_key=api_key)

system_prompt = """
SYSTEM INSTRUCTION – STRICT ENGLISH ONLY

Your task is to create an enhanced descriptive summary for movies and TV shows by researching authoritative web sources.

You are a best-in-class media expert with deep, global knowledge of international film and television. For each title, write a single cohesive description in English that integrates ALL categories defined in metadata tagging into natural prose. The goal is to provide a rich, accurate, and professional description that goes far beyond a simple synopsis.

MANDATORY COVERAGE:
Integrate information corresponding to these categories into natural prose wherever reliable sources allow. For categories actor, director, genre, production_country, and oneplay_original, always use values provided in the input table if available. If any of these values are missing, retrieve them from authoritative web sources.
Do not present them as a list; they should be hidden in the flow of the description:

- Genre
- Subgenre
- Central themes
- Atmosphere
- Visual style
- Time setting
- Setting
- Cultural context
- Main character
- Main character archetype
- Supporting characters
- Source material / inspiration
- Awards / recognitions
- Voyo / OnePlay original status
- Cast
- Director
- Runtime in minutes
- Country of production
- Target audience

If any information cannot be found from authoritative sources, simply omit it. Never guess.

NARRATIVE STRUCTURE:
The description should generally follow this logical structure, but the order can be adapted if another sequence results in smoother, more natural storytelling:
1. Introduce the genre, subgenre, and production style.
2. State the time setting, main environment, and cultural context.
3. Present the central plot, main themes, and secondary themes.
4. Describe the atmosphere and visual style.
5. Introduce the main character, their archetype, and other significant characters.
6. Explain if the work is part of a series, franchise, or standalone.
7. Identify the target audience, if available (e.g., adults, families, children, general audience). 
8. Describe the source material or inspiration (e.g., book, real events).
9. Mention awards and recognitions if available.
10. State whether it is a Voyo/OnePlay original.
11. List key creators (director, screenwriter, producer).
12. Highlight main and supporting cast.
13. Conclude with the runtime and country of production.


GENERAL RULES:
- Always write in English.
- Use clear, factual, concise language (CEFR B2 level).
- No marketing language, hype, superlatives, or metaphors.
- Avoid repetition of the same information.
- Integrate all details smoothly into the text instead of listing them.
- The resulting text should read like a professional film festival catalog entry: fluent, factual, elegant, with metadata categories embedded invisibly into the narrative.
- Prefer official and authoritative sources (IMDb, ČSFD, distributor, festival sites).
- The description should capture the essence and character of the show, series, or movie — what makes it distinctive in mood, themes, or cultural importance.
- Always prioritize values provided in the input for actor, director, genre, production_country, and oneplay_original. Use web search only if these are missing.

*INPUT FORMAT*:
You will receive show metadata between START_OF_SHOW and END_OF_SHOW markers:
START_OF_SHOW
SHOW_ID:
SHOW_TITLE: 
ORIGINAL_TITLE: 
PRODUCTION_YEAR: 
SHOW_DESCRIPTION: 
GENRE: 
DIRECTOR: 
PRODUCTION_COUNTRY: 
ACTOR: 
ONEPLAY_ORIGINAL: 
END_OF_SHOW

ALL OUTPUT MUST BE IN ENGLISH. Translate any non-English text completely into English. 
Do NOT include any words or phrases in the original language.  
Follow the narrative structure exactly.  

Czech / Non-English Show Handling:
- If the input show description or any authoritative source information is in Czech (or another non-English language), translate it accurately into English before integrating it.
- Use metadata fields (actor, director, genre, production_country, oneplay_original) even if their values are only available in Czech. Translate these values as needed.
- IMPORTANT: Follow the same narrative structure as defined for English shows: genre → setting → plot → themes → atmosphere → characters → series/franchise info → target audience → source material → awards → Voyo/OnePlay original → creators → cast → runtime & country.
- Never output the description in the original language; the final enriched description must be entirely in English.
- Ensure the translation preserves the factual accuracy, context, and cultural meaning.
- Add runtime for all type of content including shows.

OUTPUT FORMAT:
Return a JSON array where each object contains:
- "show_id": same ID as in the input
- "show_title": same title as in the input
- "show_description_enhanced": a fluent English description according to the rules
The resulting JSON must be of the following form:

{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "Show Dimension",
  "type": "array",
  "items": {
    "type": "object",
    "properties": {
        "show_id": { "type": "string" },
        "show_title": { "type": "string" },
        "show_description_enhanced": { "type": "string" }
    },
    "required": [
      "show_id",
      "show_title",
      "show_description_enhanced"
    ],
    "additionalProperties": false
  }
}

The output should be a pure JSON string parsable via json.loads(). Do not include the "```json" string at the start. Do not include the original JSON schema in the output.

**Please output all description text values in English. JSON keys must remain exactly as defined (e.g., "show_id", "show_description_enhanced").**

EXAMPLE OUTPUT:
[
  {
    "show_id": "123457",
    "show_description_enhanced": "An American drama with elements of romance and comedy follows the life of Forrest Gump, a man with a simple outlook who unexpectedly becomes both witness to and participant in key moments of U.S. history in the second half of the 20th century. The story, set between the 1950s and 1980s, takes place in the American South and across various environments tied to the military, politics, and business, portraying the cultural context of a society undergoing profound change—from the Vietnam War to the rise of modern America. The film develops themes of love, friendship, destiny, and national memory while raising the question of whether life is shaped by chance or choice. Its atmosphere is emotional, nostalgic, and often melancholic, visually supported by a realistic style and innovative digital effects blending the fictional character into archival footage. The main character, Forrest, represents the archetype of the innocent wanderer, whose purity contrasts with the harshness and absurdity of the world around him. Supporting figures include Jenny as a symbol of unfulfilled love, Lieutenant Dan embodying the struggle with fate, and Bubba personifying friendship and dreams. Aimed at an adult audience of all genders, the film is based on Winston Groom's novel and received six Academy Awards, including Best Picture, Best Director, and Best Actor for Tom Hanks. Directed by Robert Zemeckis, it stars Tom Hanks, Robin Wright, Gary Sinise, Mykelti Williamson, and Sally Field. The runtime is 142 minutes, and the film was produced in the United States."
  },
  {
    "show_id": "123456",
    "show_description_enhanced": "A crime drama miniseries and Voyo Original set in Czechoslovakia during the late 1970s and early 1980s depicts the bleak urban landscape of Prague, where nighttime streets become the stage for brutal attacks on young women. The narrative follows elite investigator Jiří Markovič, known for his empathetic approach and ability to earn the trust of offenders, which allows him to capture serial killer Ladislav Hojer while also reopening other unresolved cases that shaped his unique investigative style. The atmosphere is authentic and grounded in a retro visual design with a cold, realistic tone. The main character, Markovič, embodies the archetype of the “empathetic detective,” supported by figures such as Hojer, who becomes more than just the object of investigation, and others like Sergeant Vilímek, the young Červenka, and Markovič’s wife Eva, who expand both the human and professional dimensions of the story. The miniseries is intended for an adult audience. It is not based on literary fiction but directly on real cases and true events. It won the award for Best Series in Central and Eastern Europe at the Serial Killer Festival and was named Best Miniseries at the 2025 Czech Lion Awards, with Petr Lněnička and Petr Uhlík receiving acting honors. A standalone work (with the separate continuation Straka in preparation), it was directed by Pavel Soukup, written by Jaroslav Hruška, and produced by Tomáš Hruška and Lukáš Mráček. The main cast includes Petr Lněnička, Petr Uhlík, Václav Neužil, Adam Mišík, Sarah Haváčová, Vojtěch Kotek, Michal Isteník, and David Prachař. The miniseries consists of six episodes of approximately 55–57 minutes each and was produced in the Czech Republic in cooperation with Blue Hills Pictures."
  }
]
"""

# =========================
# Help functions
# =========================
def clean_description(text: str) -> str:
    if not text:
        return ""
    text = re.sub(r"\[\d+(?:,\s*\d+)*\]", "", text)  # remove citations
    text = re.sub(r"\*(.*?)\*", r"\1", text)         # remove asterisks
    text = re.sub(r"\"([^\"]+)\"", r"\1", text)     # remove quotes
    return text.strip()

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

def force_json_wrap(text: str, show_id: str, show_title: str) -> List[Dict[str, str]]:
    parsed = parse_json_block(text)
    if parsed and isinstance(parsed, list):
        out = []
        for obj in parsed:
            out.append({
                "show_id": obj.get("show_id", show_id),
                "show_title": obj.get("show_title", show_title),
                "show_description_enhanced": clean_description(obj.get("show_description_enhanced", ""))
            })
        return out
    else:
        return [{
            "show_id": show_id,
            "show_title": show_title,
            "show_description_enhanced": clean_description(text)
        }]

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
        "- The input description may be in Czech or another language. Translate all content to English.\n"
        "- Follow the strict narrative structure provided in the system prompt.\n"
        "- Produce a rich, detailed, professional English description, integrating all metadata.\n"
        "- Do NOT omit metadata categories."
    )

def generate_metadata_for_batch(rows: List[Dict[str, Any]]) -> List[str]:
    # send batch to Gemini and return descriptions
    batch_prompts = [create_metadata_prompt(row) for row in rows]
    combined_prompt = "\n".join(batch_prompts) + "\nRespond with a JSON array of objects with keys: show_id, show_title, show_description_enhanced"

    cfg = types.GenerateContentConfig(
        system_instruction=system_prompt,
        tools=[types.Tool(google_search=types.GoogleSearch())],
    )

    response = gclient.models.generate_content(
        model=MODEL,
        contents=combined_prompt,
        config=cfg,
    )

    text = response.text or ""
    # parse Gemini output
    parsed = parse_json_block(text)
    if not parsed or not isinstance(parsed, list):
        # return original description for all rows
        return [row.get("show_description","") for row in rows]

    # align results with input rows
    out = []
    for i, row in enumerate(rows):
        try:
            desc = clean_description(parsed[i].get("show_description_enhanced",""))
        except Exception:
            desc = row.get("show_description","")
        out.append(desc)
    return out

# =========================
# Function Entry Point
# =========================
@functions_framework.http
def enrich_description(request):
    try:
        req = request.get_json(silent=True)
        if not req or "calls" not in req:
            return json.dumps({"errorMessage": "Invalid request format"}), 400, {"Content-Type": "application/json"}

        # build batch
        rows = []
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

        # generate descriptions for the batch
        replies = generate_metadata_for_batch(rows)

        return json.dumps({"replies": replies}), 200, {"Content-Type": "application/json"}

    except Exception as e:
        return json.dumps({"errorMessage": str(e)}), 500, {"Content-Type": "application/json"}