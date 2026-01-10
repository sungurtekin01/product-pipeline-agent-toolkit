"""Base agent class for multi-agent Q&A conversations"""

from typing import List
from src.llm.base import BaseLLMClient


class BaseAgent:
    """Base class for AI agents with Q&A capabilities

    This class provides the foundation for specialized agents (Strategist, Designer, PO)
    that can participate in multi-agent conversations, ask questions, and provide answers.

    Example usage:
        agent = BaseAgent(
            name="Product Strategist",
            persona_prompt=strategist_persona,
            llm_client=llm_client
        )

        # Generate questions about a document
        questions = agent.generate_questions(brd_content, num_questions=3)

        # Answer a specific question
        answer = agent.ask("What is the target audience?", context=brd_content)
    """

    def __init__(self, name: str, persona_prompt: str, llm_client: BaseLLMClient):
        """Initialize the agent

        Args:
            name: Agent name (e.g., "Product Strategist", "UX Designer")
            persona_prompt: System prompt defining agent's role and expertise
            llm_client: LLM client for generating responses
        """
        self.name = name
        self.persona_prompt = persona_prompt
        self.llm = llm_client

    def ask(self, question: str, context: str = "") -> str:
        """Ask the agent a question with optional context

        The agent will respond based on its persona and the provided context.

        Args:
            question: Question to ask the agent
            context: Optional context to inform the answer (e.g., BRD content, design spec)

        Returns:
            Agent's response to the question

        Example:
            answer = agent.ask(
                "What are the primary user demographics?",
                context="BRD: {...}"
            )
        """
        user_prompt = f"Question: {question}"
        if context:
            user_prompt = f"Context:\n{context}\n\n{user_prompt}"

        response = self.llm.generate(user_prompt, system_prompt=self.persona_prompt)
        return response.strip()

    def generate_questions(self, document: str, num_questions: int = 5) -> List[str]:
        """Generate clarifying questions about a document

        The agent analyzes the document and generates questions to clarify
        requirements, fill gaps, or gather additional information.

        Args:
            document: Document content to analyze (e.g., BRD, design spec)
            num_questions: Number of questions to generate (default: 5)

        Returns:
            List of clarifying questions

        Example:
            brd_content = "Title: My App\\nDescription: ..."
            questions = designer.generate_questions(brd_content, num_questions=3)
            # Returns: ["What is the target platform?", "Are there accessibility requirements?", ...]
        """
        user_prompt = (
            f"Please analyze the following document and generate {num_questions} "
            "clarifying questions that would help you better understand the requirements "
            "and create a more comprehensive output.\n\n"
            "Respond with ONLY a numbered list of questions, one per line.\n\n"
            f"Document:\n{document}"
        )

        response = self.llm.generate(user_prompt, system_prompt=self.persona_prompt)

        # Parse the response to extract questions
        questions = self._parse_questions(response)

        # Return up to num_questions
        return questions[:num_questions]

    def _parse_questions(self, response: str) -> List[str]:
        """Parse questions from LLM response

        Handles various response formats:
        - Numbered lists: "1. Question?"
        - Bullet points: "- Question?"
        - Plain lines: "Question?"

        Args:
            response: Raw LLM response containing questions

        Returns:
            List of cleaned questions
        """
        questions = []
        lines = response.strip().split('\n')

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Remove common prefixes
            # Numbered: "1. ", "1) ", "Q1: "
            if line[0].isdigit():
                # Find the first non-digit, non-punctuation character
                for i, char in enumerate(line):
                    if char.isalpha() or char == '"' or char == "'":
                        line = line[i:]
                        break

            # Bullets: "- ", "* ", "• "
            elif line.startswith(('-', '*', '•')):
                line = line[1:].strip()

            # Remove "Question:" prefix if present
            if line.lower().startswith('question:'):
                line = line[9:].strip()

            # Only add non-empty lines
            if line:
                questions.append(line)

        return questions

    def __repr__(self):
        """String representation of the agent"""
        return f"<{self.__class__.__name__}: {self.name}>"
