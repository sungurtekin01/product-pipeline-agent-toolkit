# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## AI Guidance

* Ignore GEMINI.md and GEMINI-*.md files
* To save main context space, for code searches, inspections, troubleshooting or analysis, use code-searcher subagent where appropriate - giving the subagent full context background for the task(s) you assign it.
* After receiving tool results, carefully reflect on their quality and determine optimal next steps before proceeding. Use your thinking to plan and iterate based on this new information, and then take the best next action.
* For maximum efficiency, whenever you need to perform multiple independent operations, invoke all relevant tools simultaneously rather than sequentially.
* Before you finish, please verify your solution
* Do what has been asked; nothing more, nothing less.
* NEVER create files unless they're absolutely necessary for achieving your goal.
* ALWAYS prefer editing an existing file to creating a new one.
* NEVER proactively create documentation files (*.md) or README files. Only create documentation files if explicitly requested by the User.
* When you update or modify core context files, also update markdown documentation and memory bank
* When asked to commit changes, exclude CLAUDE.md and CLAUDE-*.md referenced memory bank system files from any commits. Never delete these files.

## Memory Bank System

This project uses a structured memory bank system with specialized context files. Always check these files for relevant information before starting work:

### Core Context Files

* **CLAUDE-activeContext.md** - Current session state, goals, and progress (if exists)
* **CLAUDE-patterns.md** - Established code patterns and conventions (if exists)
* **CLAUDE-decisions.md** - Architecture decisions and rationale (if exists)
* **CLAUDE-troubleshooting.md** - Common issues and proven solutions (if exists)
* **CLAUDE-config-variables.md** - Configuration variables reference (if exists)
* **CLAUDE-temp.md** - Temporary scratch pad (only read when referenced)

**Important:** Always reference the active context file first to understand what's currently being worked on and maintain session continuity.

### Memory Bank System Backups

When asked to backup Memory Bank System files, you will copy the core context files above and @.claude settings directory to directory @/path/to/backup-directory. If files already exist in the backup directory, you will overwrite them.

## Claude Code Official Documentation

When working on Claude Code features (hooks, skills, subagents, MCP servers, etc.), use the `claude-docs-consultant` skill to selectively fetch official documentation from docs.claude.com.

## Project Overview

**Product Pipeline Toolkit** - AI-powered product development pipeline using BAML schemas and multiple LLM providers (Gemini, Claude, OpenAI) with multi-agent conversations and iterative refinement.

### Monorepo Structure

```
product-pipeline-toolkit/
├── apps/
│   ├── web/              # Next.js frontend (React Flow canvas)
│   └── api/              # FastAPI backend (pipeline execution)
└── packages/
    └── engine/           # Core Python pipeline engine
```

### Architecture

1. **Frontend** (`apps/web/`)
   - Next.js 14 with React Flow for visual pipeline canvas
   - Real-time WebSocket updates during execution
   - Settings UI for API key management (localStorage)
   - Document viewer with markdown rendering

2. **Backend API** (`apps/api/`)
   - FastAPI with async pipeline execution
   - WebSocket support for real-time progress
   - Integrates with engine package

3. **BAML Schema Layer** (`packages/engine/baml_src/`)
   - Type-safe schemas define structure for PRD, Design Specs, and Tickets
   - Schemas compiled to Python Pydantic models via `baml generate`
   - Ensures validated, structured AI outputs

4. **LLM Abstraction Layer** (`packages/engine/src/llm/`)
   - `base.py` - BaseLLMClient abstract interface
   - `gemini_client.py` - Google Gemini implementation
   - `claude_client.py` - Anthropic Claude implementation
   - `openai_client.py` - OpenAI GPT implementation
   - `factory.py` - LLMFactory for creating clients from config
   - Supports per-agent configuration and CLI overrides

5. **Multi-Agent System** (`packages/engine/src/agents/`)
   - `base_agent.py` - BaseAgent with ask() and generate_questions() methods
   - `strategist.py` - Product Strategist agent
   - `designer.py` - UX/UI Designer agent
   - `po.py` - Product Owner agent
   - `conversation.py` - ConversationOrchestrator for Q&A sessions
   - Automated conversations between agents improve output quality

6. **Pipeline Scripts** (`packages/engine/scripts/`)
   - `generate_prd.py` - Creates PRD with feedback loop support
   - `generate_design.py` - Generates Design Spec with Designer ↔ Strategist Q&A
   - `generate_tickets.py` - Creates Tickets with PO ↔ Designer & Strategist Q&A
   - Flow: load persona → run Q&A → check feedback → call LLM → validate → save markdown + JSON

7. **Persona System** (`packages/engine/personas/`)
   - `strategist.toml` - Product Strategist persona
   - `designer.toml` - UX/UI Designer persona
   - `po.toml` - Product Owner persona
   - `loader.py` - PersonaLoader for reading TOML files
   - Product-agnostic personas for reusability

8. **I/O Utilities** (`packages/engine/src/io/`)
   - `markdown_writer.py` - Write PRD, Design, Tickets as markdown
   - `markdown_parser.py` - Read feedback and conversation files
   - Primary output: markdown, secondary: JSON for compatibility

9. **Configuration System** (`packages/engine/src/pipeline/`)
   - `config.py` - PipelineConfig for product.config.json
   - Supports per-agent LLM configuration
   - Priority: CLI args > agent config > defaults

10. **Pydantic Schemas** (`packages/engine/src/schemas/`)
    - `prd.py` - PRD schema mirroring BAML
    - `design.py` - Design spec schema
    - `tickets.py` - Tickets schema
    - Used for validation and markdown generation

### Persona-Task Separation Pattern

The toolkit implements a clean separation between **persona context** (WHO) and **task instructions** (WHAT):

**BAML Functions** (`baml_src/functions.baml`):
- Accept `persona` as a parameter (managed by orchestration layer)
- Structured prompt: Persona first, then task-specific instructions
- Clear separation in prompt template:
  ```baml
  prompt #"
    {{ persona }}              // WHO: Agent identity and capabilities

    ## Task: [Task Name]       // WHAT: Specific instructions for this task
    ...
  "#
  ```

**Orchestration Layer** (Scripts & API):
- `PersonaLoader` - Loads persona from TOML files (`personas/`)
- Scripts pass loaded persona to BAML functions
- Personas are product-agnostic and reusable across projects

**Benefits:**
- **Flexibility**: Swap personas without modifying BAML functions
- **Reusability**: Same task logic works with different persona configurations
- **Clarity**: Prompts show clear separation of concerns
- **Maintainability**: Update personas independently from task definitions

**Example Flow:**
```python
# 1. Load persona from TOML
persona_loader = PersonaLoader('personas')
strategist_persona = persona_loader.get_prompt('strategist')

# 2. BAML function receives persona + task data
prd = await b.GeneratePRD(
    vision=product_vision,
    persona=strategist_persona  # Injected at top of prompt
)

# 3. Final prompt structure:
#    [Persona context - WHO the agent is]
#    [Task instructions - WHAT to generate]
```

### Common Development Commands

```bash
# Start full stack with Docker (recommended)
docker compose up

# Or start manually:
# Terminal 1 - Frontend
pnpm dev

# Terminal 2 - Backend API
cd apps/api && source .venv/bin/activate && uvicorn app.main:app --reload

# Engine CLI (standalone usage)
cd packages/engine
source .venv/bin/activate
baml generate  # After modifying BAML schemas

# Run pipeline scripts
python scripts/generate_prd.py --project /path/to/project
python scripts/generate_design.py --project /path/to/project
python scripts/generate_tickets.py --project /path/to/project

# Override LLM provider and model
python scripts/generate_prd.py --project . --provider claude --model claude-sonnet-4-20250514

# Run tests
pytest tests/
```

### Environment Configuration

```bash
# Required: Copy and configure .env with API keys
cp .env.example .env
# Add API keys to .env:
# GEMINI_API_KEY=your_key_here
# ANTHROPIC_API_KEY=your_key_here  (for Claude)
# OPENAI_API_KEY=your_key_here     (for GPT)

# External projects need product.config.json:
# {
#   "vision": "Product vision...",
#   "output_dir": "docs/product",
#   "llm": {
#     "strategist": {"provider": "gemini", "model": "gemini-2.0-flash-exp"},
#     "designer": {"provider": "claude", "model": "claude-sonnet-4-20250514"},
#     "po": {"provider": "openai", "model": "gpt-4o"}
#   }
# }
```

### Key Files to Understand

**Frontend:**
- **apps/web/app/page.tsx** - Main application page
- **apps/web/components/pipeline/** - Pipeline canvas components
- **apps/web/lib/store/pipelineStore.ts** - State management

**Backend:**
- **apps/api/app/services/pipeline_executor.py** - Pipeline execution service
- **apps/api/app/api/routes/pipeline.py** - Pipeline API endpoints

**Engine:**
- **packages/engine/src/llm/factory.py** - LLM factory (Gemini, Claude, OpenAI)
- **packages/engine/src/agents/conversation.py** - Multi-agent Q&A orchestrator
- **packages/engine/baml_src/*.baml** - BAML schema definitions
- **packages/engine/personas/*.toml** - AI persona configurations

### Working with BAML Schemas

When modifying schemas in `packages/engine/baml_src/`:
1. Edit the `.baml` file to add/remove fields
2. Run `baml generate` in `packages/engine/` to regenerate Python client
3. Test with pipeline execution

### Dependencies

- **Node.js 18+** and **pnpm** (frontend)
- **Python 3.8+** (backend and engine)
- **BAML CLI v0.213.0** (must match baml-py version)
- **Docker** (optional, for containerized deployment)
- **API Keys** (at least one required):
  - Gemini: https://aistudio.google.com/apikey
  - Anthropic Claude: https://console.anthropic.com/
  - OpenAI: https://platform.openai.com/api-keys



## ALWAYS START WITH THESE COMMANDS FOR COMMON TASKS

**Task: "List/summarize all files and directories"**

```bash
fd . -t f           # Lists ALL files recursively (FASTEST)
# OR
rg --files          # Lists files (respects .gitignore)
```

**Task: "Search for content in files"**

```bash
rg "search_term"    # Search everywhere (FASTEST)
```

**Task: "Find files by name"**

```bash
fd "filename"       # Find by name pattern (FASTEST)
```

### Directory/File Exploration

```bash
# FIRST CHOICE - List all files/dirs recursively:
fd . -t f           # All files (fastest)
fd . -t d           # All directories
rg --files          # All files (respects .gitignore)

# For current directory only:
ls -la              # OK for single directory view
```

### BANNED - Never Use These Slow Tools

* ❌ `tree` - NOT INSTALLED, use `fd` instead
* ❌ `find` - use `fd` or `rg --files`
* ❌ `grep` or `grep -r` - use `rg` instead
* ❌ `ls -R` - use `rg --files` or `fd`
* ❌ `cat file | grep` - use `rg pattern file`

### Use These Faster Tools Instead

```bash
# ripgrep (rg) - content search 
rg "search_term"                # Search in all files
rg -i "case_insensitive"        # Case-insensitive
rg "pattern" -t py              # Only Python files
rg "pattern" -g "*.md"          # Only Markdown
rg -1 "pattern"                 # Filenames with matches
rg -c "pattern"                 # Count matches per file
rg -n "pattern"                 # Show line numbers 
rg -A 3 -B 3 "error"            # Context lines
rg " (TODO| FIXME | HACK)"      # Multiple patterns

# ripgrep (rg) - file listing 
rg --files                      # List files (respects •gitignore)
rg --files | rg "pattern"       # Find files by name 
rg --files -t md                # Only Markdown files 

# fd - file finding 
fd -e js                        # All •js files (fast find) 
fd -x command {}                # Exec per-file 
fd -e md -x ls -la {}           # Example with ls 

# jq - JSON processing 
jq. data.json                   # Pretty-print 
jq -r .name file.json           # Extract field 
jq '.id = 0' x.json             # Modify field
```

### Search Strategy

1. Start broad, then narrow: `rg "partial" | rg "specific"`
2. Filter by type early: `rg -t python "def function_name"`
3. Batch patterns: `rg "(pattern1|pattern2|pattern3)"`
4. Limit scope: `rg "pattern" src/`

### INSTANT DECISION TREE

```
User asks to "list/show/summarize/explore files"?
  → USE: fd . -t f  (fastest, shows all files)
  → OR: rg --files  (respects .gitignore)

User asks to "search/grep/find text content"?
  → USE: rg "pattern"  (NOT grep!)

User asks to "find file/directory by name"?
  → USE: fd "name"  (NOT find!)

User asks for "directory structure/tree"?
  → USE: fd . -t d  (directories) + fd . -t f  (files)
  → NEVER: tree (not installed!)

Need just current directory?
  → USE: ls -la  (OK for single dir)
```
