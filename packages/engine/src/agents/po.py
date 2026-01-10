"""Product Owner agent for development tickets and sprint planning"""

from src.agents.base_agent import BaseAgent


class POAgent(BaseAgent):
    """Product Owner agent

    Specializes in:
    - Breaking down requirements into tickets
    - Sprint and milestone planning
    - Acceptance criteria definition
    - Backlog prioritization
    - Developer task assignment
    - User story creation

    Example usage:
        from src.personas.loader import PersonaLoader
        from src.llm.factory import LLMFactory

        # Load PO persona
        persona_loader = PersonaLoader(Path('personas'))
        po_prompt = persona_loader.get_prompt('po')

        # Create LLM client
        llm_client = LLMFactory.create('gemini', 'gemini-2.5-pro', 'GEMINI_API_KEY')

        # Create agent
        po = POAgent(
            name="Product Owner",
            persona_prompt=po_prompt,
            llm_client=llm_client
        )

        # Generate questions about design spec
        questions = po.generate_questions(design_spec, num_questions=5)

        # Ask for clarification
        answer = po.ask(
            "What are the technical dependencies for this feature?",
            context=f"BRD: {brd}\\nDesign: {design_spec}"
        )
    """

    def __init__(self, name: str = "Product Owner", **kwargs):
        """Initialize the PO agent

        Args:
            name: Agent name (default: "Product Owner")
            **kwargs: Additional arguments passed to BaseAgent (persona_prompt, llm_client)
        """
        super().__init__(name=name, **kwargs)
