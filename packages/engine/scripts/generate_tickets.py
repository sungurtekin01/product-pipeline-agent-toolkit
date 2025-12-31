"""
generate_tickets.py - Development Tickets Generator

Part of Sait's Product Pipeline Toolkit

This script generates development tickets organized by milestones from a BRD and design spec
using BAML functions and configurable LLM providers (Gemini, Claude, OpenAI). Includes Q&A
session between PO, Designer, and Strategist, then generates validated tickets.

Usage:
    # Default (uses Gemini):
    python scripts/generate_tickets.py --output docs/product

    # With specific provider:
    python scripts/generate_tickets.py --output docs/ --provider claude

    # With feedback regeneration (auto-detected from docs/conversations/feedback/tickets-feedback.md):
    python scripts/generate_tickets.py --output docs/

Requirements:
    - prd.json (from generate_prd.py)
    - design-spec.json (from generate_design.py)
    - LLM API key in .env (GEMINI_API_KEY, ANTHROPIC_API_KEY, or OPENAI_API_KEY)
    - BAML client generated from baml_src/ schemas
"""

import argparse
import asyncio
import json
import sys
from pathlib import Path

from dotenv import load_dotenv
load_dotenv()

# Add toolkit directory to path
toolkit_dir = Path(__file__).parent.parent.resolve()
sys.path.insert(0, str(toolkit_dir))

from baml_client import b  # BAML client with functions
from baml_client.types import TicketSpec  # BAML-generated Pydantic class
from src.personas.loader import PersonaLoader
from src.baml.client_registry import BAMLClientRegistry
from src.llm.factory import LLMFactory
from src.pipeline.config import PipelineConfig
from src.io.markdown_writer import MarkdownWriter
from src.io.markdown_parser import MarkdownParser
from src.agents.po import POAgent
from src.agents.designer import DesignerAgent
from src.agents.strategist import StrategistAgent
from src.agents.conversation import ConversationOrchestrator

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
output_path.mkdir(parents=True, exist_ok=True)
print(f"✓ Output directory: {output_path}")

# Load BRD from project directory
prd_file = output_path / 'prd.json'
if not prd_file.exists():
    print(f"❌ Error: prd.json not found at {prd_file}")
    print("   Please run generate_prd.py first.")
    exit(1)

with open(prd_file) as f:
    prd = json.load(f)
print(f"✓ Loaded PRD from {prd_file}")

# Load design spec for more detailed context
design_file = output_path / 'design-spec.json'
if not design_file.exists():
    print(f"❌ Error: design-spec.json not found at {design_file}")
    print("   Please run generate_design.py first.")
    exit(1)

with open(design_file) as f:
    design_spec = json.load(f)
print(f"✓ Loaded design spec from {design_file}")

# Configure client registry for provider selection
api_params = {}
if args.provider:
    api_params['po_provider'] = args.provider
    print(f"✓ Using provider: {args.provider}")

registry = BAMLClientRegistry(api_params if api_params else None)
client_registry = registry.get_client_registry()

# Build BAML options
baml_options = {}
if client_registry:
    baml_options["client_registry"] = client_registry

# Load personas
personas_dir = toolkit_dir / 'personas'
persona_loader = PersonaLoader(personas_dir)
po_prompt = persona_loader.get_prompt('po')
designer_prompt = persona_loader.get_prompt('designer')
strategist_prompt = persona_loader.get_prompt('strategist')
print(f"✓ Loaded PO, designer, and strategist personas")

# Create LLM clients for Q&A session (Python agents stay in Python)
cli_override = {}
if args.provider:
    cli_override['provider'] = args.provider
if args.model:
    cli_override['model'] = args.model

po_llm = LLMFactory.from_config(
    pipeline_config.get_raw_config(),
    'po',
    cli_override if cli_override else None
)

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

# Run Q&A session: PO asks Designer and Strategist about BRD and Design
print("\n" + "="*60)
print("Q&A SESSION: Product Owner ↔ Designer & Strategist")
print("="*60)

po_agent = POAgent(
    name="Product Owner",
    persona_prompt=po_prompt,
    llm_client=po_llm
)

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
prd_text = json.dumps(prd, indent=2)
design_text = json.dumps(design_spec, indent=2)

qa_conversation = orchestrator.run_qa_session(
    questioner=po_agent,
    respondents=[
        (designer_agent, design_text),
        (strategist_agent, prd_text)
    ],
    session_name="tickets-qa",
    num_questions=5
)

print("="*60 + "\n")

# Check for feedback and incorporate if exists
feedback_file = output_path / 'conversations' / 'feedback' / 'tickets-feedback.md'
feedback = MarkdownParser.read_feedback(feedback_file)

async def generate_tickets_async():
    """Async wrapper for BAML Tickets generation"""
    if feedback:
        print(f"\n📝 Found feedback at {feedback_file}")
        print("🔄 Regenerating development tickets with feedback incorporated...\n")

        # Use BAML function for regeneration with feedback
        return await b.GenerateTicketsWithFeedback(
            prd=prd_text,
            design=design_text,
            qa_conversation=qa_conversation,
            feedback=feedback,
            persona=po_prompt,
            baml_options=baml_options
        )
    else:
        print("✓ No feedback found, generating development tickets...\n")

        # Use BAML function for initial generation
        return await b.GenerateTickets(
            prd=prd_text,
            design=design_text,
            qa_conversation=qa_conversation,
            persona=po_prompt,
            baml_options=baml_options
        )

try:
    # Run async BAML function
    ticket_spec = asyncio.run(generate_tickets_async())

except Exception as e:
    print(f"❌ Error generating tickets: {e}")
    exit(1)

print(f"Milestone: {ticket_spec.milestone}")
print(f"\nTickets ({len(ticket_spec.tickets)}):")
for i, ticket in enumerate(ticket_spec.tickets, 1):
    print(f"{i}. [{ticket.priority}] {ticket.title}")

# Save tickets as markdown (primary output format)
# MarkdownWriter.write_tickets expects a list of TicketSpec objects
tickets_md_output = output_path / 'development-tickets.md'
MarkdownWriter.write_tickets([ticket_spec], tickets_md_output)
print(f"\n✓ Development tickets saved to {tickets_md_output}")

# Also save as JSON for inter-script compatibility
tickets_json_output = output_path / 'development-tickets.json'
with open(tickets_json_output, "w") as f:
    try:
        f.write(ticket_spec.model_dump_json(indent=2))  # Pydantic v2+
    except AttributeError:
        f.write(ticket_spec.json(indent=2))  # Pydantic v1 fallback

print(f"✓ Development tickets (JSON) saved to {tickets_json_output}")
