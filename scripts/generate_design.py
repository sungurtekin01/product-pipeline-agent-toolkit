"""
generate_design.py - Design Specification Generator

Part of Sait's Product Pipeline Toolkit

This script generates detailed design specifications from a BRD using the Gemini API
and a designer persona. The output includes screens, components, and wireframes,
validated against a BAML schema.

Usage:
    # With config file (product.config.json in project root):
    python scripts/generate_design.py --project /path/to/project

    # With command-line arguments:
    python scripts/generate_design.py --output docs/product

    # Backward compatible (from toolkit directory):
    python scripts/generate_design.py

Requirements:
    - brd.json (from generate_brd.py)
    - Google Gemini API key
    - Designer persona file (rn_designer.toml)
    - BAML client generated from baml_src/ schemas
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path

from dotenv import load_dotenv
load_dotenv()
import google.generativeai as genai

# Add toolkit directory to path for baml_client import
toolkit_dir = Path(__file__).parent.parent.resolve()
sys.path.insert(0, str(toolkit_dir))

from baml_client.types import DesignSpec  # BAML-generated schema

# Parse command-line arguments
parser = argparse.ArgumentParser(description='Generate Design Specification')
parser.add_argument('--project', default='.', help='Project directory path')
parser.add_argument('--output', help='Output directory (overrides config)')
args = parser.parse_args()

# Resolve project path
project_path = Path(args.project).resolve()
config_path = project_path / 'product.config.json'

# Load config if exists
config = {}
if config_path.exists():
    with open(config_path) as f:
        config = json.load(f)
    print(f"✓ Loaded config from {config_path}")

# Determine output directory
output_dir = args.output or config.get('output_dir', '.')
output_path = project_path / output_dir

# Load the previously validated BRD from project directory
brd_file = output_path / 'brd.json'
if not brd_file.exists():
    print(f"❌ Error: brd.json not found at {brd_file}")
    print("   Please run generate_brd.py first.")
    exit(1)

with open(brd_file) as f:
    brd = json.load(f)
print(f"✓ Loaded BRD from {brd_file}")

# Load designer persona from toolkit directory
persona_file = toolkit_dir / 'personas' / 'rn_designer.toml'
with open(persona_file) as toml_file:
    designer_persona = toml_file.read()
print(f"✓ Loaded persona from {persona_file}")

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

design_output = output_path / 'design-spec.json'
with open(design_output, "w") as f:
    try:
        f.write(design.model_dump_json(indent=2))  # Pydantic v2
    except AttributeError:
        f.write(design.json(indent=2))             # Pydantic v1

print(f"✓ Design spec saved to {design_output}")

