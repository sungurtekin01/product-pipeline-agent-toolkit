"""Pydantic schema for Development Tickets

This schema mirrors the BAML definition in baml_src/ticket.baml
"""

from pydantic import BaseModel, Field
from typing import List, Optional


class Ticket(BaseModel):
    """Development ticket specification

    Attributes:
        id: Unique ticket identifier
        title: Concise task title
        description: Detailed task description
        priority: Priority level (e.g., High, Medium, Low)
        dependencies: List of dependent ticket IDs
        acceptance_criteria: List of conditions for task completion
        complexity: Estimated complexity or story points
        assignee: Assigned developer or team (optional)
        due_date: Due or milestone target date (optional)
        tags: Tags for categorization (optional)
        notes: Additional notes or clarifications
    """

    id: str = Field(..., description="Unique ticket identifier")
    title: str = Field(..., description="Task title")
    description: str = Field(..., description="Task description")
    priority: str = Field(..., description="Priority level")
    dependencies: List[str] = Field(default_factory=list, description="Dependent ticket IDs")
    acceptance_criteria: List[str] = Field(..., description="Completion criteria")
    complexity: str = Field(..., description="Complexity estimate")
    assignee: str = Field(default="", description="Assigned developer")
    due_date: str = Field(default="", description="Due date")
    tags: List[str] = Field(default_factory=list, description="Categorization tags")
    notes: str = Field(default="", description="Additional notes")


class TicketSpec(BaseModel):
    """Ticket specification for a milestone

    Attributes:
        milestone: Name or identifier of the milestone
        tickets: Array of tickets associated with this milestone
    """

    milestone: str = Field(..., description="Milestone name")
    tickets: List[Ticket] = Field(..., description="List of tickets")

    class Config:
        json_schema_extra = {
            "example": {
                "milestone": "MVP Launch",
                "tickets": [
                    {
                        "id": "TICK-001",
                        "title": "Implement user authentication",
                        "description": "Create login and signup flow...",
                        "priority": "High",
                        "dependencies": [],
                        "acceptance_criteria": [
                            "Users can sign up with email",
                            "Users can log in securely"
                        ],
                        "complexity": "Medium",
                        "assignee": "Backend Team",
                        "due_date": "2024-03-15",
                        "tags": ["backend", "security"],
                        "notes": "Use JWT for session management"
                    }
                ]
            }
        }
