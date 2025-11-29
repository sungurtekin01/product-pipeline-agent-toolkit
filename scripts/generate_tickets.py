"""
generate_tickets.py - Development Tickets Generator

Part of Sait's Product Pipeline Toolkit

This script generates development tickets organized by milestones from a BRD and design spec
using the Gemini API and a product owner persona. Tickets include acceptance criteria,
priorities, and dependencies.

Usage:
    # With config file (product.config.json in project root):
    python scripts/generate_tickets.py --project /path/to/project

    # With command-line arguments:
    python scripts/generate_tickets.py --output docs/product

    # Backward compatible (from toolkit directory):
    python scripts/generate_tickets.py

Requirements:
    - brd.json (from generate_brd.py)
    - design-spec.json (from generate_design.py)
    - Google Gemini API key
    - Product owner persona file (po.toml)
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

# Add toolkit directory to path
toolkit_dir = Path(__file__).parent.parent.resolve()
sys.path.insert(0, str(toolkit_dir))

# No model import here unless you have a specific ticket schema class,
# if so, import ticket model like: from baml_client.types import TicketSpec

# Parse command-line arguments
parser = argparse.ArgumentParser(description='Generate Development Tickets')
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

# Load BRD from project directory
brd_file = output_path / 'brd.json'
if not brd_file.exists():
    print(f"❌ Error: brd.json not found at {brd_file}")
    print("   Please run generate_brd.py first.")
    exit(1)

with open(brd_file) as f:
    brd = json.load(f)
print(f"✓ Loaded BRD from {brd_file}")

# Load design spec for more detailed context
design_file = output_path / 'design-spec.json'
if not design_file.exists():
    print(f"❌ Error: design-spec.json not found at {design_file}")
    print("   Please run generate_design.py first.")
    exit(1)

with open(design_file) as f:
    design_spec = json.load(f)
print(f"✓ Loaded design spec from {design_file}")

# Load product owner persona from toolkit directory
persona_file = toolkit_dir / 'personas' / 'po.toml'
with open(persona_file) as toml_file:
    product_owner_persona = toml_file.read()
print(f"✓ Loaded persona from {persona_file}")

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

# Save tickets to project output directory
tickets_output = output_path / 'development-tickets.json'
with open(tickets_output, "w") as f:
    json.dump(tickets_json, f, indent=2)

print(f"✓ Development tickets saved to {tickets_output}")
