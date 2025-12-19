# Product Pipeline Toolkit Refactoring Plan

## Overview
Refactor the toolkit to support multiple LLM providers, markdown outputs, multi-agent Q&A conversations, and feedback-based refinement. Implementation will proceed **phase by phase** with frequent logical commits on a new branch.

## Branch Strategy
- Create new branch: `refactor/modular-pipeline`
- Each phase gets multiple small commits
- Review and test after each phase before proceeding
- DO NOT work on main branch

## Implementation Approach
- **Phase by phase** - Complete each phase, commit, review, test before moving to next
- **Markdown only** - Clean break from JSON outputs
- **Tests for critical paths** - LLM clients and config only
- **Frequent commits** - Logical checkpoints within each phase

---

## Phase 1: Foundation & Project Setup

### Goals
- Create new branch
- Set up core module structure
- Create plan directory in repo
- No breaking changes yet

### Tasks
1. **Create new branch**
   ```bash
   git checkout -b refactor/modular-pipeline
   ```

2. **Create directory structure**
   ```
   src/
   ├── __init__.py
   ├── llm/__init__.py
   ├── personas/__init__.py
   ├── agents/__init__.py
   ├── io/__init__.py
   ├── pipeline/__init__.py
   └── schemas/__init__.py
   ```

3. **Create plans directory**
   ```
   plans/
   └── refactoring-plan.md (copy of this plan)
   ```

4. **Update requirements.txt**
   - Add `anthropic` for Claude support
   - Add `openai` for GPT support
   - Keep existing dependencies

5. **Update .gitignore**
   - Add `plans/` directory
   - Add `.claude/` directory
   - Add `CLAUDE.md` file
   - Add `GEMINI.md` file

### Commits
- `feat: create new branch and directory structure for refactoring`
- `chore: update .gitignore to exclude plans, .claude, and AI guidance files`
- `docs: add refactoring plan to plans/ directory`
- `deps: add anthropic and openai SDK dependencies`

### Files to Create
- `src/__init__.py`
- `src/llm/__init__.py`
- `src/personas/__init__.py`
- `src/agents/__init__.py`
- `src/io/__init__.py`
- `src/pipeline/__init__.py`
- `src/schemas/__init__.py`
- `plans/refactoring-plan.md`

### Files to Modify
- `requirements.txt`
- `.gitignore`

---

## Phase 2: LLM Abstraction Layer

### Goals
- Create provider-agnostic LLM interface
- Implement Gemini, Claude, OpenAI clients
- Add configuration and factory pattern
- Tests for all LLM clients

### Tasks

#### 2.1 Base LLM Interface
**File:** `src/llm/base.py`
```python
from abc import ABC, abstractmethod
from typing import Optional

class BaseLLMClient(ABC):
    """Abstract base class for LLM providers"""

    def __init__(self, model: str, api_key: str):
        self.model = model
        self.api_key = api_key

    @abstractmethod
    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Generate response from LLM"""
        pass

    @abstractmethod
    def clean_response(self, response: str) -> str:
        """Clean code fences and formatting from response"""
        pass
```

**Commit:** `feat(llm): add base LLM client interface`

#### 2.2 Gemini Client
**File:** `src/llm/gemini_client.py`
- Extract existing Gemini logic from generate_brd.py
- Implement `BaseLLMClient` interface
- Include existing JSON fence cleaning logic

**Commit:** `feat(llm): implement Gemini client with existing logic`

#### 2.3 Claude Client
**File:** `src/llm/claude_client.py`
- Use `anthropic` SDK
- Implement `BaseLLMClient` interface
- Handle Claude-specific response format

**Commit:** `feat(llm): implement Claude/Anthropic client`

#### 2.4 OpenAI Client
**File:** `src/llm/openai_client.py`
- Use `openai` SDK
- Implement `BaseLLMClient` interface
- Handle OpenAI-specific response format

**Commit:** `feat(llm): implement OpenAI GPT client`

#### 2.5 LLM Factory
**File:** `src/llm/factory.py`
```python
class LLMFactory:
    PROVIDERS = {
        'gemini': GeminiClient,
        'claude': ClaudeClient,
        'openai': OpenAIClient
    }

    @classmethod
    def create(cls, provider: str, model: str, api_key_env: str):
        # Load from environment, create client

    @classmethod
    def from_config(cls, config: dict, agent_name: str, cli_override=None):
        # Priority: CLI > agent config > defaults
```

**Commit:** `feat(llm): add LLM factory with config-based creation`

#### 2.6 Tests (Critical Path Only)
**File:** `tests/test_llm_clients.py`
- Mock LLM responses
- Test all three providers
- Test factory creation
- Test CLI overrides

**Commit:** `test(llm): add unit tests for LLM clients and factory`

### Files to Create
- `src/llm/base.py`
- `src/llm/gemini_client.py`
- `src/llm/claude_client.py`
- `src/llm/openai_client.py`
- `src/llm/factory.py`
- `tests/test_llm_clients.py`

---

## Phase 3: Persona System Refactoring

### Goals
- Create Product Strategist TOML persona
- Make all personas product-agnostic
- Build unified persona loader
- Update BRD script to use TOML persona

### Tasks

#### 3.1 Create Strategist Persona
**File:** `personas/strategist.toml`
- Extract hardcoded persona from generate_brd.py lines 79-85
- Make generic (remove tic-tac-toe references)
- Structure:
  ```toml
  name = "Product Strategist"
  role = "Business Requirements Specialist"
  prompt = """
  You are a Product Strategist specializing in...
  """
  ```

**Commit:** `feat(personas): create product strategist TOML persona`

#### 3.2 Make Existing Personas Generic
**Files to Modify:**
- `personas/rn_designer.toml` - Remove tic-tac-toe references
- `personas/designer.toml` - Remove product-specific examples
- `personas/po.toml` - Make generic for any product type

**Commit:** `refactor(personas): make all personas product-agnostic`

#### 3.3 Persona Loader
**File:** `src/personas/loader.py`
```python
class PersonaLoader:
    def __init__(self, personas_dir: Path):
        self.personas_dir = personas_dir

    def load(self, persona_name: str) -> dict:
        # Load TOML file

    def get_prompt(self, persona_name: str) -> str:
        # Extract prompt field
```

**Commit:** `feat(personas): add unified persona loader`

#### 3.4 Update BRD Script
**File:** `scripts/generate_brd.py`
- Remove hardcoded persona (lines 79-85)
- Use `PersonaLoader` to load strategist.toml
- Keep everything else the same for now

**Commit:** `refactor(brd): use strategist persona from TOML file`

### Files to Create
- `personas/strategist.toml`
- `src/personas/loader.py`

### Files to Modify
- `personas/rn_designer.toml`
- `personas/designer.toml`
- `personas/po.toml`
- `scripts/generate_brd.py`

---

## Phase 4: Configuration Management

### Goals
- Create config management system
- Support product.config.json with LLM settings
- Enable CLI overrides
- Test configuration loading

### Tasks

#### 4.1 Pipeline Config
**File:** `src/pipeline/config.py`
```python
class PipelineConfig:
    def __init__(self, project_path: Path):
        self.config = self._load_config()

    def get_vision(self, cli_override=None) -> str:
        # Priority: CLI > config > error

    def get_output_dir(self, cli_override=None) -> Path:
        # Priority: CLI > config > default

    def get_llm_config(self, agent_name: str) -> dict:
        # Return LLM config for agent
```

**Commit:** `feat(config): add pipeline configuration management`

#### 4.2 Update Scripts with Config Support
**Files to Modify:**
- `scripts/generate_brd.py` - Add --provider, --model CLI args
- `scripts/generate_design.py` - Add --provider, --model CLI args
- `scripts/generate_tickets.py` - Add --provider, --model CLI args

**Commit:** `feat(scripts): add LLM provider CLI arguments`

#### 4.3 Integrate LLM Factory into Scripts
- Modify all scripts to use `LLMFactory.from_config()`
- Replace direct `genai.GenerativeModel()` calls
- Test with all three providers

**Commit:** `refactor(scripts): integrate LLM factory for multi-provider support`

#### 4.4 Tests
**File:** `tests/test_config.py`
- Test config loading
- Test CLI overrides
- Test LLM config resolution

**Commit:** `test(config): add configuration management tests`

### Files to Create
- `src/pipeline/config.py`
- `tests/test_config.py`

### Files to Modify
- `scripts/generate_brd.py`
- `scripts/generate_design.py`
- `scripts/generate_tickets.py`

---

## Phase 5: Markdown Output

### Goals
- Create markdown I/O utilities
- Create Pydantic schemas (mirror BAML)
- Switch all outputs to markdown format
- Remove JSON outputs (clean break)

### Tasks

#### 5.1 Pydantic Schemas
**Files:** `src/schemas/`
- `brd.py` - Mirror baml_src/brd.baml
- `design.py` - Mirror baml_src/design_spec.baml
- `tickets.py` - Mirror baml_src/ticket.baml

**Commit:** `feat(schemas): add Pydantic schemas mirroring BAML definitions`

#### 5.2 Markdown Writer
**File:** `src/io/markdown_writer.py`
```python
class MarkdownWriter:
    @staticmethod
    def write_brd(brd: BRD, output_path: Path):
        # Generate markdown structure

    @staticmethod
    def write_design_spec(design: DesignSpec, output_path: Path):
        # Generate markdown structure

    @staticmethod
    def write_tickets(tickets: TicketSpec, output_path: Path):
        # Generate markdown structure
```

**Commit:** `feat(io): add markdown writer for all document types`

#### 5.3 Markdown Parser
**File:** `src/io/markdown_parser.py`
```python
class MarkdownParser:
    @staticmethod
    def read_feedback(feedback_file: Path) -> Optional[str]:
        # Read feedback markdown if exists

    @staticmethod
    def read_conversation(conversation_file: Path) -> Optional[str]:
        # Read Q&A conversation markdown
```

**Commit:** `feat(io): add markdown parser for feedback and conversations`

#### 5.4 Update Scripts to Output Markdown
- Modify generate_brd.py: Output BRD.md instead of brd.json
- Modify generate_design.py: Output design-spec.md instead of design-spec.json
- Modify generate_tickets.py: Output tickets.md instead of development-tickets.json
- Remove all JSON writing code
- Use BAML validation internally, output markdown

**Commit:** `refactor(scripts): switch to markdown output format`

### Files to Create
- `src/schemas/brd.py`
- `src/schemas/design.py`
- `src/schemas/tickets.py`
- `src/io/markdown_writer.py`
- `src/io/markdown_parser.py`

### Files to Modify
- `scripts/generate_brd.py`
- `scripts/generate_design.py`
- `scripts/generate_tickets.py`

---

## Phase 6: Agent System & Q&A Conversations

### Goals
- Create agent classes (Strategist, Designer, PO)
- Build conversation orchestrator
- Integrate Q&A into design and tickets generation
- Save conversations to markdown

### Tasks

#### 6.1 Base Agent
**File:** `src/agents/base_agent.py`
```python
class BaseAgent:
    def __init__(self, name: str, persona_prompt: str, llm_client: BaseLLMClient):
        self.name = name
        self.persona_prompt = persona_prompt
        self.llm = llm_client

    def ask(self, question: str, context: str) -> str:
        # Ask agent a question with context

    def generate_questions(self, document: str, num_questions: int) -> list[str]:
        # Generate clarifying questions about document
```

**Commit:** `feat(agents): add base agent class with Q&A methods`

#### 6.2 Specific Agents
**Files:**
- `src/agents/strategist.py` - StrategistAgent(BaseAgent)
- `src/agents/designer.py` - DesignerAgent(BaseAgent)
- `src/agents/po.py` - POAgent(BaseAgent)

**Commit:** `feat(agents): implement strategist, designer, and PO agents`

#### 6.3 Conversation Orchestrator
**File:** `src/agents/conversation.py`
```python
class ConversationOrchestrator:
    def __init__(self, output_dir: Path):
        self.conversations_dir = output_dir / 'conversations'

    def run_qa_session(self, questioner: BaseAgent,
                       respondents: List[Tuple[BaseAgent, str]],
                       session_name: str,
                       num_questions: int) -> str:
        # Sequential Q&A: generate questions → get answers → save markdown
```

**Commit:** `feat(agents): add conversation orchestrator for multi-agent Q&A`

#### 6.4 Integrate Q&A into Design Generation
**File:** `scripts/generate_design.py`
- Create DesignerAgent and StrategistAgent
- Run Q&A session before design generation
- Save to conversations/design-qa.md
- Include Q&A context in design prompt

**Commit:** `feat(design): integrate Q&A session with strategist before generation`

#### 6.5 Integrate Q&A into Tickets Generation
**File:** `scripts/generate_tickets.py`
- Create POAgent, DesignerAgent, StrategistAgent
- Run Q&A session: PO asks → Designer/Strategist answer
- Save to conversations/tickets-qa.md
- Include Q&A context in tickets prompt

**Commit:** `feat(tickets): integrate Q&A session with designer and strategist`

### Files to Create
- `src/agents/base_agent.py`
- `src/agents/strategist.py`
- `src/agents/designer.py`
- `src/agents/po.py`
- `src/agents/conversation.py`

### Files to Modify
- `scripts/generate_design.py`
- `scripts/generate_tickets.py`

---

## Phase 7: Feedback Loop

### Goals
- Implement feedback detection in all generators
- Incorporate feedback into regeneration prompts
- Create feedback directory structure
- Test feedback workflow

### Tasks

#### 7.1 Update BRD Generator with Feedback
**File:** `scripts/generate_brd.py`
- Check for `conversations/feedback/brd-feedback.md`
- If exists, read feedback and include in prompt
- Regenerate BRD incorporating feedback

**Commit:** `feat(brd): add feedback loop for iterative refinement`

#### 7.2 Update Design Generator with Feedback
**File:** `scripts/generate_design.py`
- Check for `conversations/feedback/design-feedback.md`
- If exists, incorporate into design generation

**Commit:** `feat(design): add feedback loop for iterative refinement`

#### 7.3 Update Tickets Generator with Feedback
**File:** `scripts/generate_tickets.py`
- Check for `conversations/feedback/tickets-feedback.md`
- If exists, incorporate into tickets generation

**Commit:** `feat(tickets): add feedback loop for iterative refinement`

#### 7.4 Create Example Project Template
**Directory:** `examples/project-template/`
```
product.config.json (with LLM config examples)
docs/product/
└── conversations/
    └── feedback/
        ├── brd-feedback.md (template)
        ├── design-feedback.md (template)
        └── tickets-feedback.md (template)
```

**Commit:** `docs: add project template with feedback examples`

### Files to Modify
- `scripts/generate_brd.py`
- `scripts/generate_design.py`
- `scripts/generate_tickets.py`

### Files to Create
- `examples/project-template/product.config.json`
- `examples/project-template/docs/product/conversations/feedback/brd-feedback.md`
- `examples/project-template/docs/product/conversations/feedback/design-feedback.md`
- `examples/project-template/docs/product/conversations/feedback/tickets-feedback.md`

---

## Phase 8: Documentation & Examples

### Goals
- Update README with new features
- Document configuration format
- Provide usage examples
- Update CLAUDE.md

### Tasks

#### 8.1 Update README
**File:** `README.md`
- Document multi-provider LLM support
- Explain product.config.json LLM configuration
- Show feedback workflow
- Show Q&A conversation feature
- Update examples to use markdown outputs

**Commit:** `docs: update README with multi-provider and Q&A features`

#### 8.2 Update CLAUDE.md
**File:** `CLAUDE.md`
- Update architecture section with new src/ modules
- Document LLM abstraction layer
- Update common commands

**Commit:** `docs: update CLAUDE.md with refactored architecture`

#### 8.3 Create Configuration Examples
**File:** `examples/product.config.json`
- Show all three LLM providers
- Show per-agent configuration
- Include comments explaining each field

**Commit:** `docs: add comprehensive product.config.json examples`

### Files to Modify
- `README.md`
- `CLAUDE.md`

### Files to Create
- `examples/product.config.json`

---

## Critical Files Reference

### New Core Modules (Phase 2-6)
1. `src/llm/base.py` - LLM abstraction interface
2. `src/llm/factory.py` - Provider factory with config
3. `src/agents/conversation.py` - Q&A orchestrator
4. `src/io/markdown_writer.py` - Markdown output
5. `src/pipeline/config.py` - Configuration management

### Modified Scripts (Phase 3-7)
1. `scripts/generate_brd.py` - Persona loading, LLM factory, markdown output, feedback
2. `scripts/generate_design.py` - LLM factory, Q&A integration, markdown output, feedback
3. `scripts/generate_tickets.py` - LLM factory, Q&A integration, markdown output, feedback

### New Personas (Phase 3)
1. `personas/strategist.toml` - Product Strategist persona

### Test Files (Phase 2, 4)
1. `tests/test_llm_clients.py` - LLM client tests
2. `tests/test_config.py` - Configuration tests

---

## Commit Strategy

### Commit Message Format
```
<type>(<scope>): <subject>

Examples:
feat(llm): add base LLM client interface
refactor(brd): use strategist persona from TOML file
test(config): add configuration management tests
docs: update README with multi-provider support
```

### Commit Frequency
- After each logical unit of work
- At least 2-3 commits per phase
- Test commits separate from feature commits
- Documentation commits at the end of phases

### Review Points
- End of each phase: Review, test, commit
- User reviews before proceeding to next phase
- Can iterate on a phase before moving forward

---

## Testing Strategy

### Critical Path Testing (Phases 2, 4)
1. **LLM Clients** (`tests/test_llm_clients.py`)
   - Mock LLM responses
   - Test all three providers (Gemini, Claude, OpenAI)
   - Test factory creation
   - Test CLI overrides

2. **Configuration** (`tests/test_config.py`)
   - Test config file loading
   - Test CLI override precedence
   - Test LLM config resolution
   - Test default values

### Manual Testing (Each Phase)
- Run scripts with different LLM providers
- Verify markdown output format
- Test Q&A conversations
- Test feedback workflow
- Verify error handling

---

## Success Criteria

### Phase Completion Checklist
- [ ] All code changes committed
- [ ] Tests pass (if applicable)
- [ ] Documentation updated
- [ ] Manual testing successful
- [ ] User review and approval

### Overall Success Metrics
- ✅ 3 LLM providers supported (Gemini, Claude, OpenAI)
- ✅ All outputs in Markdown format
- ✅ Per-agent LLM configuration working
- ✅ 2 Q&A sessions (design-qa, tickets-qa) functioning
- ✅ Feedback loop operational
- ✅ Tests for critical paths passing
- ✅ Documentation complete and accurate

---

## Next Steps

1. **Create new branch**: `refactor/modular-pipeline`
2. **Start Phase 1**: Set up directory structure and plan
3. **Commit frequently**: Small, logical commits
4. **Review after each phase**: User testing and approval before proceeding
5. **Iterate as needed**: Adjust plan based on learnings

## Notes
- Work on `refactor/modular-pipeline` branch ONLY
- Do NOT work on main branch
- Each phase should be independently testable
- User will review and test after each phase
- Save this plan to both locations: `plans/refactoring-plan.md` and the Claude Code plan directory
