	# Sait's Product Pipeline Toolkit

AI-powered product development pipeline using BAML schemas and Gemini API to generate Business Requirements Documents, Design Specifications, and Development Tickets.

## Features

- **Type-Safe AI Outputs**: Uses BAML (Boundary Markup Language) schemas to ensure structured, validated responses
- **Reusable Personas**: Pre-configured AI personas for different roles (Designer, Product Owner)
- **Complete Pipeline**: BRD → Design → Tickets workflow for rapid product planning
- **Gemini-Powered**: Leverages Google's Gemini 2.5 Pro for intelligent content generation

## What Gets Generated

1. **Business Requirements Document (BRD)**: Structured overview of your product vision with title, description, and objectives
2. **Design Specification**: Detailed UI/UX design including screens, components, wireframes, and code snippets
3. **Development Tickets**: Organized milestones with actionable tickets including priorities, dependencies, and acceptance criteria

## Prerequisites

- **Python 3.8+**
- **Gemini API Key** - Get yours at [https://aistudio.google.com/apikey](https://aistudio.google.com/apikey)
- **BAML CLI v0.213.0** - Install with: `npm install -g @boundaryml/baml@0.213.0`

## Setup Instructions

### Quick Setup (Recommended)

Run the automated setup script:

```bash
./setup.sh
```

This will:
- Create a virtual environment
- Install all dependencies with correct versions
- Copy .env.example to .env
- Check for required tools

Then follow the next steps to configure your environment and generate the BAML client.

### Manual Setup

### 1. Add to Your Project

Copy all toolkit files into your project directory:

```bash
# Your project structure will look like:
your-project/
├── scripts/          # Python generation scripts
├── baml_src/         # BAML schema definitions
├── personas/         # AI persona configurations
├── examples/         # Sample outputs
├── .env.example      # Environment template
└── requirements.txt  # Python dependencies
```

### 2. Create Virtual Environment and Install Dependencies

```bash
# Create virtual environment
python3 -m venv .venv

# Activate virtual environment
source .venv/bin/activate  # On macOS/Linux
# OR
.venv\Scripts\activate     # On Windows

# Install dependencies
pip install -r requirements.txt
```

**Note**: Always activate the virtual environment before running scripts.

### 3. Configure Environment

```bash
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY
```

### 4. Generate BAML Client

This creates the Python Pydantic models from BAML schemas:

```bash
baml generate
```

**Note**: Make sure you have BAML CLI v0.213.0 installed globally (see Prerequisites). This version generates Python by default.

## Usage

The toolkit can be used in two ways:
1. **Standalone mode** - Run from toolkit directory for quick prototyping
2. **Project mode** - Generate docs for any external project using `product.config.json`

### Using with External Projects (Recommended)

#### Step 1: Create Config in Your Project

In your project root, create `product.config.json`:

```json
{
  "name": "Your Project Name",
  "vision": "Your product vision and description...",
  "output_dir": "docs/product"
}
```

#### Step 2: Generate All Documents

From anywhere, run the toolkit scripts pointing to your project:

```bash
# From your project directory:
cd ~/your-project
python ~/path/to/product-pipeline-toolkit/scripts/generate_brd.py --project .
python ~/path/to/product-pipeline-toolkit/scripts/generate_design.py --project .
python ~/path/to/product-pipeline-toolkit/scripts/generate_tickets.py --project .
```

Or from anywhere:

```bash
python ~/path/to/product-pipeline-toolkit/scripts/generate_brd.py --project ~/your-project
python ~/path/to/product-pipeline-toolkit/scripts/generate_design.py --project ~/your-project
python ~/path/to/product-pipeline-toolkit/scripts/generate_tickets.py --project ~/your-project
```

**Outputs** will be saved to your project's configured output directory (e.g., `docs/product/`):
- `brd.json` - Business Requirements Document
- `design-spec.json` - Design Specification
- `development-tickets.json` - Development Tickets

### Standalone Mode (Quick Prototyping)

#### Step 1: Generate Business Requirements Document

Edit `scripts/generate_brd.py` and customize the `product_vision` variable with your product idea, then run:

```bash
# Make sure virtual environment is activated
source .venv/bin/activate

# Run the script
PYTHONPATH=. python scripts/generate_brd.py
```

**Output**: `brd.json` - Structured business requirements

### Step 2: Generate Design Specification

Uses the BRD to create detailed design specifications:

```bash
PYTHONPATH=. python scripts/generate_design.py
```

**Output**: `design-spec.json` - Complete design specification with screens and components

### Step 3: Generate Development Tickets

Creates actionable development tickets organized by milestones:

```bash
PYTHONPATH=. python scripts/generate_tickets.py
```

**Output**: `product/development-tickets.json` - Ready-to-use development tickets

## Customization

### Personas

The toolkit includes three AI personas in the `personas/` directory:

- **designer.toml** - Web/UI designer specialized in Tailwind CSS
- **rn_designer.toml** - React Native designer for mobile apps
- **po.toml** - Product Owner specialized in kids' educational apps

**To customize**: Edit the persona files to match your domain, tech stack, or preferences.

### BAML Schemas

Extend or modify the schemas in `baml_src/` to add custom fields:

- **brd.baml** - Business requirements structure
- **design_spec.baml** - Design specification format
- **ticket.baml** - Development ticket structure

After modifying schemas, regenerate the BAML client:

```bash
baml generate
```

### Product Vision

Edit the `product_vision` variable in `scripts/generate_brd.py` for each new project.

## Example Outputs

See the `examples/` directory for sample outputs:

- `brd.json` - Example Business Requirements Document
- `design-spec.json` - Example Design Specification
- `development-tickets.json` - Example Development Tickets

## File Structure

```
product-pipeline-toolkit/
├── README.md                       # This file
├── requirements.txt                # Python dependencies
├── .env.example                    # Environment variable template
├── .gitignore                      # Git ignore patterns
├── scripts/
│   ├── generate_brd.py            # Generate Business Requirements
│   ├── generate_design.py         # Generate Design Specifications
│   └── generate_tickets.py        # Generate Development Tickets
├── baml_src/
│   ├── brd.baml                   # BRD schema definition
│   ├── design_spec.baml           # Design spec schema
│   └── ticket.baml                # Ticket schema
├── personas/
│   ├── designer.toml              # Web/UI designer persona
│   ├── rn_designer.toml           # React Native designer persona
│   └── po.toml                    # Product Owner persona
└── examples/
    ├── brd.json                   # Sample BRD output
    ├── design-spec.json           # Sample design spec
    └── development-tickets.json   # Sample tickets
```

## Troubleshooting

### "GEMINI_API_KEY not found"
- Ensure `.env` file exists in project root
- Verify `GEMINI_API_KEY=your_key_here` is set correctly
- Check you're running scripts from the project root

### "ModuleNotFoundError: No module named 'baml_client'"
- Run `baml generate` to create the Python client
- Ensure BAML CLI v0.213.0 is installed: `npm install -g @boundaryml/baml@0.213.0`
- Make sure to run scripts with `PYTHONPATH=.` to include the current directory in the Python path

### "baml-py version mismatch" or "baml-py is likely out of date"
- This means the baml_client was generated with a different version of baml-py
- The requirements.txt pins baml-py to version 0.213.0 to match BAML CLI v0.213.0
- Both the Python package (baml-py) and CLI tool must be version 0.213.0

### "FileNotFoundError" when running scripts
- Ensure you're running from the project root, not from `scripts/` directory
- Correct: `python scripts/generate_brd.py`
- Incorrect: `cd scripts && python generate_brd.py`

### Schema Validation Errors
- The AI might generate output that doesn't match the BAML schema
- Try running the script again (LLM outputs can vary)
- Check the console for detailed error messages
- Consider adjusting your prompt or schema if errors persist

## Advanced Tips

### Using Different Gemini Models

Edit the model selection in each script:

```python
model = genai.GenerativeModel("gemini-2.5-flash")  # Faster, cheaper
model = genai.GenerativeModel("gemini-2.5-pro")    # Better quality
```

### Swapping to Other LLM Providers

The scripts use direct Gemini API calls. To use Claude, GPT-4, or other providers:

1. Replace the `genai` imports and API calls
2. Update the model initialization
3. Adjust the response parsing if needed

Each script only has ~5 lines of LLM-specific code, making swaps straightforward.

### Batch Processing

Create a shell script to run the entire pipeline:

```bash
#!/bin/bash
source .venv/bin/activate
PYTHONPATH=. python scripts/generate_brd.py && \
PYTHONPATH=. python scripts/generate_design.py && \
PYTHONPATH=. python scripts/generate_tickets.py
```

## Credits

Created by Sait for rapid product development workflows.

## License

Feel free to use this toolkit in your projects and adapt it to your needs.
