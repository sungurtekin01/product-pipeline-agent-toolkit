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

# Add toolkit directory to path for baml_client import
toolkit_dir = Path(__file__).parent.parent.resolve()
sys.path.insert(0, str(toolkit_dir))

from baml_client.types import DesignSpec  # BAML-generated schema
from src.personas.loader import PersonaLoader
from src.llm.factory import LLMFactory
from src.pipeline.config import PipelineConfig
from src.io.markdown_writer import MarkdownWriter
from src.agents.designer import DesignerAgent
from src.agents.strategist import StrategistAgent
from src.agents.conversation import ConversationOrchestrator

# Parse command-line arguments
parser = argparse.ArgumentParser(description='Generate Design Specification')
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

# Load the previously validated BRD from project directory
brd_file = output_path / 'brd.json'
if not brd_file.exists():
    print(f"❌ Error: brd.json not found at {brd_file}")
    print("   Please run generate_brd.py first.")
    exit(1)

with open(brd_file) as f:
    brd = json.load(f)
print(f"✓ Loaded BRD from {brd_file}")

# Load personas
personas_dir = toolkit_dir / 'personas'
persona_loader = PersonaLoader(personas_dir)
designer_prompt = persona_loader.get_prompt('designer')
strategist_prompt = persona_loader.get_prompt('strategist')
print(f"✓ Loaded designer and strategist personas")

# Create LLM clients with CLI overrides
cli_override = {}
if args.provider:
    cli_override['provider'] = args.provider
if args.model:
    cli_override['model'] = args.model

designer_llm = LLMFactory.from_config(
    pipeline_config.get_raw_config(),
    'designer',
    cli_override if cli_override else None
)

strategist_llm = LLMFactory.from_config(
    pipeline_config.get_raw_config(),
    'strategist',
    cli_override if cli_override else None
)

# Run Q&A session: Designer asks Strategist about BRD
print("\n" + "="*60)
print("Q&A SESSION: Designer ↔ Strategist")
print("="*60)

designer_agent = DesignerAgent(
    name="UX Designer",
    persona_prompt=designer_prompt,
    llm_client=designer_llm
)

strategist_agent = StrategistAgent(
    name="Product Strategist",
    persona_prompt=strategist_prompt,
    llm_client=strategist_llm
)

orchestrator = ConversationOrchestrator(output_path)
brd_text = json.dumps(brd, indent=2)

qa_conversation = orchestrator.run_qa_session(
    questioner=designer_agent,
    respondents=[(strategist_agent, brd_text)],
    session_name="design-qa",
    num_questions=5
)

print("="*60 + "\n")

# Use designer LLM client for final generation
llm_client = designer_llm

# Provide a schema hint to guide LLM output structure
schema_hint = (
    "Output a single JSON object matching this schema: "
    '{ "summary": string, "screens": [ { "name": string, "description": string, "wireframe": string, "components": [ { "name": string, "description": string, "code_snippet": string, "notes": string } ] } ] }'
)

# Compose the user prompt with Q&A context
user_prompt = (
    f"{schema_hint}\n\n"
    "Here is the validated BRD:\n"
    f"{json.dumps(brd, indent=2)}\n\n"
    "Additional context from Q&A session with Product Strategist:\n"
    f"{qa_conversation}"
)

# Generate design spec using LLM client
response = llm_client.generate(user_prompt, system_prompt=designer_prompt)

# Clean response (removes code fences)
cleaned = llm_client.clean_response(response)

try:
    json_response = json.loads(cleaned)
    design = DesignSpec(**json_response)
except Exception as e:
    print("Error validating design artifact:", e)
    print("Raw output:\n", cleaned)
    exit(1)

# Save design spec as markdown (primary output format)
design_md_output = output_path / 'design-spec.md'
MarkdownWriter.write_design_spec(design, design_md_output)
print(f"✓ Design spec saved to {design_md_output}")

# Also save as JSON for inter-script compatibility
design_json_output = output_path / 'design-spec.json'
with open(design_json_output, "w") as f:
    try:
        f.write(design.model_dump_json(indent=2))  # Pydantic v2
    except AttributeError:
        f.write(design.json(indent=2))             # Pydantic v1

print(f"✓ Design spec (JSON) saved to {design_json_output}")

