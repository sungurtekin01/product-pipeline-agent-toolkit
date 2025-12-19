"""Product Strategist agent for business requirements and product vision"""

from src.agents.base_agent import BaseAgent


class StrategistAgent(BaseAgent):
    """Product Strategist agent

    Specializes in:
    - Business requirements analysis
    - Product vision clarification
    - Strategic objectives definition
    - Market and user research insights

    Example usage:
        from src.personas.loader import PersonaLoader
        from src.llm.factory import LLMFactory

        # Load strategist persona
        persona_loader = PersonaLoader(Path('personas'))
        strategist_prompt = persona_loader.get_prompt('strategist')

        # Create LLM client
        llm_client = LLMFactory.create('gemini', 'gemini-2.5-pro', 'GEMINI_API_KEY')

        # Create agent
        strategist = StrategistAgent(
            name="Product Strategist",
            persona_prompt=strategist_prompt,
            llm_client=llm_client
        )

        # Ask questions
        answer = strategist.ask("What are the key business objectives?", context=brd)
    """

    def __init__(self, name: str = "Product Strategist", **kwargs):
        """Initialize the Strategist agent

        Args:
            name: Agent name (default: "Product Strategist")
            **kwargs: Additional arguments passed to BaseAgent (persona_prompt, llm_client)
        """
        super().__init__(name=name, **kwargs)
