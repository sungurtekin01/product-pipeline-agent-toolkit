"""Pydantic schema for Business Requirements Document (BRD)

This schema mirrors the BAML definition in baml_src/brd.baml
"""

from pydantic import BaseModel, Field
from typing import List


class BRD(BaseModel):
    """Business Requirements Document schema

    Attributes:
        title: Clear, concise product name or identifier
        description: Comprehensive overview of the product
        objectives: Specific, measurable goals the product aims to achieve
    """

    title: str = Field(..., description="Product title or name")
    description: str = Field(..., description="Product description and overview")
    objectives: List[str] = Field(..., description="List of product objectives")

    class Config:
        json_schema_extra = {
            "example": {
                "title": "Project Management App",
                "description": "A modern project management application...",
                "objectives": [
                    "Enable teams to collaborate effectively",
                    "Provide real-time progress tracking"
                ]
            }
        }
