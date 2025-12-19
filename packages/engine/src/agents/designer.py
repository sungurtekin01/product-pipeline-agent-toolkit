"""UX/UI Designer agent for design specifications and user experience"""

from src.agents.base_agent import BaseAgent


class DesignerAgent(BaseAgent):
    """UX/UI Designer agent

    Specializes in:
    - User experience design
    - UI component specifications
    - Wireframe and layout design
    - Design system consistency
    - Accessibility and usability

    Example usage:
        from src.personas.loader import PersonaLoader
        from src.llm.factory import LLMFactory

        # Load designer persona
        persona_loader = PersonaLoader(Path('personas'))
        designer_prompt = persona_loader.get_prompt('designer')

        # Create LLM client
        llm_client = LLMFactory.create('gemini', 'gemini-2.5-pro', 'GEMINI_API_KEY')

        # Create agent
        designer = DesignerAgent(
            name="UX Designer",
            persona_prompt=designer_prompt,
            llm_client=llm_client
        )

        # Generate questions about BRD
        questions = designer.generate_questions(brd_content, num_questions=5)

        # Ask for clarification
        answer = designer.ask("What are the accessibility requirements?", context=brd)
    """

    def __init__(self, name: str = "UX Designer", **kwargs):
        """Initialize the Designer agent

        Args:
            name: Agent name (default: "UX Designer")
            **kwargs: Additional arguments passed to BaseAgent (persona_prompt, llm_client)
        """
        super().__init__(name=name, **kwargs)
