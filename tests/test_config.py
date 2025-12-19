"""Unit tests for pipeline configuration management"""

import json
import pytest
from pathlib import Path
from tempfile import TemporaryDirectory

from src.pipeline.config import PipelineConfig


class TestPipelineConfig:
    """Test PipelineConfig class"""

    def test_load_valid_config(self):
        """Test loading valid product.config.json"""
        with TemporaryDirectory() as tmpdir:
            project_path = Path(tmpdir)
            config_file = project_path / 'product.config.json'

            # Create config file
            config_data = {
                'vision': 'Test product vision',
                'output_dir': 'docs/product',
                'llm': {
                    'strategist': {
                        'provider': 'claude',
                        'model': 'claude-opus-4-5',
                        'api_key_env': 'ANTHROPIC_API_KEY'
                    }
                }
            }
            with open(config_file, 'w') as f:
                json.dump(config_data, f)

            # Load config
            config = PipelineConfig(project_path)

            assert config.has_config()
            assert config.get_raw_config() == config_data

    def test_load_missing_config(self):
        """Test handling missing config file"""
        with TemporaryDirectory() as tmpdir:
            project_path = Path(tmpdir)

            config = PipelineConfig(project_path)

            assert not config.has_config()
            assert config.get_raw_config() == {}

    def test_load_invalid_json(self):
        """Test handling malformed JSON"""
        with TemporaryDirectory() as tmpdir:
            project_path = Path(tmpdir)
            config_file = project_path / 'product.config.json'

            # Create invalid JSON file
            with open(config_file, 'w') as f:
                f.write('{ invalid json }')

            with pytest.raises(ValueError, match="Invalid JSON"):
                PipelineConfig(project_path)

    def test_get_vision_from_config(self):
        """Test getting vision from config"""
        with TemporaryDirectory() as tmpdir:
            project_path = Path(tmpdir)
            config_file = project_path / 'product.config.json'

            config_data = {'vision': 'Build an amazing app'}
            with open(config_file, 'w') as f:
                json.dump(config_data, f)

            config = PipelineConfig(project_path)
            vision = config.get_vision()

            assert vision == 'Build an amazing app'

    def test_get_vision_cli_override(self):
        """Test CLI override takes precedence over config"""
        with TemporaryDirectory() as tmpdir:
            project_path = Path(tmpdir)
            config_file = project_path / 'product.config.json'

            config_data = {'vision': 'Config vision'}
            with open(config_file, 'w') as f:
                json.dump(config_data, f)

            config = PipelineConfig(project_path)
            vision = config.get_vision(cli_override='CLI vision')

            assert vision == 'CLI vision'

    def test_get_vision_missing_raises_error(self):
        """Test error when vision not provided"""
        with TemporaryDirectory() as tmpdir:
            project_path = Path(tmpdir)

            config = PipelineConfig(project_path)

            with pytest.raises(ValueError, match="Product vision not found"):
                config.get_vision()

    def test_get_output_dir_from_config(self):
        """Test getting output directory from config"""
        with TemporaryDirectory() as tmpdir:
            project_path = Path(tmpdir)
            config_file = project_path / 'product.config.json'

            config_data = {'output_dir': 'docs/product'}
            with open(config_file, 'w') as f:
                json.dump(config_data, f)

            config = PipelineConfig(project_path)
            output_dir = config.get_output_dir()

            expected = project_path / 'docs/product'
            assert output_dir == expected

    def test_get_output_dir_default(self):
        """Test default output directory"""
        with TemporaryDirectory() as tmpdir:
            project_path = Path(tmpdir)

            config = PipelineConfig(project_path)
            output_dir = config.get_output_dir()

            assert output_dir == project_path / '.'

    def test_get_output_dir_cli_override(self):
        """Test CLI override for output directory"""
        with TemporaryDirectory() as tmpdir:
            project_path = Path(tmpdir)
            config_file = project_path / 'product.config.json'

            config_data = {'output_dir': 'docs/product'}
            with open(config_file, 'w') as f:
                json.dump(config_data, f)

            config = PipelineConfig(project_path)
            output_dir = config.get_output_dir(cli_override='custom/output')

            expected = project_path / 'custom/output'
            assert output_dir == expected

    def test_get_llm_config_existing_agent(self):
        """Test getting LLM config for existing agent"""
        with TemporaryDirectory() as tmpdir:
            project_path = Path(tmpdir)
            config_file = project_path / 'product.config.json'

            config_data = {
                'llm': {
                    'strategist': {
                        'provider': 'claude',
                        'model': 'claude-opus-4-5',
                        'api_key_env': 'ANTHROPIC_API_KEY'
                    },
                    'designer': {
                        'provider': 'gemini',
                        'model': 'gemini-2.5-pro',
                        'api_key_env': 'GEMINI_API_KEY'
                    }
                }
            }
            with open(config_file, 'w') as f:
                json.dump(config_data, f)

            config = PipelineConfig(project_path)

            strategist_config = config.get_llm_config('strategist')
            assert strategist_config['provider'] == 'claude'
            assert strategist_config['model'] == 'claude-opus-4-5'

            designer_config = config.get_llm_config('designer')
            assert designer_config['provider'] == 'gemini'
            assert designer_config['model'] == 'gemini-2.5-pro'

    def test_get_llm_config_missing_agent(self):
        """Test getting LLM config for non-existent agent"""
        with TemporaryDirectory() as tmpdir:
            project_path = Path(tmpdir)
            config_file = project_path / 'product.config.json'

            config_data = {
                'llm': {
                    'strategist': {
                        'provider': 'claude',
                        'model': 'claude-opus-4-5'
                    }
                }
            }
            with open(config_file, 'w') as f:
                json.dump(config_data, f)

            config = PipelineConfig(project_path)
            unknown_config = config.get_llm_config('unknown_agent')

            assert unknown_config == {}

    def test_get_llm_config_no_llm_section(self):
        """Test getting LLM config when no LLM section exists"""
        with TemporaryDirectory() as tmpdir:
            project_path = Path(tmpdir)
            config_file = project_path / 'product.config.json'

            config_data = {'vision': 'Test vision'}
            with open(config_file, 'w') as f:
                json.dump(config_data, f)

            config = PipelineConfig(project_path)
            llm_config = config.get_llm_config('strategist')

            assert llm_config == {}

    def test_multiple_agents_config(self):
        """Test configuration supports any number of agents"""
        with TemporaryDirectory() as tmpdir:
            project_path = Path(tmpdir)
            config_file = project_path / 'product.config.json'

            # Test with 5 different agents
            config_data = {
                'llm': {
                    'strategist': {'provider': 'claude', 'model': 'claude-opus-4-5'},
                    'designer': {'provider': 'gemini', 'model': 'gemini-2.5-pro'},
                    'po': {'provider': 'openai', 'model': 'gpt-4'},
                    'qa': {'provider': 'claude', 'model': 'claude-sonnet-4-5'},
                    'tech_lead': {'provider': 'gemini', 'model': 'gemini-2.5-flash'}
                }
            }
            with open(config_file, 'w') as f:
                json.dump(config_data, f)

            config = PipelineConfig(project_path)

            # Verify all 5 agents are accessible
            assert config.get_llm_config('strategist')['provider'] == 'claude'
            assert config.get_llm_config('designer')['provider'] == 'gemini'
            assert config.get_llm_config('po')['provider'] == 'openai'
            assert config.get_llm_config('qa')['provider'] == 'claude'
            assert config.get_llm_config('tech_lead')['provider'] == 'gemini'


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
