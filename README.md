# Product Pipeline Toolkit - Monorepo

AI-powered product development pipeline with visual canvas UI. Transform your product vision into complete documentation (PRD → Design Spec → Development Tickets) using multi-agent LLM collaboration.

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
Vision → PRD → Design Spec → Dev Tickets
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

**For Docker (Recommended):**
- **Docker** and **Docker Compose** installed
- **API Keys** (at least one) - You'll configure these in the Settings UI:
  - Gemini: https://aistudio.google.com/apikey (Free tier: 60 requests/min)
  - Anthropic: https://console.anthropic.com/ ($5 free credit)
  - OpenAI: https://platform.openai.com/api-keys ($5 free credit for new accounts)

**For Manual Setup (Development):**
- **Node.js 18+** and **pnpm**
- **Python 3.8+**
- **BAML CLI v0.213.0**: `npm install -g @boundaryml/baml@0.213.0`
- Same API keys as above

### 1. Clone and Setup

#### For Docker Users (Quick Setup):

```bash
# Clone repository
git clone <repo-url>
cd product-pipeline-toolkit

# That's it! Docker will handle the rest.
# Skip to "2. Run the Application → Option A: Docker"
```

#### For Manual Setup (Development):

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

#### Option A: Docker (Easiest - Recommended)

```bash
# Start all services (frontend + backend)
docker compose up

# Or run in detached mode
docker compose up -d

# View logs
docker compose logs -f

# Stop services
docker compose down
```

Then open http://localhost:3000

#### Option B: Manual (Development)

```bash
# Terminal 1 - Frontend
pnpm dev

# Terminal 2 - Backend API
cd apps/api
source .venv/bin/activate
uvicorn app.main:app --reload
```

Then open http://localhost:3000

#### Option C: Engine Only (CLI)

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
python ~/product-pipeline-toolkit/packages/engine/scripts/generate_prd.py --project .
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
- `scripts/` - Generation scripts (PRD, Design, Tickets)

## 🎮 Using the UI

### 1. Configure API Keys (First Time)

Click the **Settings** button in the top-right corner to configure your API keys. Keys are stored securely in your browser's local storage and sent directly to the LLM providers - never stored on any server.

**For CLI/Engine-only usage:**
Create `.env` in `packages/engine` with:
```bash
GEMINI_API_KEY=your_key_here
ANTHROPIC_API_KEY=your_key_here
OPENAI_API_KEY=your_key_here
```

### 2. Enter Product Vision

In the sidebar, enter your product vision in the text area.

### 3. Configure LLM

Select your preferred LLM provider (Gemini, Claude, or GPT).

### 4. Run Pipeline

Click "Run Pipeline" to execute all steps sequentially:
1. PRD generation
2. Design Spec generation (with Q&A)
3. Development Tickets (with Q&A)

### 5. Watch Real-time Progress

Watch the pipeline canvas nodes update in real-time via WebSocket as each step executes:
- Gray = Pending
- Blue with progress bar = Running
- Green = Completed
- Red = Failed

### 6. View Generated Documents

Click "View Documents" to open the document viewer:
- Switch between PRD, Design Spec, and Tickets tabs
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

**For Users**: Configure API keys via the Settings UI in the web application. No manual `.env` file setup required.

**For Developers**: If testing the engine CLI directly (without the UI), create `.env` in `packages/engine`:

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

### "API key not found" or "Please configure your API keys"

Click the **Settings** button in the UI and add at least one API key. Keys are stored in your browser's local storage.

For CLI/standalone engine usage, ensure `.env` file exists in `packages/engine` with your API keys.

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
- [x] Inline feedback editor in UI
- [x] Settings UI for API key management
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
