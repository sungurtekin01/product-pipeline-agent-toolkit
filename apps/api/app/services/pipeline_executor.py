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

from src.llm.factory import LLMFactory
from src.personas.loader import PersonaLoader
from src.agents.strategist import StrategistAgent
from src.agents.designer import DesignerAgent
from src.agents.po import POAgent
from src.agents.conversation import ConversationOrchestrator
from src.io.markdown_writer import MarkdownWriter
from src.io.markdown_parser import MarkdownParser
from baml_client import b


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

        return LLMFactory.create(
            provider=provider,
            model=model,
            api_key_env=api_key_env
        )

    async def generate_brd(self, feedback: Optional[str] = None) -> Dict[str, Any]:
        """Generate Business Requirements Document"""
        try:
            # Load strategist persona
            strategist_prompt = self.persona_loader.get_prompt("strategist")

            # Create LLM client
            llm_client = self._get_llm_client("strategist")

            # Build prompt
            if feedback:
                user_prompt = (
                    f"Product Vision:\n{self.vision}\n\n"
                    f"Previous BRD Feedback:\n{feedback}\n\n"
                    "Please regenerate the BRD incorporating the feedback above."
                )
            else:
                user_prompt = f"Product Vision:\n{self.vision}"

            # Generate BRD using BAML
            brd_response = await b.GenerateBRD(
                persona=strategist_prompt,
                user_input=user_prompt
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
        """Generate Design Specification with Q&A"""
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

            # Create LLM clients
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

            # Run Q&A session
            orchestrator = ConversationOrchestrator(self.output_dir)
            brd_text = json.dumps(brd, indent=2)
            qa_conversation = orchestrator.run_qa_session(
                questioner=designer_agent,
                respondents=[(strategist_agent, brd_text)],
                session_name="design-qa",
                num_questions=5
            )

            # Build prompt
            schema_hint = "Generate a comprehensive design specification in JSON format matching the DesignSpec schema."

            if feedback:
                user_prompt = (
                    f"{schema_hint}\n\n"
                    f"Here is the validated BRD:\n{brd_text}\n\n"
                    f"Additional context from Q&A session with Product Strategist:\n{qa_conversation}\n\n"
                    f"Previous Design Feedback:\n{feedback}\n\n"
                    "Please regenerate the design spec incorporating the feedback above."
                )
            else:
                user_prompt = (
                    f"{schema_hint}\n\n"
                    f"Here is the validated BRD:\n{brd_text}\n\n"
                    f"Additional context from Q&A session with Product Strategist:\n{qa_conversation}"
                )

            # Generate design spec using BAML
            design_response = await b.GenerateDesignSpec(
                persona=designer_prompt,
                brd=json.dumps(brd),
                user_input=user_prompt
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
        """Generate Development Tickets with Q&A"""
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

            # Create LLM clients
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

            # Run Q&A session
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

            # Build prompt
            schema_hint = "Generate development tickets in JSON format matching the TicketSpec schema."

            if feedback:
                user_prompt = (
                    f"{schema_hint}\n\n"
                    f"BRD:\n{brd_text}\n\n"
                    f"Design Spec:\n{design_text}\n\n"
                    f"Additional context from Q&A:\n{qa_conversation}\n\n"
                    f"Previous Tickets Feedback:\n{feedback}\n\n"
                    "Please regenerate the tickets incorporating the feedback above."
                )
            else:
                user_prompt = (
                    f"{schema_hint}\n\n"
                    f"BRD:\n{brd_text}\n\n"
                    f"Design Spec:\n{design_text}\n\n"
                    f"Additional context from Q&A:\n{qa_conversation}"
                )

            # Generate tickets using BAML
            tickets_response = await b.GenerateDevelopmentTickets(
                persona=po_prompt,
                brd=json.dumps(brd),
                design_spec=json.dumps(design),
                user_input=user_prompt
            )

            # Convert to dict
            tickets = tickets_response.model_dump()

            # Write to markdown
            output_file = self.output_dir / "development-tickets.md"
            MarkdownWriter.write_tickets(tickets_response, output_file)

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
