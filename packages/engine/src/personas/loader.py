"""Unified persona loading system for consistent persona management"""

from pathlib import Path
from typing import Dict, Any
import toml


class PersonaLoader:
    """Load and manage persona TOML files

    This class provides a unified interface for loading personas from TOML files,
    ensuring consistent persona access across all generation scripts.

    Example usage:
        loader = PersonaLoader(Path('personas'))
        strategist = loader.load('strategist')
        prompt = loader.get_prompt('strategist')
    """

    def __init__(self, personas_dir: Path):
        """Initialize PersonaLoader

        Args:
            personas_dir: Path to directory containing persona TOML files
        """
        self.personas_dir = personas_dir

    def load(self, persona_name: str) -> Dict[str, Any]:
        """Load persona TOML file

        Args:
            persona_name: Name of persona (without .toml extension)
                         Examples: 'strategist', 'designer', 'po', 'rn_designer'

        Returns:
            Dictionary containing persona configuration with keys:
            - 'description': Brief description of persona role
            - 'prompt': Full persona prompt/instructions

        Raises:
            FileNotFoundError: If persona file doesn't exist
            toml.TomlDecodeError: If TOML file is malformed
        """
        persona_file = self.personas_dir / f"{persona_name}.toml"

        if not persona_file.exists():
            raise FileNotFoundError(
                f"Persona not found: {persona_file}\n"
                f"Available personas: {self._list_available_personas()}"
            )

        with open(persona_file, 'r') as f:
            return toml.load(f)

    def get_prompt(self, persona_name: str) -> str:
        """Get the prompt field from persona

        Convenience method to extract just the prompt string from a persona.

        Args:
            persona_name: Name of persona

        Returns:
            Persona prompt string ready to use as system prompt

        Raises:
            FileNotFoundError: If persona file doesn't exist
            KeyError: If persona file missing 'prompt' field
        """
        persona = self.load(persona_name)

        if 'prompt' not in persona:
            raise KeyError(
                f"Persona '{persona_name}' missing required 'prompt' field"
            )

        return persona['prompt']

    def get_description(self, persona_name: str) -> str:
        """Get the description field from persona

        Args:
            persona_name: Name of persona

        Returns:
            Persona description string

        Raises:
            FileNotFoundError: If persona file doesn't exist
        """
        persona = self.load(persona_name)
        return persona.get('description', '')

    def _list_available_personas(self) -> str:
        """List available persona files

        Returns:
            Comma-separated list of available persona names
        """
        if not self.personas_dir.exists():
            return "None (personas directory not found)"

        personas = [
            p.stem for p in self.personas_dir.glob('*.toml')
        ]
        return ', '.join(sorted(personas)) if personas else 'None'

    def list_personas(self) -> list[str]:
        """List available persona names

        Returns:
            List of persona names (without .toml extension)
        """
        if not self.personas_dir.exists():
            return []

        return sorted([p.stem for p in self.personas_dir.glob('*.toml')])
