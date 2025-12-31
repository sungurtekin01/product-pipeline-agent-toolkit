"""
Pipeline Executor Service

Integrates with packages/engine to execute pipeline steps (PRD, Design, Tickets)
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
from baml_client.types import PRD, DesignSpec, TicketSpec
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
        llm_config: Optional[Dict[str, Any]] = None,
        api_keys: Optional[Dict[str, str]] = None,
        persona_config: Optional[Dict[str, str]] = None
    ):
        self.vision = vision
        self.output_dir = Path(output_dir)
        self.llm_config = llm_config or {}
        self.api_keys = api_keys or {}
        self.persona_config = persona_config or {}

        # Default persona mappings
        self.default_personas = {
            "prd": "strategist",
            "design": "designer",
            "tickets": "po"
        }

        # Create output directory if it doesn't exist
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Load personas
        self.persona_loader = PersonaLoader(ENGINE_PATH / "personas")

    def _get_llm_client(self, agent_name: str, default_provider: str = "gemini"):
        """Get LLM client for an agent"""
        agent_config = self.llm_config.get(agent_name, {})
        provider = agent_config.get("provider", default_provider)
        model = agent_config.get("model")

        # If no model specified, use provider default
        if not model:
            model_defaults = {
                'gemini': 'gemini-2.5-pro',
                'claude': 'claude-sonnet-4-5',
                'openai': 'gpt-4'
            }
            model = model_defaults.get(provider, 'gemini-2.5-pro')

        # Get API key from request or fall back to environment
        api_key = None
        api_key_env = None

        if self.api_keys:
            # Map provider to API key from request
            provider_key_map = {
                'gemini': 'gemini',
                'claude': 'anthropic',
                'openai': 'openai'
            }
            key_name = provider_key_map.get(provider)
            if key_name and key_name in self.api_keys:
                api_key = self.api_keys[key_name]

        # If no API key from request, fall back to environment variable
        if not api_key:
            api_key_env_defaults = {
                'gemini': 'GEMINI_API_KEY',
                'claude': 'ANTHROPIC_API_KEY',
                'openai': 'OPENAI_API_KEY'
            }
            api_key_env = agent_config.get("api_key_env") or api_key_env_defaults.get(provider, 'GEMINI_API_KEY')

        return LLMFactory.create(
            provider=provider,
            model=model,
            api_key=api_key,
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

    def _get_persona_for_step(self, step: str) -> str:
        """
        Get persona for a given pipeline step

        Args:
            step: Pipeline step ("prd", "design", "tickets")

        Returns:
            Persona ID to use for this step

        Priority:
            1. User-configured persona (from persona_config)
            2. Default persona for step
        """
        # Check if persona specified in config
        if step in self.persona_config:
            return self.persona_config[step]

        # Fall back to default
        return self.default_personas.get(step, "strategist")

    async def generate_prd(self, feedback: Optional[str] = None) -> Dict[str, Any]:
        """Generate Product Requirements Document using BAML"""
        try:
            # Load strategist persona (use dynamic selection)
            persona_id = self._get_persona_for_step("prd")
            strategist_prompt = self.persona_loader.get_prompt(persona_id)

            # Get BAML options for provider selection
            baml_options = self._get_baml_options()

            # Generate PRD using BAML function
            if feedback:
                # Use BAML function for regeneration with feedback
                prd_response = await b.GeneratePRDWithFeedback(
                    vision=self.vision,
                    feedback=feedback,
                    persona=strategist_prompt,
                    baml_options=baml_options
                )
            else:
                # Use BAML function for initial generation
                prd_response = await b.GeneratePRD(
                    vision=self.vision,
                    persona=strategist_prompt,
                    baml_options=baml_options
                )

            # Convert to dict
            prd = prd_response.model_dump()

            # Write to markdown
            output_file = self.output_dir / "PRD.md"
            MarkdownWriter.write_prd(prd_response, output_file)

            # Also write JSON for compatibility
            json_file = self.output_dir / "prd.json"
            with open(json_file, "w") as f:
                json.dump(prd, f, indent=2)

            return {
                "status": "completed",
                "output_file": str(output_file),
                "json_file": str(json_file),
                "data": prd
            }

        except Exception as e:
            raise Exception(f"PRD generation failed: {str(e)}")

    async def generate_design(self, feedback: Optional[str] = None) -> Dict[str, Any]:
        """Generate Design Specification with Q&A using BAML"""
        try:
            # Load PRD
            prd_file = self.output_dir / "prd.json"
            if not prd_file.exists():
                raise Exception("PRD not found. Please generate PRD first.")

            with open(prd_file) as f:
                prd = json.load(f)

            # Load personas (use dynamic selection)
            designer_persona_id = self._get_persona_for_step("design")
            strategist_persona_id = self._get_persona_for_step("prd")
            designer_prompt = self.persona_loader.get_prompt(designer_persona_id)
            strategist_prompt = self.persona_loader.get_prompt(strategist_persona_id)

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
            prd_text = json.dumps(prd, indent=2)
            qa_conversation = orchestrator.run_qa_session(
                questioner=designer_agent,
                respondents=[(strategist_agent, prd_text)],
                session_name="design-qa",
                num_questions=5
            )

            # Get BAML options for provider selection
            baml_options = self._get_baml_options()

            # Refine PRD using BAML function (type-safe)
            refined_prd = await b.RefinePRD(
                original_prd=prd_text,
                qa_conversation=qa_conversation,
                persona=strategist_prompt,
                baml_options=baml_options
            )

            # Save refined PRD (overwrite original)
            refined_output_file = self.output_dir / "PRD.md"
            MarkdownWriter.write_prd(refined_prd, refined_output_file)

            refined_json_file = self.output_dir / "prd.json"
            with open(refined_json_file, "w") as f:
                json.dump(refined_prd.model_dump(), f, indent=2)

            # Update prd_text to use refined version
            prd_text = json.dumps(refined_prd.model_dump(), indent=2)

            # Generate design spec using BAML function (type-safe)
            if feedback:
                design_response = await b.GenerateDesignWithFeedback(
                    prd=prd_text,
                    qa_conversation=qa_conversation,
                    feedback=feedback,
                    persona=designer_prompt,
                    baml_options=baml_options
                )
            else:
                design_response = await b.GenerateDesign(
                    prd=prd_text,
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
            # Load PRD and Design
            prd_file = self.output_dir / "prd.json"
            design_file = self.output_dir / "design-spec.json"

            if not prd_file.exists() or not design_file.exists():
                raise Exception("PRD and Design Spec required. Please generate them first.")

            with open(prd_file) as f:
                prd = json.load(f)

            with open(design_file) as f:
                design = json.load(f)

            # Load personas (use dynamic selection)
            po_persona_id = self._get_persona_for_step("tickets")
            designer_persona_id = self._get_persona_for_step("design")
            strategist_persona_id = self._get_persona_for_step("prd")
            po_prompt = self.persona_loader.get_prompt(po_persona_id)
            designer_prompt = self.persona_loader.get_prompt(designer_persona_id)
            strategist_prompt = self.persona_loader.get_prompt(strategist_persona_id)

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
            prd_text = json.dumps(prd, indent=2)

            qa_conversation = orchestrator.run_qa_session(
                questioner=po_agent,
                respondents=[
                    (designer_agent, design_text),
                    (strategist_agent, prd_text)
                ],
                session_name="tickets-qa",
                num_questions=5
            )

            # Get BAML options for provider selection
            baml_options = self._get_baml_options()

            # Generate tickets using BAML function (type-safe)
            if feedback:
                tickets_response = await b.GenerateTicketsWithFeedback(
                    prd=prd_text,
                    design=design_text,
                    qa_conversation=qa_conversation,
                    feedback=feedback,
                    persona=po_prompt,
                    baml_options=baml_options
                )
            else:
                tickets_response = await b.GenerateTickets(
                    prd=prd_text,
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
