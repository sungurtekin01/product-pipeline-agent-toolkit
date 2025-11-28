"""
generate_tickets.py - Development Tickets Generator

Part of Sait's Product Pipeline Toolkit

This script generates development tickets organized by milestones from a BRD and design spec
using the Gemini API and a product owner persona. Tickets include acceptance criteria,
priorities, and dependencies.

Usage:
    1. Ensure generate_brd.py and generate_design.py have been run
    2. Ensure GEMINI_API_KEY is set in your .env file
    3. Run from project root: python scripts/generate_tickets.py
    4. Output will be saved to ./product/development-tickets.json

Requirements:
    - brd.json (from generate_brd.py)
    - design-spec.json (from generate_design.py)
    - Google Gemini API key
    - Product owner persona file (po.toml)
"""

from dotenv import load_dotenv
load_dotenv()
import os
import google.generativeai as genai
import json
import re

# No model import here unless you have a specific ticket schema class,
# if so, import ticket model like: from baml_client.types import TicketSpec

# Load BRD from disk
with open("brd.json") as f:
    brd = json.load(f)

# Load design spec for more detailed context
with open("design-spec.json") as f:
    design_spec = json.load(f)

# Load product owner persona prompt
with open("personas/po.toml") as toml_file:
    product_owner_persona = toml_file.read()

# Schema hint describing ticket output structure expected from Gemini
schema_hint = (
    "Output a JSON-formatted array of tickets grouped by milestones including fields: "
    "title, description, priority, dependencies, acceptance_criteria, complexity."
)

# Compose the prompt passed to Gemini including BRD, design spec, and schema hint
full_prompt = (
    f"{product_owner_persona}\n\n"
    f"{schema_hint}\n\n"
    "Here is the validated Business Requirements Document:\n"
    f"{json.dumps(brd, indent=2)}\n\n"
    "Here is the validated Design Spec:\n"
    f"{json.dumps(design_spec, indent=2)}"
)

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-2.5-pro")

response = model.generate_content(full_prompt, stream=False)

cleaned = response.text.strip()

# Remove code block fences if present
cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)
cleaned = re.sub(r"\s*```$", "", cleaned)

try:
    tickets_json = json.loads(cleaned)
except Exception as e:
    print("Error parsing ticket JSON:", e)
    print("Raw response:", cleaned)
    exit(1)

# Save tickets to product directory for developer consumption
os.makedirs("product", exist_ok=True)
with open("product/development-tickets.json", "w") as f:
    json.dump(tickets_json, f, indent=2)

print("Product owner tickets saved to product/development-tickets.json")
