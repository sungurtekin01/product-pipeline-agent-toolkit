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

# Add toolkit directory to path for baml_client import
toolkit_dir = Path(__file__).parent.parent.resolve()
sys.path.insert(0, str(toolkit_dir))

from baml_client.types import BRD  # Your BAML-generated Pydantic class
from src.personas.loader import PersonaLoader
from src.llm.factory import LLMFactory
from src.pipeline.config import PipelineConfig
from src.io.markdown_writer import MarkdownWriter
from src.io.markdown_parser import MarkdownParser

# Parse command-line arguments
parser = argparse.ArgumentParser(description='Generate Business Requirements Document')
parser.add_argument('--project', default='.', help='Project directory path')
parser.add_argument('--output', help='Output directory (overrides config)')
parser.add_argument('--vision', help='Product vision (overrides config)')
parser.add_argument('--provider', help='LLM provider: gemini, claude, openai (overrides config)')
parser.add_argument('--model', help='LLM model name (overrides config)')
args = parser.parse_args()

# Load project configuration
project_path = Path(args.project).resolve()
pipeline_config = PipelineConfig(project_path)

if pipeline_config.has_config():
    print(f"✓ Loaded config from {pipeline_config.config_path}")

# Get configuration values with CLI overrides (priority: CLI > config > defaults)
product_vision = pipeline_config.get_vision(cli_override=args.vision)
output_path = pipeline_config.get_output_dir(cli_override=args.output)

# Ensure output directory exists
output_path.mkdir(parents=True, exist_ok=True)
print(f"✓ Output directory: {output_path}")

# Create LLM client with CLI overrides
cli_override = {}
if args.provider:
    cli_override['provider'] = args.provider
if args.model:
    cli_override['model'] = args.model

llm_client = LLMFactory.from_config(
    pipeline_config.get_raw_config(),
    'strategist',
    cli_override if cli_override else None
)

# Load strategist persona from TOML file
personas_dir = toolkit_dir / 'personas'
persona_loader = PersonaLoader(personas_dir)
strategist_prompt = persona_loader.get_prompt('strategist')

# Check for feedback and incorporate if exists
feedback_file = output_path / 'conversations' / 'feedback' / 'brd-feedback.md'
feedback = MarkdownParser.read_feedback(feedback_file)

if feedback:
    print(f"\n📝 Found feedback at {feedback_file}")
    print("🔄 Regenerating BRD with feedback incorporated...\n")
    user_prompt = (
        f"Product Vision:\n{product_vision}\n\n"
        f"Previous BRD Feedback:\n{feedback}\n\n"
        "Please regenerate the BRD incorporating the feedback above."
    )
else:
    print("✓ No feedback found, generating initial BRD...\n")
    user_prompt = f"Product Vision:\n{product_vision}"

# Generate BRD using LLM client
response = llm_client.generate(user_prompt, system_prompt=strategist_prompt)

# Clean response (removes code fences)
cleaned = llm_client.clean_response(response)

# If 'cleaned' is still empty, print for debugging:
if not cleaned:
    print('Cleaned string is empty. Raw output was:', response)
    exit(1)

print('Cleaned:', repr(cleaned))

try:
    json_response = json.loads(cleaned)
    brd = BRD(**json_response)
except Exception as e:
    print("Error validating or parsing model output:", e)
    print("Raw response:\n", response)
    exit(1)

print("BRD Title:", brd.title)
print("\nDescription:\n", brd.description)
print("\nObjectives:")
for i, obj in enumerate(brd.objectives, 1):
    print(f"{i}. {obj}")

# Save BRD as markdown (primary output format)
brd_md_output = output_path / 'BRD.md'
MarkdownWriter.write_brd(brd, brd_md_output)
print(f"\n✓ BRD saved to {brd_md_output}")

# Also save as JSON for inter-script compatibility
brd_json_output = output_path / 'brd.json'
with open(brd_json_output, "w") as f:
    try:
        f.write(brd.model_dump_json(indent=2))  # Pydantic v2+
    except AttributeError:
        f.write(brd.json(indent=2))  # Pydantic v1 fallback

print(f"✓ BRD (JSON) saved to {brd_json_output}")
