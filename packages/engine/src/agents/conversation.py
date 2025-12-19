"""Conversation orchestrator for multi-agent Q&A sessions"""

from pathlib import Path
from typing import List, Tuple
from datetime import datetime

from src.agents.base_agent import BaseAgent


class ConversationOrchestrator:
    """Orchestrate Q&A conversations between multiple agents

    This class manages multi-agent conversations where one agent asks questions
    and one or more agents provide answers. Conversations are saved as markdown
    files for human review and future reference.

    Example usage:
        orchestrator = ConversationOrchestrator(output_dir=Path('docs/product'))

        # Designer asks questions to Strategist about BRD
        conversation = orchestrator.run_qa_session(
            questioner=designer,
            respondents=[(strategist, brd_content)],
            session_name="design-qa",
            num_questions=5
        )

        # PO asks questions to Designer and Strategist
        conversation = orchestrator.run_qa_session(
            questioner=po,
            respondents=[
                (designer, design_spec_content),
                (strategist, brd_content)
            ],
            session_name="tickets-qa",
            num_questions=5
        )
    """

    def __init__(self, output_dir: Path):
        """Initialize the conversation orchestrator

        Args:
            output_dir: Base output directory (conversations will be saved to output_dir/conversations/)
        """
        self.output_dir = output_dir
        self.conversations_dir = output_dir / 'conversations'
        self.conversations_dir.mkdir(parents=True, exist_ok=True)

    def run_qa_session(
        self,
        questioner: BaseAgent,
        respondents: List[Tuple[BaseAgent, str]],
        session_name: str,
        num_questions: int = 5
    ) -> str:
        """Run a Q&A session between agents

        Process:
        1. Questioner analyzes all respondent contexts and generates questions
        2. Each question is asked to all respondents
        3. Responses are collected and formatted
        4. Conversation is saved to markdown file
        5. Conversation text is returned for inclusion in subsequent prompts

        Args:
            questioner: Agent that will ask questions
            respondents: List of (agent, context) tuples
                        Each respondent will answer based on their context
            session_name: Name for the conversation file (e.g., "design-qa", "tickets-qa")
            num_questions: Number of questions to generate (default: 5)

        Returns:
            Complete conversation as formatted string

        Example:
            conversation = orchestrator.run_qa_session(
                questioner=designer,
                respondents=[(strategist, brd_content)],
                session_name="design-qa",
                num_questions=3
            )
        """
        # Combine all respondent contexts for question generation
        combined_context = self._combine_contexts(respondents)

        # Generate questions from questioner
        print(f"\n🤔 {questioner.name} is analyzing documents and generating questions...")
        questions = questioner.generate_questions(combined_context, num_questions=num_questions)
        print(f"✓ Generated {len(questions)} questions")

        # Build conversation
        conversation_parts = []
        conversation_parts.append(f"# Q&A Session: {questioner.name} ↔ {', '.join(r[0].name for r in respondents)}")
        conversation_parts.append(f"\n*Session: {session_name}*")
        conversation_parts.append(f"*Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}*\n")

        # Ask each question to all respondents
        for i, question in enumerate(questions, 1):
            print(f"\n  Q{i}: {question[:80]}{'...' if len(question) > 80 else ''}")
            conversation_parts.append(f"## Question {i}\n")
            conversation_parts.append(f"**{questioner.name} asks:**\n")
            conversation_parts.append(f"{question}\n")

            # Get answers from each respondent
            for respondent, context in respondents:
                print(f"    ↳ {respondent.name} is responding...")
                answer = respondent.ask(question, context=context)
                conversation_parts.append(f"**{respondent.name} responds:**\n")
                conversation_parts.append(f"{answer}\n")

        # Join conversation parts
        conversation_text = "\n".join(conversation_parts)

        # Save conversation to markdown file
        conversation_file = self.conversations_dir / f"{session_name}.md"
        with open(conversation_file, 'w', encoding='utf-8') as f:
            f.write(conversation_text)

        print(f"\n✓ Conversation saved to {conversation_file}")

        return conversation_text

    def _combine_contexts(self, respondents: List[Tuple[BaseAgent, str]]) -> str:
        """Combine contexts from multiple respondents

        Args:
            respondents: List of (agent, context) tuples

        Returns:
            Combined context string with agent attribution
        """
        combined = []
        for agent, context in respondents:
            combined.append(f"=== {agent.name} Context ===\n{context}\n")

        return "\n".join(combined)

    def load_conversation(self, session_name: str) -> str:
        """Load a saved conversation

        Args:
            session_name: Name of the conversation file (without .md extension)

        Returns:
            Conversation content, or empty string if file doesn't exist
        """
        conversation_file = self.conversations_dir / f"{session_name}.md"

        if not conversation_file.exists():
            return ""

        try:
            with open(conversation_file, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            print(f"Warning: Error reading conversation file {conversation_file}: {e}")
            return ""

    def list_conversations(self) -> List[Path]:
        """List all saved conversations

        Returns:
            List of conversation file paths
        """
        if not self.conversations_dir.exists():
            return []

        return sorted(self.conversations_dir.glob('*.md'))
