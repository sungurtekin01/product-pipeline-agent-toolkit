"""Document serving endpoints"""

from fastapi import APIRouter, HTTPException
from pathlib import Path
from typing import Optional
from pydantic import BaseModel

router = APIRouter()


class FeedbackRequest(BaseModel):
    step: str
    feedback: str


@router.get("/documents/list")
async def list_documents(output_dir: str = "docs/product"):
    """
    List all available documents

    Returns:
        List of available documents with their status
    """
    output_path = Path(output_dir)

    documents = {
        'brd': {
            'name': 'Business Requirements Document',
            'file': 'BRD.md',
            'exists': (output_path / 'BRD.md').exists()
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
        step: One of 'brd', 'design', 'tickets'
        output_dir: Output directory path (default: docs/product)

    Returns:
        Document content as markdown text
    """
    # Map step names to file names
    file_mapping = {
        'brd': 'BRD.md',
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
        step: One of 'design', 'tickets' (BRD has no Q&A)
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
        step: One of 'brd', 'design', 'tickets'
        request: Feedback content
        output_dir: Output directory path

    Returns:
        Success message with file path
    """
    if step not in ['brd', 'design', 'tickets']:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid step. Must be one of: brd, design, tickets"
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
        step: One of 'brd', 'design', 'tickets'
        output_dir: Output directory path

    Returns:
        Feedback content if exists, empty string otherwise
    """
    if step not in ['brd', 'design', 'tickets']:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid step. Must be one of: brd, design, tickets"
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
