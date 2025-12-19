"""Pipeline execution endpoints"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional, Dict, Any
import asyncio
from datetime import datetime

router = APIRouter()


# Request/Response models
class PipelineConfig(BaseModel):
    """Pipeline configuration"""
    vision: str
    output_dir: str = "docs/product"
    llm: Optional[Dict[str, Any]] = None


class PipelineExecutionRequest(BaseModel):
    """Request to execute a pipeline step"""
    config: PipelineConfig
    step: str  # "brd", "design", or "tickets"
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
    Execute a pipeline step (BRD, Design, or Tickets)

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


# Background execution function
async def execute_step(
    task_id: str,
    config: PipelineConfig,
    step: str,
    feedback: Optional[str] = None
):
    """Execute a pipeline step in the background"""
    from app.services.pipeline_executor import PipelineExecutor

    try:
        # Update status to running
        tasks[task_id].status = "running"
        tasks[task_id].progress = 10

        # Create executor
        executor = PipelineExecutor(
            vision=config.vision,
            output_dir=config.output_dir,
            llm_config=config.llm
        )

        tasks[task_id].progress = 20

        # Execute the appropriate step
        if step == "brd":
            result = await executor.generate_brd(feedback)
        elif step == "design":
            result = await executor.generate_design(feedback)
        elif step == "tickets":
            result = await executor.generate_tickets(feedback)
        else:
            raise ValueError(f"Invalid step: {step}")

        tasks[task_id].progress = 90

        # Mark as completed
        tasks[task_id].status = "completed"
        tasks[task_id].progress = 100
        tasks[task_id].completed_at = datetime.now()
        tasks[task_id].result = result

    except Exception as e:
        tasks[task_id].status = "failed"
        tasks[task_id].error = str(e)
        tasks[task_id].completed_at = datetime.now()
