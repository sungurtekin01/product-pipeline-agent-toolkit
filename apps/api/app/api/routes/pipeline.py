"""Pipeline execution endpoints"""

from fastapi import APIRouter, HTTPException, BackgroundTasks, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from typing import Optional, Dict, Any
import asyncio
from datetime import datetime

from app.core.websocket import manager

router = APIRouter()


# Request/Response models
class PipelineConfig(BaseModel):
    """Pipeline configuration"""
    vision: str
    output_dir: str = "docs/product"
    llm: Optional[Dict[str, Any]] = None
    api_keys: Optional[Dict[str, str]] = None  # API keys from frontend Settings UI
    personas: Optional[Dict[str, str]] = None  # Persona mapping: {"prd": "strategist", "design": "designer", "tickets": "po"}


class PipelineExecutionRequest(BaseModel):
    """Request to execute a pipeline step"""
    config: PipelineConfig
    step: str  # "prd", "design", or "tickets"
    feedback: Optional[str] = None


class PipelineExecutionResponse(BaseModel):
    """Response from pipeline execution"""
    task_id: str
    status: str
    message: str


class PipelineStatus(BaseModel):
    """Pipeline execution status"""
    task_id: str
    status: str  # "pending", "running", "completed", "failed"
    step: str
    progress: int  # 0-100
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    started_at: datetime
    completed_at: Optional[datetime] = None


# In-memory task storage (replace with Redis/DB in production)
tasks: Dict[str, PipelineStatus] = {}


@router.post("/execute", response_model=PipelineExecutionResponse)
async def execute_pipeline_step(
    request: PipelineExecutionRequest,
    background_tasks: BackgroundTasks
):
    """
    Execute a pipeline step (PRD, Design, or Tickets)

    This endpoint starts the execution in the background and returns a task ID.
    Use /status/{task_id} to poll for completion.
    """
    import uuid

    task_id = str(uuid.uuid4())

    # Create task status
    tasks[task_id] = PipelineStatus(
        task_id=task_id,
        status="pending",
        step=request.step,
        progress=0,
        started_at=datetime.now()
    )

    # Start background execution
    background_tasks.add_task(
        execute_step,
        task_id=task_id,
        config=request.config,
        step=request.step,
        feedback=request.feedback
    )

    return PipelineExecutionResponse(
        task_id=task_id,
        status="pending",
        message=f"Pipeline step '{request.step}' queued for execution"
    )


@router.get("/status/{task_id}", response_model=PipelineStatus)
async def get_pipeline_status(task_id: str):
    """Get status of a pipeline execution task"""
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="Task not found")

    return tasks[task_id]


@router.get("/tasks")
async def list_tasks():
    """List all pipeline tasks"""
    return {"tasks": list(tasks.values())}


@router.get("/personas")
async def get_personas():
    """
    Get available personas grouped by role

    Returns:
        {
            "personas": {
                "strategist": [{"id": "strategist", "name": "...", "description": "..."}],
                "designer": [{"id": "designer", ...}, {"id": "rn_designer", ...}],
                "po": [{"id": "po", ...}]
            }
        }
    """
    from pathlib import Path
    import sys
    import toml

    # Add engine to path
    ENGINE_PATH = Path(__file__).parent.parent.parent.parent.parent.parent / "packages" / "engine"
    sys.path.insert(0, str(ENGINE_PATH))

    personas_dir = ENGINE_PATH / "personas"

    # Read all persona TOML files
    personas_by_role = {
        "strategist": [],
        "designer": [],
        "po": []
    }

    # Map persona files to their roles
    persona_role_mapping = {
        "strategist": "strategist",
        "designer": "designer",
        "rn_designer": "designer",
        "po": "po"
    }

    for persona_file in personas_dir.glob("*.toml"):
        persona_id = persona_file.stem

        # Determine role
        role = persona_role_mapping.get(persona_id)
        if not role:
            continue

        # Load persona data
        try:
            data = toml.load(persona_file)
            persona_info = {
                "id": persona_id,
                "name": persona_id.replace("_", " ").title(),
                "description": data.get("description", "")
            }
            personas_by_role[role].append(persona_info)
        except Exception as e:
            print(f"Error loading persona {persona_id}: {e}")
            continue

    return {"personas": personas_by_role}


@router.websocket("/ws/{task_id}")
async def websocket_endpoint(websocket: WebSocket, task_id: str):
    """
    WebSocket endpoint for real-time pipeline updates

    Clients connect to this endpoint to receive real-time progress updates
    for a specific task.
    """
    await manager.connect(websocket, task_id)
    try:
        # Keep connection alive and send updates
        while True:
            # Wait for messages (optional - could be used for client commands)
            data = await websocket.receive_text()

            # Echo back (or handle client commands if needed)
            await websocket.send_json({
                "type": "ack",
                "message": f"Received: {data}"
            })
    except WebSocketDisconnect:
        manager.disconnect(websocket, task_id)


# Background execution function
def execute_step(
    task_id: str,
    config: PipelineConfig,
    step: str,
    feedback: Optional[str] = None
):
    """Execute a pipeline step in the background"""
    import asyncio
    asyncio.run(execute_step_async(task_id, config, step, feedback))


async def execute_step_async(
    task_id: str,
    config: PipelineConfig,
    step: str,
    feedback: Optional[str] = None
):
    """Async implementation of pipeline step execution"""
    from app.services.pipeline_executor import PipelineExecutor
    from pathlib import Path

    try:
        # Update status to running
        tasks[task_id].status = "running"
        tasks[task_id].progress = 10
        await manager.send_message(task_id, {
            "type": "progress",
            "status": "running",
            "progress": 10,
            "message": "Starting pipeline execution...",
            "result": {"step": step}
        })

        # Auto-load feedback if not provided and file exists
        if feedback is None:
            feedback_file = Path(config.output_dir) / "conversations" / "feedback" / f"{step}-feedback.md"
            if feedback_file.exists():
                with open(feedback_file, 'r', encoding='utf-8') as f:
                    feedback = f.read()
                await manager.send_message(task_id, {
                    "type": "progress",
                    "status": "running",
                    "progress": 15,
                    "message": f"Found existing feedback, incorporating it into regeneration...",
                    "result": {"step": step}
                })

        # Create executor
        executor = PipelineExecutor(
            vision=config.vision,
            output_dir=config.output_dir,
            llm_config=config.llm,
            api_keys=config.api_keys,
            persona_config=config.personas
        )

        tasks[task_id].progress = 20
        await manager.send_message(task_id, {
            "type": "progress",
            "status": "running",
            "progress": 20,
            "message": f"Initializing {step} generation...",
            "result": {"step": step}
        })

        # Execute the appropriate step
        if step == "prd":
            await manager.send_message(task_id, {
                "type": "progress",
                "status": "running",
                "progress": 30,
                "message": "Generating Product Requirements Document...",
                "result": {"step": step}
            })
            result = await executor.generate_prd(feedback)
            await manager.send_message(task_id, {
                "type": "progress",
                "status": "running",
                "progress": 80,
                "message": "PRD generated successfully",
                "result": {"step": step}
            })
        elif step == "design":
            await manager.send_message(task_id, {
                "type": "progress",
                "status": "running",
                "progress": 30,
                "message": "Running Q&A with Strategist...",
                "result": {"step": step}
            })
            await manager.send_message(task_id, {
                "type": "progress",
                "status": "running",
                "progress": 50,
                "message": "Analyzing PRD and generating design questions...",
                "result": {"step": step}
            })
            result = await executor.generate_design(feedback)
            await manager.send_message(task_id, {
                "type": "progress",
                "status": "running",
                "progress": 80,
                "message": "Design specification generated successfully",
                "result": {"step": step}
            })
        elif step == "tickets":
            await manager.send_message(task_id, {
                "type": "progress",
                "status": "running",
                "progress": 30,
                "message": "Running Q&A with Designer and Strategist...",
                "result": {"step": step}
            })
            await manager.send_message(task_id, {
                "type": "progress",
                "status": "running",
                "progress": 50,
                "message": "Analyzing design and PRD for ticket generation...",
                "result": {"step": step}
            })
            result = await executor.generate_tickets(feedback)
            await manager.send_message(task_id, {
                "type": "progress",
                "status": "running",
                "progress": 80,
                "message": "Development tickets generated successfully",
                "result": {"step": step}
            })
        else:
            raise ValueError(f"Invalid step: {step}")

        tasks[task_id].progress = 90
        await manager.send_message(task_id, {
            "type": "progress",
            "status": "running",
            "progress": 90,
            "message": "Finalizing and saving documents...",
            "result": {"step": step}
        })

        # Mark as completed
        tasks[task_id].status = "completed"
        tasks[task_id].progress = 100
        tasks[task_id].completed_at = datetime.now()
        tasks[task_id].result = result

        await manager.send_message(task_id, {
            "type": "complete",
            "status": "completed",
            "progress": 100,
            "message": f"{step.upper()} generation completed successfully!",
            "result": {**result, "step": step}
        })

    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Pipeline execution error for task {task_id}:")
        print(error_details)

        tasks[task_id].status = "failed"
        tasks[task_id].error = str(e)
        tasks[task_id].completed_at = datetime.now()

        await manager.send_message(task_id, {
            "type": "error",
            "status": "failed",
            "progress": 0,
            "message": f"Error: {str(e)}",
            "error": str(e),
            "result": {"step": step}
        })
