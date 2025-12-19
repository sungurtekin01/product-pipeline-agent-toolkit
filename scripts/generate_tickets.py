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

# Add toolkit directory to path
toolkit_dir = Path(__file__).parent.parent.resolve()
sys.path.insert(0, str(toolkit_dir))

# No model import here unless you have a specific ticket schema class,
# if so, import ticket model like: from baml_client.types import TicketSpec
from src.personas.loader import PersonaLoader
from src.llm.factory import LLMFactory
from src.pipeline.config import PipelineConfig

# Parse command-line arguments
parser = argparse.ArgumentParser(description='Generate Development Tickets')
parser.add_argument('--project', default='.', help='Project directory path')
parser.add_argument('--output', help='Output directory (overrides config)')
parser.add_argument('--provider', help='LLM provider: gemini, claude, openai (overrides config)')
parser.add_argument('--model', help='LLM model name (overrides config)')
args = parser.parse_args()

# Load project configuration
project_path = Path(args.project).resolve()
pipeline_config = PipelineConfig(project_path)

if pipeline_config.has_config():
    print(f"✓ Loaded config from {pipeline_config.config_path}")

# Get output directory with CLI override
output_path = pipeline_config.get_output_dir(cli_override=args.output)

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

# Load product owner persona
personas_dir = toolkit_dir / 'personas'
persona_loader = PersonaLoader(personas_dir)
po_prompt = persona_loader.get_prompt('po')
print(f"✓ Loaded product owner persona")

# Create LLM client with CLI overrides
cli_override = {}
if args.provider:
    cli_override['provider'] = args.provider
if args.model:
    cli_override['model'] = args.model

llm_client = LLMFactory.from_config(
    pipeline_config.get_raw_config(),
    'po',
    cli_override if cli_override else None
)

# Schema hint describing ticket output structure expected from LLM
schema_hint = (
    "Output a JSON-formatted array of tickets grouped by milestones including fields: "
    "title, description, priority, dependencies, acceptance_criteria, complexity."
)

# Compose the user prompt including BRD, design spec, and schema hint
user_prompt = (
    f"{schema_hint}\n\n"
    "Here is the validated Business Requirements Document:\n"
    f"{json.dumps(brd, indent=2)}\n\n"
    "Here is the validated Design Spec:\n"
    f"{json.dumps(design_spec, indent=2)}"
)

# Generate tickets using LLM client
response = llm_client.generate(user_prompt, system_prompt=po_prompt)

# Clean response (removes code fences)
cleaned = llm_client.clean_response(response)

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
