# Sait's Product Pipeline Toolkit

AI-powered product development pipeline using BAML schemas and multiple LLM providers to generate Business Requirements Documents, Design Specifications, and Development Tickets with multi-agent conversations and iterative refinement.

## Features

- **🤖 Multi-Provider LLM Support**: Use Gemini, Claude (Anthropic), or OpenAI GPT - mix and match per agent
- **💬 Multi-Agent Q&A**: Automated conversations between Designer, Strategist, and Product Owner agents for better context
- **🔄 Feedback Loop**: Iterative refinement - provide feedback and regenerate with improvements incorporated
- **📝 Markdown Outputs**: Human-readable markdown documents (with JSON for compatibility)
- **🎯 Type-Safe AI Outputs**: Uses BAML (Boundary Markup Language) schemas for structured, validated responses
- **🎭 Reusable Personas**: Pre-configured AI personas for different roles (Designer, Product Owner, Strategist)
- **⚙️ Flexible Configuration**: Per-agent LLM configuration with CLI overrides
- **📊 Complete Pipeline**: BRD → Design → Tickets workflow for rapid product planning

## What Gets Generated

### Documents
1. **Business Requirements Document (BRD)**: Structured overview with objectives, constraints, and success metrics
2. **Design Specification**: Detailed UI/UX design with screens, components, wireframes, and code snippets
3. **Development Tickets**: Organized milestones with actionable tickets including priorities, dependencies, and acceptance criteria

### Multi-Agent Conversations
- **design-qa.md**: Designer asks Strategist about BRD before creating design spec
- **tickets-qa.md**: Product Owner asks Designer and Strategist before generating tickets

### Feedback Templates
- **brd-feedback.md**: Provide feedback to refine BRD
- **design-feedback.md**: Provide feedback to refine design spec
- **tickets-feedback.md**: Provide feedback to refine tickets

## Prerequisites

- **Python 3.8+**
- **API Keys** (at least one):
  - Gemini API Key: [https://aistudio.google.com/apikey](https://aistudio.google.com/apikey)
  - Anthropic API Key: [https://console.anthropic.com/](https://console.anthropic.com/)
  - OpenAI API Key: [https://platform.openai.com/api-keys](https://platform.openai.com/api-keys)
- **BAML CLI v0.213.0**: `npm install -g @boundaryml/baml@0.213.0`

## Quick Start

### 1. Setup Toolkit

```bash
# Clone or copy toolkit to your machine
git clone <repo-url> product-pipeline-toolkit
cd product-pipeline-toolkit

# Run automated setup
./setup.sh

# Or manual setup:
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and add your API keys:
# GEMINI_API_KEY=your_key
# ANTHROPIC_API_KEY=your_key
# OPENAI_API_KEY=your_key

# Generate BAML client
baml generate
```

### 2. Set Up Your Project

```bash
# Copy project template to your project directory
cp -r examples/project-template/* ~/your-project/

# Edit product.config.json with your product vision and LLM preferences
cd ~/your-project
nano product.config.json
```

Example `product.config.json`:

```json
{
  "vision": "Build a task management app for remote teams with real-time collaboration...",
  "output_dir": "docs/product",
  "llm": {
    "strategist": {
      "provider": "gemini",
      "model": "gemini-2.0-flash-exp"
    },
    "designer": {
      "provider": "claude",
      "model": "claude-sonnet-4-20250514"
    },
    "po": {
      "provider": "openai",
      "model": "gpt-4o"
    }
  }
}
```

### 3. Generate Product Documents

```bash
# From your project directory
cd ~/your-project

# Generate BRD
python ~/product-pipeline-toolkit/scripts/generate_brd.py --project .

# Review BRD, then generate Design Spec (includes Q&A with Strategist)
python ~/product-pipeline-toolkit/scripts/generate_design.py --project .

# Review Design, then generate Tickets (includes Q&A with Designer & Strategist)
python ~/product-pipeline-toolkit/scripts/generate_tickets.py --project .
```

### 4. Iterative Refinement (Optional)

```bash
# Add feedback to any document
nano docs/product/conversations/feedback/brd-feedback.md
# Add your feedback using the structured template

# Regenerate with feedback incorporated
python ~/product-pipeline-toolkit/scripts/generate_brd.py --project .

# Repeat for design and tickets as needed
```

## LLM Provider Configuration

### Supported Providers

| Provider | Models | Strengths |
|----------|--------|-----------|
| **Gemini** | `gemini-2.0-flash-exp`, `gemini-1.5-pro` | Fast, cost-effective, great for structured output |
| **Claude** | `claude-sonnet-4-20250514`, `claude-opus-4-20250514` | Excellent reasoning, detailed analysis |
| **OpenAI** | `gpt-4o`, `gpt-4o-mini`, `gpt-4-turbo` | Versatile, reliable, balanced performance |

### Per-Agent Configuration

Configure different LLM providers for each agent in `product.config.json`:

```json
{
  "llm": {
    "strategist": {
      "provider": "gemini",
      "model": "gemini-2.0-flash-exp",
      "api_key_env": "GEMINI_API_KEY"
    },
    "designer": {
      "provider": "claude",
      "model": "claude-sonnet-4-20250514",
      "api_key_env": "ANTHROPIC_API_KEY"
    },
    "po": {
      "provider": "openai",
      "model": "gpt-4o",
      "api_key_env": "OPENAI_API_KEY"
    }
  }
}
```

### CLI Overrides

Override provider/model from command line:

```bash
# Override provider for all agents
python scripts/generate_brd.py --project . --provider claude

# Override specific model
python scripts/generate_design.py --project . --model claude-opus-4-20250514

# Override both
python scripts/generate_tickets.py --project . --provider gemini --model gemini-2.0-flash-exp
```

**Priority**: CLI args > agent config > defaults

## Multi-Agent Q&A System

The toolkit uses multi-agent conversations to improve output quality.

### Design Generation Q&A

Before generating the design spec, the **Designer agent** asks the **Strategist agent** clarifying questions about the BRD:

```
Q&A SESSION: UX Designer ↔ Product Strategist
==========================================

🤔 UX Designer is analyzing BRD and generating questions...
✓ Generated 5 questions

Q1: What are the primary user personas?
  ↳ Product Strategist is responding...

Q2: What are the technical constraints?
  ↳ Product Strategist is responding...
...

✓ Conversation saved to docs/product/conversations/design-qa.md
```

The Q&A context is automatically included in the design generation prompt.

### Tickets Generation Q&A

Before generating tickets, the **Product Owner agent** asks both **Designer** and **Strategist** questions:

```
Q&A SESSION: Product Owner ↔ Designer & Strategist
==================================================

🤔 Product Owner is analyzing documents and generating questions...
✓ Generated 5 questions

Q1: What are the technical dependencies?
  ↳ UX Designer is responding...
  ↳ Product Strategist is responding...

Q2: What should be the MVP scope?
  ↳ UX Designer is responding...
  ↳ Product Strategist is responding...
...

✓ Conversation saved to docs/product/conversations/tickets-qa.md
```

## Feedback Loop Workflow

All generators support iterative refinement through feedback files.

### How It Works

1. **Generate Initial Document**
   ```bash
   python scripts/generate_brd.py --project ~/your-project
   ```

2. **Review Output**
   - Read `docs/product/BRD.md`
   - Identify areas for improvement

3. **Add Feedback**
   - Edit `docs/product/conversations/feedback/brd-feedback.md`
   - Use structured template to provide feedback:

   ```markdown
   ### Missing Requirements
   - Need offline mode support
   - Add data export functionality

   ### Scope Adjustments
   - Remove advanced analytics from MVP
   ```

4. **Regenerate with Feedback**
   ```bash
   python scripts/generate_brd.py --project ~/your-project
   ```

   The script detects feedback and incorporates it:
   ```
   📝 Found feedback at docs/product/conversations/feedback/brd-feedback.md
   🔄 Regenerating BRD with feedback incorporated...
   ```

5. **Iterate**
   - Review updated document
   - Add more feedback if needed
   - Regenerate again

This works for all three document types (BRD, Design, Tickets).

## Output Structure

After running all scripts, your project will have:

```
your-project/
├── product.config.json
└── docs/product/
    ├── BRD.md                       # Business Requirements (markdown)
    ├── brd.json                     # BRD (JSON for compatibility)
    ├── design-spec.md               # Design Specification (markdown)
    ├── design-spec.json             # Design (JSON)
    ├── development-tickets.md       # Development Tickets (markdown)
    ├── development-tickets.json     # Tickets (JSON)
    └── conversations/
        ├── design-qa.md             # Q&A: Designer ↔ Strategist
        ├── tickets-qa.md            # Q&A: PO ↔ Designer & Strategist
        └── feedback/
            ├── brd-feedback.md      # Your feedback for BRD
            ├── design-feedback.md   # Your feedback for design
            └── tickets-feedback.md  # Your feedback for tickets
```

## Customization

### Personas

The toolkit includes three AI personas in `personas/`:

- **strategist.toml** - Product Strategist for business requirements
- **designer.toml** - UX/UI Designer for design specifications
- **po.toml** - Product Owner for development tickets

**To customize**: Edit persona TOML files to match your domain, tech stack, or preferences.

### BAML Schemas

Extend or modify schemas in `baml_src/`:

- **brd.baml** - Business requirements structure
- **design_spec.baml** - Design specification format
- **ticket.baml** - Development ticket structure

After modifying schemas:

```bash
baml generate
```

## Architecture

### Module Structure

```
product-pipeline-toolkit/
├── scripts/                  # Generation scripts
│   ├── generate_brd.py      # BRD generator
│   ├── generate_design.py   # Design spec generator
│   └── generate_tickets.py  # Tickets generator
├── src/                      # Core modules
│   ├── llm/                 # LLM abstraction layer
│   │   ├── base.py          # BaseLLMClient interface
│   │   ├── gemini_client.py # Gemini implementation
│   │   ├── claude_client.py # Claude implementation
│   │   ├── openai_client.py # OpenAI implementation
│   │   └── factory.py       # LLMFactory for creating clients
│   ├── agents/              # Multi-agent system
│   │   ├── base_agent.py    # BaseAgent with Q&A methods
│   │   ├── strategist.py    # Strategist agent
│   │   ├── designer.py      # Designer agent
│   │   ├── po.py            # Product Owner agent
│   │   └── conversation.py  # ConversationOrchestrator
│   ├── personas/            # Persona management
│   │   └── loader.py        # PersonaLoader for TOML files
│   ├── io/                  # Input/Output utilities
│   │   ├── markdown_writer.py  # Write documents as markdown
│   │   └── markdown_parser.py  # Read feedback/conversations
│   ├── pipeline/            # Pipeline configuration
│   │   └── config.py        # PipelineConfig management
│   └── schemas/             # Pydantic schemas
│       ├── brd.py           # BRD schema
│       ├── design.py        # Design spec schema
│       └── tickets.py       # Tickets schema
├── personas/                 # Persona TOML files
├── baml_src/                 # BAML schema definitions
├── examples/                 # Examples and templates
│   └── project-template/    # Project template with config
└── tests/                    # Unit tests
```

### Key Components

**LLM Abstraction Layer** (`src/llm/`):
- Abstract interface for multiple LLM providers
- Factory pattern for creating clients from config
- Consistent API across Gemini, Claude, and OpenAI

**Multi-Agent System** (`src/agents/`):
- BaseAgent with `ask()` and `generate_questions()` methods
- Specialized agents for different roles
- ConversationOrchestrator for managing Q&A sessions

**Configuration System** (`src/pipeline/`):
- Supports `product.config.json` in project directories
- CLI overrides for provider and model
- Priority: CLI > config > defaults

## Advanced Usage

### Standalone Mode (Without Config File)

```bash
# Set vision via CLI
python scripts/generate_brd.py --vision "Build a task management app..." --output docs/product

# Or edit scripts directly and run
PYTHONPATH=. python scripts/generate_brd.py
```

### Batch Processing

Create a pipeline script:

```bash
#!/bin/bash
PROJECT_DIR="$1"

echo "Generating BRD..."
python scripts/generate_brd.py --project "$PROJECT_DIR"

echo "Generating Design Spec..."
python scripts/generate_design.py --project "$PROJECT_DIR"

echo "Generating Development Tickets..."
python scripts/generate_tickets.py --project "$PROJECT_DIR"

echo "✓ Pipeline complete!"
```

Usage:

```bash
chmod +x pipeline.sh
./pipeline.sh ~/your-project
```

### Using Different Models Per Run

```bash
# Try different models to compare output quality
python scripts/generate_design.py --project . --model claude-opus-4-20250514
python scripts/generate_design.py --project . --model gpt-4o
python scripts/generate_design.py --project . --model gemini-2.0-flash-exp
```

## Troubleshooting

### "API key not found"

**Solution**:
- Ensure `.env` file exists with correct API key(s)
- Check environment variable names match config
- Verify you're using the correct key for your provider

### "ModuleNotFoundError: No module named 'baml_client'"

**Solution**:
- Run `baml generate` to create the Python client
- Ensure BAML CLI v0.213.0 is installed
- Check `baml_client/` directory was created

### "BAML validation error"

**Solution**:
- LLM output doesn't match schema
- Try regenerating (LLM outputs vary)
- Consider using a different model
- Check schema in `baml_src/` if customized

### "Config file not found"

**Solution**:
- Make sure `product.config.json` is in project root
- Or use CLI args: `--vision "..." --output docs/product`
- Or copy from `examples/project-template/`

### Feedback not being incorporated

**Solution**:
- Verify feedback file path: `docs/product/conversations/feedback/[type]-feedback.md`
- Check output directory matches config
- Ensure feedback file is not empty

## Testing

Run unit tests:

```bash
# Activate virtual environment
source .venv/bin/activate

# Run all tests
pytest tests/

# Run specific test file
pytest tests/test_llm_clients.py
pytest tests/test_config.py
```

## Examples

See `examples/project-template/` for:
- Sample `product.config.json` with all configuration options
- Feedback templates for all document types
- Complete project structure
- Usage instructions

## Contributing

This toolkit is designed to be extensible:

1. **Add new LLM providers**: Implement `BaseLLMClient` interface in `src/llm/`
2. **Add new agents**: Extend `BaseAgent` in `src/agents/`
3. **Customize schemas**: Edit BAML files in `baml_src/`
4. **Add new personas**: Create TOML files in `personas/`

## Credits

Created by Sait for rapid product development workflows.

Powered by:
- [BAML](https://www.boundaryml.com/) - Type-safe AI schemas
- [Google Gemini](https://ai.google.dev/) - Fast, cost-effective LLM
- [Anthropic Claude](https://www.anthropic.com/) - Advanced reasoning
- [OpenAI GPT](https://openai.com/) - Versatile language models

## License

Feel free to use this toolkit in your projects and adapt it to your needs.
