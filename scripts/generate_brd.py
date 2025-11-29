"""
generate_brd.py - Business Requirements Document Generator

Part of Sait's Product Pipeline Toolkit

This script generates a structured Business Requirements Document (BRD) from a product vision
using the Gemini API. The output is validated against a BAML schema and saved as brd.json.

Usage:
    1. Ensure GEMINI_API_KEY is set in your .env file
    2. Edit the product_vision variable below with your product idea
    3. Run from project root: python scripts/generate_brd.py
    4. Output will be saved to ./brd.json

Requirements:
    - Google Gemini API key
    - BAML client generated from baml_src/ schemas
"""

from dotenv import load_dotenv
load_dotenv()
import os
import google.generativeai as genai
import json
import re
from baml_client.types import BRD  # Your BAML-generated Pydantic class

# Configure Gemini with your API key from .env
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-2.5-pro")  # Use your desired Gemini model

product_vision = (
    "Build a colorful, child-friendly Tic Tac Toe app (called 3T) in React Native for iPhone, iPad, and Android. "
    "It should be easy for young children to play, use fun graphics and sounds, "
    "and include a helpful AI coach to encourage learning and social play. "
    "The app should support single-player and two-player modes, "
    "quick feedback, and gentle win/loss animations."
)

# Prompt instructing the LLM to respond with only schema-compliant JSON
prompt = (
    "You are a Product Strategist. Turn the product vision into a structured Business Requirements Document (BRD) "
    "for a React Native children's Tic Tac Toe mobile app ('3T'). "
    "Respond only with a JSON object matching this format:\n"
    "{ \"title\": string, \"description\": string, \"objectives\": [string, ...] }\n"
    "Focus on learning, fun, easy play, and safe social interaction. Avoid technical implementation details."
)

response = model.generate_content(
    f"{prompt}\n\nProduct Vision:\n{product_vision}",
    stream=False
)

# First strip leading/trailing whitespace
cleaned = response.text.strip()

# Remove the opening code fence (```json or ```
cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)
# Remove closing code fence (```
cleaned = re.sub(r"\s*```$", "", cleaned)

# If 'cleaned' is still empty, print for debugging:
if not cleaned:
    print('Cleaned string is empty. Raw output was:', response.text)
    exit(1)

print('Cleaned:', repr(cleaned))

try:
    json_response = json.loads(cleaned)
    brd = BRD(**json_response)
except Exception as e:
    print("Error validating or parsing model output:", e)
    print("Raw response:\n", response.text)
    exit(1)

print("BRD Title:", brd.title)
print("\nDescription:\n", brd.description)
print("\nObjectives:")
for i, obj in enumerate(brd.objectives, 1):
    print(f"{i}. {obj}")

# Save validated BRD to disk for other agents to use
with open("brd.json", "w") as f:
    try:
        f.write(brd.model_dump_json(indent=2))  # Pydantic v2+
    except AttributeError:
        f.write(brd.json(indent=2))  # Pydantic v1 fallback

print("\nBRD saved to brd.json")
