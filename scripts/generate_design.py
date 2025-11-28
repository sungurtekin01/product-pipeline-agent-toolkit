"""
generate_design.py - Design Specification Generator

Part of Sait's Product Pipeline Toolkit

This script generates detailed design specifications from a BRD using the Gemini API
and a designer persona. The output includes screens, components, and wireframes,
validated against a BAML schema.

Usage:
    1. Ensure generate_brd.py has been run and brd.json exists
    2. Ensure GEMINI_API_KEY is set in your .env file
    3. Run from project root: python scripts/generate_design.py
    4. Output will be saved to ./design-spec.json

Requirements:
    - brd.json (from generate_brd.py)
    - Google Gemini API key
    - Designer persona file (rn_designer.toml)
    - BAML client generated from baml_src/ schemas
"""

from dotenv import load_dotenv
load_dotenv()
import os
import google.generativeai as genai
import json
import re
from baml_client.types import DesignSpec  # BAML-generated schema

# Load the previously validated BRD from disk
with open("brd.json") as f:
    brd = json.load(f)

# Load designer persona and best practices from designer.toml
with open("personas/rn_designer.toml") as toml_file:
    designer_persona = toml_file.read()

# Provide a schema hint to guide Gemini output structure
schema_hint = (
    "Output a single JSON object matching this schema: "
    '{ "summary": string, "screens": [ { "name": string, "description": string, "wireframe": string, "components": [ { "name": string, "description": string, "code_snippet": string, "notes": string } ] } ] }'
)

# Compose the full prompt for Gemini
full_prompt = (
    f"{designer_persona}\n\n"
    f"{schema_hint}\n"
    "Here is the validated BRD for the React Native Tic Tac Toe app:\n"
    f"{json.dumps(brd, indent=2)}"
)

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-2.5-pro")

response = model.generate_content(full_prompt, stream=False)

# Robust cleaning of code fences
cleaned = response.text.strip()
cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)
cleaned = re.sub(r"\s*```$", "", cleaned)

try:
    json_response = json.loads(cleaned)
    design = DesignSpec(**json_response)
except Exception as e:
    print("Error validating design artifact:", e)
    print("Raw output:\n", cleaned)
    exit(1)

with open("design-spec.json", "w") as f:
    try:
        f.write(design.model_dump_json(indent=2))  # Pydantic v2
    except AttributeError:
        f.write(design.json(indent=2))             # Pydantic v1

print("Design spec saved to design-spec.json")

