"""Pipeline configuration management with CLI override support"""

import json
from pathlib import Path
from typing import Dict, Any, Optional


class PipelineConfig:
    """Load and manage product.config.json with CLI overrides

    This class provides a unified interface for accessing project configuration,
    with support for CLI argument overrides and sensible defaults.

    Example usage:
        config = PipelineConfig(Path('/path/to/project'))
        vision = config.get_vision(cli_override="Custom vision")
        output_dir = config.get_output_dir()
        llm_config = config.get_llm_config('strategist')
    """

    def __init__(self, project_path: Path):
        """Initialize PipelineConfig

        Args:
            project_path: Path to project directory containing product.config.json
        """
        self.project_path = project_path.resolve()
        self.config_path = self.project_path / 'product.config.json'
        self.config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """Load product.config.json if it exists

        Returns:
            Dictionary containing configuration, or empty dict if file doesn't exist
        """
        if not self.config_path.exists():
            return {}

        try:
            with open(self.config_path, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            raise ValueError(
                f"Invalid JSON in {self.config_path}: {e}"
            )

    def get_vision(self, cli_override: Optional[str] = None) -> str:
        """Get product vision with CLI override support

        Priority: CLI > config > error

        Args:
            cli_override: Vision string from command-line argument

        Returns:
            Product vision string

        Raises:
            ValueError: If vision not provided via CLI or config
        """
        if cli_override:
            return cli_override

        vision = self.config.get('vision')
        if not vision:
            raise ValueError(
                "Product vision not found. Provide via:\n"
                "  1. CLI: --vision 'Your product vision'\n"
                "  2. Config: Add 'vision' field to product.config.json"
            )

        return vision

    def get_output_dir(self, cli_override: Optional[str] = None) -> Path:
        """Get output directory with CLI override support

        Priority: CLI > config > default ('.')

        Args:
            cli_override: Output directory from command-line argument

        Returns:
            Resolved Path object for output directory
        """
        output_str = cli_override or self.config.get('output_dir', '.')
        return self.project_path / output_str

    def get_llm_config(self, agent_name: str) -> Dict[str, Any]:
        """Get LLM configuration for a specific agent

        Returns the LLM configuration for the specified agent from
        product.config.json. Returns empty dict if no config found.

        Expected config structure:
        {
          "llm": {
            "strategist": {
              "provider": "claude",
              "model": "claude-opus-4-5",
              "api_key_env": "ANTHROPIC_API_KEY"
            },
            "designer": {
              "provider": "gemini",
              "model": "gemini-2.5-pro",
              "api_key_env": "GEMINI_API_KEY"
            }
          }
        }

        Args:
            agent_name: Name of the agent (e.g., 'strategist', 'designer', 'po')

        Returns:
            Dictionary with provider, model, and api_key_env fields,
            or empty dict if agent has no specific config
        """
        return self.config.get('llm', {}).get(agent_name, {})

    def has_config(self) -> bool:
        """Check if product.config.json exists

        Returns:
            True if config file exists and was loaded, False otherwise
        """
        return self.config_path.exists()

    def get_raw_config(self) -> Dict[str, Any]:
        """Get the raw configuration dictionary

        Returns:
            Complete configuration dictionary
        """
        return self.config
