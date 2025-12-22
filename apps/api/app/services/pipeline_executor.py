"""
Pipeline Executor Service

Integrates with packages/engine to execute pipeline steps (BRD, Design, Tickets)
"""

import sys
import os
from pathlib import Path
from typing import Optional, Dict, Any
import json
import tempfile

# Add engine to Python path
ENGINE_PATH = Path(__file__).parent.parent.parent.parent.parent / "packages" / "engine"
sys.path.insert(0, str(ENGINE_PATH))

from baml_client import b  # BAML client with functions
from baml_client.types import BRD, DesignSpec, TicketSpec
from src.llm.factory import LLMFactory  # Still used for Q&A agents
from src.baml.client_registry import BAMLClientRegistry
from src.personas.loader import PersonaLoader
from src.agents.strategist import StrategistAgent
from src.agents.designer import DesignerAgent
from src.agents.po import POAgent
from src.agents.conversation import ConversationOrchestrator
from src.io.markdown_writer import MarkdownWriter
from src.io.markdown_parser import MarkdownParser


class PipelineExecutor:
    """Executes pipeline steps using the engine"""

    def __init__(
        self,
        vision: str,
        output_dir: str,
        llm_config: Optional[Dict[str, Any]] = None
    ):
        self.vision = vision
        self.output_dir = Path(output_dir)
        self.llm_config = llm_config or {}

        # Create output directory if it doesn't exist
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Load personas
        self.persona_loader = PersonaLoader(ENGINE_PATH / "personas")

    def _get_llm_client(self, agent_name: str, default_provider: str = "gemini"):
        """Get LLM client for an agent"""
        agent_config = self.llm_config.get(agent_name, {})
        provider = agent_config.get("provider", default_provider)
        model = agent_config.get("model")
        api_key_env = agent_config.get("api_key_env")

        # If no API key env specified, use provider default
        if not api_key_env:
            api_key_env_defaults = {
                'gemini': 'GEMINI_API_KEY',
                'claude': 'ANTHROPIC_API_KEY',
                'openai': 'OPENAI_API_KEY'
            }
            api_key_env = api_key_env_defaults.get(provider, 'GEMINI_API_KEY')

        # If no model specified, use provider default
        if not model:
            model_defaults = {
                'gemini': 'gemini-2.5-pro',
                'claude': 'claude-sonnet-4-5',
                'openai': 'gpt-4'
            }
            model = model_defaults.get(provider, 'gemini-2.5-pro')

        return LLMFactory.create(
            provider=provider,
            model=model,
            api_key_env=api_key_env
        )

    def _get_baml_options(self) -> Dict[str, Any]:
        """Get BAML options for provider selection via ClientRegistry"""
        api_params = {}

        # Map llm_config to ClientRegistry format
        for agent_name, config in self.llm_config.items():
            if "provider" in config:
                api_params[f"{agent_name}_provider"] = config["provider"]

        # Create registry and get client registry
        registry = BAMLClientRegistry(api_params if api_params else None)
        client_registry = registry.get_client_registry()

        # Return BAML options
        if client_registry:
            return {"client_registry": client_registry}
        return {}

    async def generate_brd(self, feedback: Optional[str] = None) -> Dict[str, Any]:
        """Generate Business Requirements Document using BAML"""
        try:
            # Load strategist persona
            strategist_prompt = self.persona_loader.get_prompt("strategist")

            # Get BAML options for provider selection
            baml_options = self._get_baml_options()

            # Generate BRD using BAML function
            if feedback:
                # Use BAML function for regeneration with feedback
                brd_response = await b.GenerateBRDWithFeedback(
                    vision=self.vision,
                    feedback=feedback,
                    persona=strategist_prompt,
                    baml_options=baml_options
                )
            else:
                # Use BAML function for initial generation
                brd_response = await b.GenerateBRD(
                    vision=self.vision,
                    persona=strategist_prompt,
                    baml_options=baml_options
                )

            # Convert to dict
            brd = brd_response.model_dump()

            # Write to markdown
            output_file = self.output_dir / "BRD.md"
            MarkdownWriter.write_brd(brd_response, output_file)

            # Also write JSON for compatibility
            json_file = self.output_dir / "brd.json"
            with open(json_file, "w") as f:
                json.dump(brd, f, indent=2)

            return {
                "status": "completed",
                "output_file": str(output_file),
                "json_file": str(json_file),
                "data": brd
            }

        except Exception as e:
            raise Exception(f"BRD generation failed: {str(e)}")

    async def generate_design(self, feedback: Optional[str] = None) -> Dict[str, Any]:
        """Generate Design Specification with Q&A using BAML"""
        try:
            # Load BRD
            brd_file = self.output_dir / "brd.json"
            if not brd_file.exists():
                raise Exception("BRD not found. Please generate BRD first.")

            with open(brd_file) as f:
                brd = json.load(f)

            # Load personas
            designer_prompt = self.persona_loader.get_prompt("designer")
            strategist_prompt = self.persona_loader.get_prompt("strategist")

            # Create LLM clients for Q&A session (Python orchestration)
            designer_llm = self._get_llm_client("designer")
            strategist_llm = self._get_llm_client("strategist")

            # Create agents
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

            # Run Q&A session (stays in Python for dynamic orchestration)
            orchestrator = ConversationOrchestrator(self.output_dir)
            brd_text = json.dumps(brd, indent=2)
            qa_conversation = orchestrator.run_qa_session(
                questioner=designer_agent,
                respondents=[(strategist_agent, brd_text)],
                session_name="design-qa",
                num_questions=5
            )

            # Get BAML options for provider selection
            baml_options = self._get_baml_options()

            # Refine BRD using BAML function (type-safe)
            refined_brd = await b.RefineBRD(
                original_brd=brd_text,
                qa_conversation=qa_conversation,
                persona=strategist_prompt,
                baml_options=baml_options
            )

            # Save refined BRD (overwrite original)
            refined_output_file = self.output_dir / "BRD.md"
            MarkdownWriter.write_brd(refined_brd, refined_output_file)

            refined_json_file = self.output_dir / "brd.json"
            with open(refined_json_file, "w") as f:
                json.dump(refined_brd.model_dump(), f, indent=2)

            # Update brd_text to use refined version
            brd_text = json.dumps(refined_brd.model_dump(), indent=2)

            # Generate design spec using BAML function (type-safe)
            if feedback:
                design_response = await b.GenerateDesignWithFeedback(
                    brd=brd_text,
                    qa_conversation=qa_conversation,
                    feedback=feedback,
                    persona=designer_prompt,
                    baml_options=baml_options
                )
            else:
                design_response = await b.GenerateDesign(
                    brd=brd_text,
                    qa_conversation=qa_conversation,
                    persona=designer_prompt,
                    baml_options=baml_options
                )

            # Convert to dict
            design = design_response.model_dump()

            # Write to markdown
            output_file = self.output_dir / "design-spec.md"
            MarkdownWriter.write_design_spec(design_response, output_file)

            # Also write JSON
            json_file = self.output_dir / "design-spec.json"
            with open(json_file, "w") as f:
                json.dump(design, f, indent=2)

            return {
                "status": "completed",
                "output_file": str(output_file),
                "json_file": str(json_file),
                "qa_conversation": str(self.output_dir / "conversations" / "design-qa.md"),
                "data": design
            }

        except Exception as e:
            raise Exception(f"Design generation failed: {str(e)}")

    async def generate_tickets(self, feedback: Optional[str] = None) -> Dict[str, Any]:
        """Generate Development Tickets with Q&A using BAML"""
        try:
            # Load BRD and Design
            brd_file = self.output_dir / "brd.json"
            design_file = self.output_dir / "design-spec.json"

            if not brd_file.exists() or not design_file.exists():
                raise Exception("BRD and Design Spec required. Please generate them first.")

            with open(brd_file) as f:
                brd = json.load(f)

            with open(design_file) as f:
                design = json.load(f)

            # Load personas
            po_prompt = self.persona_loader.get_prompt("po")
            designer_prompt = self.persona_loader.get_prompt("designer")
            strategist_prompt = self.persona_loader.get_prompt("strategist")

            # Create LLM clients for Q&A session (Python orchestration)
            po_llm = self._get_llm_client("po")
            designer_llm = self._get_llm_client("designer")
            strategist_llm = self._get_llm_client("strategist")

            # Create agents
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

            # Run Q&A session (stays in Python for dynamic orchestration)
            orchestrator = ConversationOrchestrator(self.output_dir)
            design_text = json.dumps(design, indent=2)
            brd_text = json.dumps(brd, indent=2)

            qa_conversation = orchestrator.run_qa_session(
                questioner=po_agent,
                respondents=[
                    (designer_agent, design_text),
                    (strategist_agent, brd_text)
                ],
                session_name="tickets-qa",
                num_questions=5
            )

            # Get BAML options for provider selection
            baml_options = self._get_baml_options()

            # Generate tickets using BAML function (type-safe)
            if feedback:
                tickets_response = await b.GenerateTicketsWithFeedback(
                    brd=brd_text,
                    design=design_text,
                    qa_conversation=qa_conversation,
                    feedback=feedback,
                    persona=po_prompt,
                    baml_options=baml_options
                )
            else:
                tickets_response = await b.GenerateTickets(
                    brd=brd_text,
                    design=design_text,
                    qa_conversation=qa_conversation,
                    persona=po_prompt,
                    baml_options=baml_options
                )

            # Convert to dict
            tickets = tickets_response.model_dump()

            # Write to markdown
            output_file = self.output_dir / "development-tickets.md"
            MarkdownWriter.write_tickets([tickets_response], output_file)

            # Also write JSON
            json_file = self.output_dir / "development-tickets.json"
            with open(json_file, "w") as f:
                json.dump(tickets, f, indent=2)

            return {
                "status": "completed",
                "output_file": str(output_file),
                "json_file": str(json_file),
                "qa_conversation": str(self.output_dir / "conversations" / "tickets-qa.md"),
                "data": tickets
            }

        except Exception as e:
            raise Exception(f"Tickets generation failed: {str(e)}")
