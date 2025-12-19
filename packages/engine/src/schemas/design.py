"""Pydantic schema for Design Specification

This schema mirrors the BAML definition in baml_src/design_spec.baml
"""

from pydantic import BaseModel, Field
from typing import List


class Component(BaseModel):
    """UI Component specification

    Attributes:
        name: Component name
        description: Component purpose and behavior
        code_snippet: Example code or implementation hint
        notes: Additional implementation notes
    """

    name: str = Field(..., description="Component name")
    description: str = Field(..., description="Component description")
    code_snippet: str = Field(..., description="Code snippet or implementation example")
    notes: str = Field(..., description="Additional notes or clarifications")


class Screen(BaseModel):
    """Screen/View specification

    Attributes:
        name: Screen name
        description: Screen purpose and user interactions
        wireframe: Markdown, HTML, or text representation of layout
        components: List of UI components for this screen
    """

    name: str = Field(..., description="Screen name")
    description: str = Field(..., description="Screen description")
    wireframe: str = Field(..., description="Wireframe representation")
    components: List[Component] = Field(..., description="List of components")


class DesignSpec(BaseModel):
    """Design Specification schema

    Attributes:
        summary: Overall design summary
        screens: List of screens/views in the application
    """

    summary: str = Field(..., description="Design summary")
    screens: List[Screen] = Field(..., description="List of screens")

    class Config:
        json_schema_extra = {
            "example": {
                "summary": "A modern, responsive design for the project...",
                "screens": [
                    {
                        "name": "Home Screen",
                        "description": "Main landing page...",
                        "wireframe": "...",
                        "components": [
                            {
                                "name": "Header",
                                "description": "Navigation header",
                                "code_snippet": "<Header />",
                                "notes": "Use responsive design"
                            }
                        ]
                    }
                ]
            }
        }
