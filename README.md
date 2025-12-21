# Product Pipeline Toolkit - Monorepo

AI-powered product development pipeline with visual canvas UI. Transform your product vision into complete documentation (BRD → Design Spec → Development Tickets) using multi-agent LLM collaboration.

## 🎯 What is This?

A monorepo containing:
- **Visual UI** (Next.js + React Flow) - Interactive pipeline canvas
- **API Backend** (FastAPI) - Executes pipeline steps
- **Engine** (Python) - Core AI pipeline with multi-provider LLM support

## 🏗️ Architecture

```
product-pipeline-toolkit/
├── apps/
│   ├── web/          # Next.js frontend with React Flow canvas
│   └── api/          # FastAPI backend for pipeline execution
└── packages/
    └── engine/       # Core pipeline engine (Python)
```

### Visual Pipeline Flow

```
Vision → BRD → Design Spec → Dev Tickets
         ↓        ↓             ↓
      Strategist  Designer      PO
         ↓        ↓             ↓
      Q&A with   Q&A with    Q&A with
      nothing    Strategist   Designer+Strategist
```

## ✨ Key Features

- **🎨 Visual Pipeline Canvas** - Interactive React Flow diagram
- **🤖 Multi-Provider LLM** - Gemini, Claude (Anthropic), OpenAI GPT
- **💬 Multi-Agent Q&A** - Agents collaborate before generating documents
- **🔄 Feedback Loop** - Iterative refinement with feedback incorporation
- **📝 Dual Output** - Markdown (primary) + JSON (compatibility)
- **⚙️ Flexible Config** - Per-agent LLM configuration
- **🎯 Type-Safe** - BAML schemas + Pydantic validation
- **🚀 Real-time Progress** - Watch pipeline execution live

## 🚀 Quick Start

### Prerequisites

- **Node.js 18+** and **pnpm**
- **Python 3.8+**
- **BAML CLI v0.213.0**: `npm install -g @boundaryml/baml@0.213.0`
- **API Keys** (at least one):
  - Gemini: https://aistudio.google.com/apikey
  - Anthropic: https://console.anthropic.com/
  - OpenAI: https://platform.openai.com/api-keys

### 1. Clone and Setup

```bash
# Clone repository
git clone <repo-url>
cd product-pipeline-toolkit

# Install frontend dependencies
pnpm install

# Setup Python environment for engine
cd packages/engine
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
# Edit .env and add your API keys

# Generate BAML client
baml generate
cd ../..

# Setup API backend
cd apps/api
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cd ../..
```

### 2. Run the Application

#### Option A: Full Stack (Recommended)

```bash
# Terminal 1 - Frontend
pnpm dev

# Terminal 2 - Backend API
cd apps/api
source .venv/bin/activate
uvicorn app.main:app --reload
```

Then open http://localhost:3000

#### Option B: Engine Only (CLI)

```bash
# Navigate to engine
cd packages/engine
source .venv/bin/activate

# Create a project
mkdir -p ~/my-product
cp -r examples/project-template/* ~/my-product/
cd ~/my-product

# Edit product.config.json with your vision

# Run pipeline
python ~/product-pipeline-toolkit/packages/engine/scripts/generate_brd.py --project .
python ~/product-pipeline-toolkit/packages/engine/scripts/generate_design.py --project .
python ~/product-pipeline-toolkit/packages/engine/scripts/generate_tickets.py --project .
```

## 📦 Monorepo Structure

### Frontend (`apps/web`)

Next.js 14 application with React Flow pipeline canvas.

**Key Components:**
- `components/pipeline/PipelineCanvas.tsx` - Main canvas with React Flow
- `components/pipeline/PipelineNode.tsx` - Custom node for pipeline steps
- `app/page.tsx` - Main application page

**Tech Stack:**
- Next.js 14 (App Router)
- React Flow 12
- Tailwind CSS 4
- TypeScript
- Lucide Icons

### Backend (`apps/api`)

FastAPI application that executes the pipeline.

**Endpoints:**
- `POST /api/pipeline/execute` - Execute a pipeline step
- `GET /api/pipeline/status/{task_id}` - Get execution status
- `GET /api/pipeline/tasks` - List all tasks
- `WS /api/pipeline/ws/{task_id}` - Real-time progress updates
- `GET /api/documents/{step}` - Get generated document content
- `GET /api/documents/{step}/qa` - Get Q&A conversation
- `GET /api/documents/list` - List all available documents
- `GET /api/health` - Health check

**Tech Stack:**
- FastAPI
- Uvicorn
- Pydantic
- Python 3.8+

### Engine (`packages/engine`)

Core pipeline engine with multi-provider LLM support.

**Architecture:**
- `src/llm/` - Multi-provider LLM abstraction (Gemini, Claude, OpenAI)
- `src/agents/` - Multi-agent system (Strategist, Designer, PO)
- `src/personas/` - Reusable agent personas (TOML)
- `src/io/` - Markdown/JSON I/O utilities
- `src/pipeline/` - Configuration management
- `src/schemas/` - Pydantic schemas (mirror BAML)
- `baml_src/` - BAML schema definitions
- `scripts/` - Generation scripts (BRD, Design, Tickets)

## 🎮 Using the UI

### 1. Enter Product Vision

In the sidebar, enter your product vision in the text area.

### 2. Configure LLM

Select your preferred LLM provider (Gemini, Claude, or GPT).

### 3. Run Pipeline

Click "Run Pipeline" to execute all steps sequentially:
1. BRD generation
2. Design Spec generation (with Q&A)
3. Development Tickets (with Q&A)

### 4. Watch Real-time Progress

Watch the pipeline canvas nodes update in real-time via WebSocket as each step executes:
- Gray = Pending
- Blue with progress bar = Running
- Green = Completed
- Red = Failed

### 5. View Generated Documents

Click "View Documents" to open the document viewer:
- Switch between BRD, Design Spec, and Tickets tabs
- View Q&A conversations for Design and Tickets
- Download any document as markdown
- See which documents are available

## 📝 Configuration

### LLM Configuration

Configure different LLMs for each agent in your project's `product.config.json`:

```json
{
  "vision": "Build a task management app...",
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

### Environment Variables

Create `.env` files in both `packages/engine` and `apps/api`:

```bash
GEMINI_API_KEY=your_key_here
ANTHROPIC_API_KEY=your_key_here
OPENAI_API_KEY=your_key_here
```

## 🔄 Feedback Loop

All generators support iterative refinement:

1. Generate initial document
2. Review output in `docs/product/`
3. Add feedback to `docs/product/conversations/feedback/[type]-feedback.md`
4. Regenerate - feedback is automatically incorporated

## 🧪 Development

### Frontend Development

```bash
# Start dev server
pnpm dev

# Lint
pnpm lint

# Build
pnpm build
```

### Backend Development

```bash
cd apps/api
source .venv/bin/activate

# Run with hot reload
uvicorn app.main:app --reload

# Run tests (when implemented)
pytest
```

### Engine Development

```bash
cd packages/engine
source .venv/bin/activate

# Run tests
pytest tests/

# After modifying BAML schemas
baml generate
```

## 📚 Documentation

- **Frontend**: `apps/web/README.md`
- **Backend**: `apps/api/README.md`
- **Engine**: `packages/engine/README.md`

## 🛠️ Troubleshooting

### "ModuleNotFoundError: No module named 'baml_client'"

```bash
cd packages/engine
baml generate
```

### "API key not found"

Ensure `.env` files exist in both `packages/engine` and `apps/api` with your API keys.

### Frontend can't connect to backend

Ensure FastAPI is running on port 8000:
```bash
cd apps/api
source .venv/bin/activate
uvicorn app.main:app --reload
```

### Python import errors

Ensure you're in the correct virtual environment:
```bash
# For API
cd apps/api
source .venv/bin/activate

# For Engine
cd packages/engine
source .venv/bin/activate
```

## 🎯 Roadmap

- [x] WebSocket support for real-time progress updates
- [x] Document viewer with markdown rendering
- [ ] Inline feedback editor in UI
- [ ] Project management (save/load multiple projects)
- [ ] Authentication and user management
- [ ] Export to Linear/Jira/GitHub Issues
- [ ] Collaborative editing
- [ ] Version history

## 📄 License

MIT

## 🙏 Credits

Powered by:
- [BAML](https://www.boundaryml.com/) - Type-safe AI schemas
- [React Flow](https://reactflow.dev/) - Interactive node graphs
- [Next.js](https://nextjs.org/) - React framework
- [FastAPI](https://fastapi.tiangolo.com/) - Python web framework
- [Google Gemini](https://ai.google.dev/) - Fast, cost-effective LLM
- [Anthropic Claude](https://www.anthropic.com/) - Advanced reasoning
- [OpenAI GPT](https://openai.com/) - Versatile language models
