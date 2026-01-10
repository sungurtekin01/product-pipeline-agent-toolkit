"""Document serving endpoints"""

from fastapi import APIRouter, HTTPException
from pathlib import Path
from typing import Optional
from pydantic import BaseModel
import sys

# Add engine to Python path
ENGINE_PATH = Path(__file__).parent.parent.parent.parent.parent / "packages" / "engine"
sys.path.insert(0, str(ENGINE_PATH))

from src.llm.factory import LLMFactory

router = APIRouter()


class FeedbackRequest(BaseModel):
    step: str
    feedback: str


class VisualizeRequest(BaseModel):
    provider: Optional[str] = "gemini"
    model: Optional[str] = None
    api_keys: Optional[dict] = None


@router.get("/documents/list")
async def list_documents(output_dir: str = "docs/product"):
    """
    List all available documents

    Returns:
        List of available documents with their status
    """
    output_path = Path(output_dir)

    documents = {
        'prd': {
            'name': 'Product Requirements Document',
            'file': 'PRD.md',
            'exists': (output_path / 'PRD.md').exists()
        },
        'design': {
            'name': 'Design Specification',
            'file': 'design-spec.md',
            'exists': (output_path / 'design-spec.md').exists(),
            'qa': (output_path / 'conversations' / 'design-qa.md').exists()
        },
        'tickets': {
            'name': 'Development Tickets',
            'file': 'development-tickets.md',
            'exists': (output_path / 'development-tickets.md').exists(),
            'qa': (output_path / 'conversations' / 'tickets-qa.md').exists()
        }
    }

    return {
        "output_dir": str(output_path),
        "documents": documents
    }


@router.get("/documents/{step}")
async def get_document(step: str, output_dir: str = "docs/product"):
    """
    Get a generated document by step name

    Args:
        step: One of 'prd', 'design', 'tickets'
        output_dir: Output directory path (default: docs/product)

    Returns:
        Document content as markdown text
    """
    # Map step names to file names
    file_mapping = {
        'prd': 'PRD.md',
        'design': 'design-spec.md',
        'tickets': 'development-tickets.md'
    }

    if step not in file_mapping:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid step. Must be one of: {', '.join(file_mapping.keys())}"
        )

    # Construct file path
    file_name = file_mapping[step]
    file_path = Path(output_dir) / file_name

    # Check if file exists
    if not file_path.exists():
        raise HTTPException(
            status_code=404,
            detail=f"Document not found: {file_name}. Has the pipeline been run?"
        )

    # Read and return content
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        return {
            "step": step,
            "file_name": file_name,
            "content": content,
            "path": str(file_path)
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error reading document: {str(e)}"
        )


@router.get("/documents/{step}/qa")
async def get_qa_conversation(step: str, output_dir: str = "docs/product"):
    """
    Get Q&A conversation for a step

    Args:
        step: One of 'design', 'tickets' (PRD has no Q&A)
        output_dir: Output directory path

    Returns:
        Q&A conversation content as markdown
    """
    # Map step names to Q&A file names
    qa_mapping = {
        'design': 'design-qa.md',
        'tickets': 'tickets-qa.md'
    }

    if step not in qa_mapping:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid step. Q&A only available for: {', '.join(qa_mapping.keys())}"
        )

    # Construct file path
    file_name = qa_mapping[step]
    file_path = Path(output_dir) / 'conversations' / file_name

    # Check if file exists
    if not file_path.exists():
        raise HTTPException(
            status_code=404,
            detail=f"Q&A conversation not found: {file_name}"
        )

    # Read and return content
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        return {
            "step": step,
            "file_name": file_name,
            "content": content,
            "path": str(file_path)
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error reading Q&A conversation: {str(e)}"
        )


@router.post("/documents/{step}/feedback")
async def save_feedback(step: str, request: FeedbackRequest, output_dir: str = "docs/product"):
    """
    Save feedback for a document step

    Args:
        step: One of 'prd', 'design', 'tickets'
        request: Feedback content
        output_dir: Output directory path

    Returns:
        Success message with file path
    """
    if step not in ['prd', 'design', 'tickets']:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid step. Must be one of: prd, design, tickets"
        )

    # Create feedback directory
    feedback_dir = Path(output_dir) / 'conversations' / 'feedback'
    feedback_dir.mkdir(parents=True, exist_ok=True)

    # Save feedback
    feedback_file = feedback_dir / f"{step}-feedback.md"
    try:
        with open(feedback_file, 'w', encoding='utf-8') as f:
            f.write(request.feedback)

        return {
            "message": "Feedback saved successfully",
            "path": str(feedback_file),
            "step": step
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error saving feedback: {str(e)}"
        )


@router.get("/documents/{step}/feedback")
async def get_feedback(step: str, output_dir: str = "docs/product"):
    """
    Get existing feedback for a step

    Args:
        step: One of 'prd', 'design', 'tickets'
        output_dir: Output directory path

    Returns:
        Feedback content if exists, empty string otherwise
    """
    if step not in ['prd', 'design', 'tickets']:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid step. Must be one of: prd, design, tickets"
        )

    feedback_file = Path(output_dir) / 'conversations' / 'feedback' / f"{step}-feedback.md"

    if not feedback_file.exists():
        return {
            "step": step,
            "feedback": "",
            "exists": False
        }

    try:
        with open(feedback_file, 'r', encoding='utf-8') as f:
            content = f.read()

        return {
            "step": step,
            "feedback": content,
            "exists": True,
            "path": str(feedback_file)
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error reading feedback: {str(e)}"
        )


@router.post("/documents/design/visualize")
async def visualize_design(request: VisualizeRequest, output_dir: str = "docs/product"):
    """
    Generate HTML visualization of design spec using LLM

    Args:
        request: Provider and model configuration
        output_dir: Output directory path

    Returns:
        HTML content for visualization
    """
    # Read design spec
    design_file = Path(output_dir) / 'design-spec.md'

    if not design_file.exists():
        raise HTTPException(
            status_code=404,
            detail="Design spec not found. Please generate design spec first."
        )

    try:
        with open(design_file, 'r', encoding='utf-8') as f:
            design_content = f.read()

        # Create LLM client
        provider = request.provider or "gemini"
        model = request.model

        # Set default models if not specified
        if not model:
            model_defaults = {
                'gemini': 'gemini-2.0-flash-exp',
                'claude': 'claude-sonnet-4-20250514',
                'openai': 'gpt-4o'
            }
            model = model_defaults.get(provider, 'gemini-2.0-flash-exp')

        # Get API key from request or fall back to environment
        api_key = None
        api_key_env = None

        if request.api_keys:
            # Map provider to API key from request
            provider_key_map = {
                'gemini': 'gemini',
                'claude': 'anthropic',
                'openai': 'openai'
            }
            key_name = provider_key_map.get(provider)
            if key_name and key_name in request.api_keys:
                api_key = request.api_keys[key_name]

        # If no API key from request, fall back to environment variable
        if not api_key:
            api_key_env_defaults = {
                'gemini': 'GEMINI_API_KEY',
                'claude': 'ANTHROPIC_API_KEY',
                'openai': 'OPENAI_API_KEY'
            }
            api_key_env = api_key_env_defaults.get(provider, 'GEMINI_API_KEY')

        llm_client = LLMFactory.create(
            provider=provider,
            model=model,
            api_key=api_key,
            api_key_env=api_key_env
        )

        # Create prompt for HTML visualization
        prompt = f"""You are a frontend developer creating an interactive HTML mockup from a design specification.

INPUT: A design specification document containing screens, components, and UI requirements.

OUTPUT: A single, self-contained HTML file with:
- Embedded CSS (no external stylesheets)
- Embedded JavaScript for interactivity
- All screens from the spec as separate divs
- Working navigation between screens
- Interactive components (buttons, forms, toggles, etc.)
- Responsive layout (mobile-first, max-width container)
- Visual polish (transitions, hover states, animations where specified)

REQUIREMENTS:
1. Parse the design spec and identify all screens/views
2. Implement each component described with appropriate HTML/CSS
3. Add tab navigation or buttons to switch between screens
4. Make all interactive elements functional (clicks, toggles, form inputs)
5. Apply the color scheme and visual style described in the spec
6. Add smooth transitions and animations for better UX
7. Ensure accessibility (ARIA labels, semantic HTML, keyboard navigation)
8. Include inline comments mapping components back to the spec

DESIGN SPECIFICATION:
{design_content}

Generate a complete HTML file ready to download and view in a browser. Start with <!DOCTYPE html>.
DO NOT include markdown code blocks or explanations - output only the raw HTML."""

        # Generate HTML (synchronous call)
        html_content = llm_client.generate(prompt)

        # Clean up if LLM wrapped it in code blocks
        html_content = html_content.strip()
        if html_content.startswith('```html'):
            html_content = html_content[7:]
        if html_content.startswith('```'):
            html_content = html_content[3:]
        if html_content.endswith('```'):
            html_content = html_content[:-3]
        html_content = html_content.strip()

        return {
            "html": html_content,
            "provider": provider,
            "model": model
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating visualization: {str(e)}"
        )
