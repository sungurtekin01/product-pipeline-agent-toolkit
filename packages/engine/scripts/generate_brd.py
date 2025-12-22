"""
generate_brd.py - Business Requirements Document Generator

Part of Sait's Product Pipeline Toolkit

This script generates a structured Business Requirements Document (BRD) from a product vision
using BAML functions and configurable LLM providers (Gemini, Claude, OpenAI).
The output is type-safe and validated against BAML schemas.

Usage:
    # Default (uses Gemini):
    python scripts/generate_brd.py --vision "Your product vision" --output docs/product

    # With specific provider:
    python scripts/generate_brd.py --vision "..." --output docs/ --provider claude

    # With feedback regeneration (auto-detected from docs/conversations/feedback/brd-feedback.md):
    python scripts/generate_brd.py --output docs/

Requirements:
    - LLM API key in .env (GEMINI_API_KEY, ANTHROPIC_API_KEY, or OPENAI_API_KEY)
    - BAML client generated from baml_src/ schemas
"""

import argparse
import asyncio
import sys
from pathlib import Path

from dotenv import load_dotenv
load_dotenv()

# Add toolkit directory to path for baml_client import
toolkit_dir = Path(__file__).parent.parent.resolve()
sys.path.insert(0, str(toolkit_dir))

from baml_client import b  # BAML client with functions
from baml_client.types import BRD  # Your BAML-generated Pydantic class
from src.personas.loader import PersonaLoader
from src.baml.client_registry import BAMLClientRegistry
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

# Configure client registry for provider selection
api_params = {}
if args.provider:
    api_params['strategist_provider'] = args.provider
    print(f"✓ Using provider: {args.provider}")

registry = BAMLClientRegistry(api_params if api_params else None)
client_registry = registry.get_client_registry()

# Build BAML options
baml_options = {}
if client_registry:
    baml_options["client_registry"] = client_registry

# Load strategist persona from TOML file
personas_dir = toolkit_dir / 'personas'
persona_loader = PersonaLoader(personas_dir)
strategist_prompt = persona_loader.get_prompt('strategist')

# Check for feedback and incorporate if exists
feedback_file = output_path / 'conversations' / 'feedback' / 'brd-feedback.md'
feedback = MarkdownParser.read_feedback(feedback_file)

async def generate_brd_async():
    """Async wrapper for BAML BRD generation"""
    if feedback:
        print(f"\n📝 Found feedback at {feedback_file}")
        print("🔄 Regenerating BRD with feedback incorporated...\n")

        # Use BAML function for regeneration with feedback
        return await b.GenerateBRDWithFeedback(
            vision=product_vision,
            feedback=feedback,
            persona=strategist_prompt,
            baml_options=baml_options
        )
    else:
        print("✓ No feedback found, generating initial BRD...\n")

        # Use BAML function for initial generation
        return await b.GenerateBRD(
            vision=product_vision,
            persona=strategist_prompt,
            baml_options=baml_options
        )

try:
    # Run async BAML function
    brd = asyncio.run(generate_brd_async())

except Exception as e:
    print(f"❌ Error generating BRD: {e}")
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
