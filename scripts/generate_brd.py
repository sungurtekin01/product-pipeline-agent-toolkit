"""
generate_brd.py - Business Requirements Document Generator

Part of Sait's Product Pipeline Toolkit

This script generates a structured Business Requirements Document (BRD) from a product vision
using the Gemini API. The output is validated against a BAML schema and saved as brd.json.

Usage:
    # With config file (product.config.json in project root):
    python scripts/generate_brd.py --project /path/to/project

    # With command-line arguments:
    python scripts/generate_brd.py --vision "Your product vision" --output docs/product

    # Backward compatible (from toolkit directory):
    python scripts/generate_brd.py

Requirements:
    - Google Gemini API key
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

from baml_client.types import BRD  # Your BAML-generated Pydantic class
from src.personas.loader import PersonaLoader

# Parse command-line arguments
parser = argparse.ArgumentParser(description='Generate Business Requirements Document')
parser.add_argument('--project', default='.', help='Project directory path')
parser.add_argument('--output', help='Output directory (overrides config)')
parser.add_argument('--vision', help='Product vision (overrides config)')
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

# Determine values (priority: CLI args > config > defaults)
product_vision = args.vision or config.get('vision',
    "Build a colorful, child-friendly Tic Tac Toe app (called 3T) in React Native for iPhone, iPad, and Android. "
    "It should be easy for young children to play, use fun graphics and sounds, "
    "and include a helpful AI coach to encourage learning and social play. "
    "The app should support single-player and two-player modes, "
    "quick feedback, and gentle win/loss animations."
)
output_dir = args.output or config.get('output_dir', '.')
output_path = project_path / output_dir

# Ensure output directory exists
output_path.mkdir(parents=True, exist_ok=True)
print(f"✓ Output directory: {output_path}")

# Configure Gemini with your API key from .env
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-2.5-pro")  # Use your desired Gemini model

# Load strategist persona from TOML file
personas_dir = toolkit_dir / 'personas'
persona_loader = PersonaLoader(personas_dir)
strategist_prompt = persona_loader.get_prompt('strategist')

response = model.generate_content(
    f"{strategist_prompt}\n\nProduct Vision:\n{product_vision}",
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
brd_output = output_path / 'brd.json'
with open(brd_output, "w") as f:
    try:
        f.write(brd.model_dump_json(indent=2))  # Pydantic v2+
    except AttributeError:
        f.write(brd.json(indent=2))  # Pydantic v1 fallback

print(f"\n✓ BRD saved to {brd_output}")
