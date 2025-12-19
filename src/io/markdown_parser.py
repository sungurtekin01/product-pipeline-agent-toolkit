"""Markdown parser for reading feedback and conversation files"""

from pathlib import Path
from typing import Optional


class MarkdownParser:
    """Parse markdown files for feedback and conversations

    This class provides static methods to read feedback and Q&A conversation
    files from markdown format.

    Example usage:
        feedback = MarkdownParser.read_feedback(Path('docs/feedback/brd-feedback.md'))
        if feedback:
            print(f"Incorporating feedback: {feedback}")
    """

    @staticmethod
    def read_feedback(feedback_file: Path) -> Optional[str]:
        """Read feedback from markdown file

        Args:
            feedback_file: Path to feedback markdown file

        Returns:
            Feedback content as string, or None if file doesn't exist

        Example feedback file format:
            # Feedback on BRD

            ## Requested Changes
            - Add more detail about user authentication
            - Clarify the target audience

            ## Additional Notes
            Consider adding a section on data privacy requirements.
        """
        if not feedback_file.exists():
            return None

        try:
            with open(feedback_file, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                return content if content else None
        except Exception as e:
            print(f"Warning: Error reading feedback file {feedback_file}: {e}")
            return None

    @staticmethod
    def read_conversation(conversation_file: Path) -> Optional[str]:
        """Read Q&A conversation from markdown file

        Args:
            conversation_file: Path to conversation markdown file

        Returns:
            Conversation content as string, or None if file doesn't exist

        Example conversation file format:
            # Q&A Session: Designer ↔ Strategist

            ## Question 1
            **Designer asks Strategist:**
            What is the primary user demographic?

            **Strategist responds:**
            The primary users are professionals aged 25-45...

            ## Question 2
            **Designer asks Strategist:**
            Are there any accessibility requirements?

            **Strategist responds:**
            Yes, the app should meet WCAG 2.1 AA standards...
        """
        if not conversation_file.exists():
            return None

        try:
            with open(conversation_file, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                return content if content else None
        except Exception as e:
            print(f"Warning: Error reading conversation file {conversation_file}: {e}")
            return None

    @staticmethod
    def list_feedback_files(feedback_dir: Path) -> list[Path]:
        """List all feedback markdown files in a directory

        Args:
            feedback_dir: Path to feedback directory

        Returns:
            List of feedback file paths
        """
        if not feedback_dir.exists():
            return []

        try:
            return sorted(feedback_dir.glob('*-feedback.md'))
        except Exception as e:
            print(f"Warning: Error listing feedback files in {feedback_dir}: {e}")
            return []

    @staticmethod
    def list_conversation_files(conversations_dir: Path) -> list[Path]:
        """List all conversation markdown files in a directory

        Args:
            conversations_dir: Path to conversations directory

        Returns:
            List of conversation file paths
        """
        if not conversations_dir.exists():
            return []

        try:
            # Match files like: design-qa.md, tickets-qa.md
            return sorted(conversations_dir.glob('*-qa.md'))
        except Exception as e:
            print(f"Warning: Error listing conversation files in {conversations_dir}: {e}")
            return []
