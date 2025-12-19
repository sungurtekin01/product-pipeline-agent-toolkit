"""Markdown writer for converting schemas to markdown format"""

from pathlib import Path
from typing import Union
from src.schemas.brd import BRD
from src.schemas.design import DesignSpec
from src.schemas.tickets import TicketSpec


class MarkdownWriter:
    """Write schema objects to markdown files

    This class provides static methods to convert BRD, DesignSpec, and TicketSpec
    objects into well-formatted markdown documents.

    Example usage:
        brd = BRD(title="My App", description="...", objectives=[...])
        MarkdownWriter.write_brd(brd, Path('docs/BRD.md'))
    """

    @staticmethod
    def write_brd(brd: BRD, output_path: Path) -> None:
        """Write Business Requirements Document to markdown

        Args:
            brd: BRD object to convert
            output_path: Path to output markdown file

        Format:
            # {title}

            ## Description
            {description}

            ## Objectives
            1. {objective 1}
            2. {objective 2}
            ...
        """
        markdown = f"# {brd.title}\n\n"
        markdown += "## Description\n\n"
        markdown += f"{brd.description}\n\n"
        markdown += "## Objectives\n\n"

        for i, objective in enumerate(brd.objectives, 1):
            markdown += f"{i}. {objective}\n"

        # Ensure output directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(markdown)

    @staticmethod
    def write_design_spec(design: DesignSpec, output_path: Path) -> None:
        """Write Design Specification to markdown

        Args:
            design: DesignSpec object to convert
            output_path: Path to output markdown file

        Format:
            # Design Specification

            ## Summary
            {summary}

            ## Screens

            ### {screen.name}
            {screen.description}

            **Wireframe:**
            {screen.wireframe}

            **Components:**
            - **{component.name}**: {component.description}
              ```
              {component.code_snippet}
              ```
              *Notes: {component.notes}*
        """
        markdown = "# Design Specification\n\n"
        markdown += "## Summary\n\n"
        markdown += f"{design.summary}\n\n"
        markdown += "## Screens\n\n"

        for screen in design.screens:
            markdown += f"### {screen.name}\n\n"
            markdown += f"{screen.description}\n\n"
            markdown += "**Wireframe:**\n\n"
            markdown += f"{screen.wireframe}\n\n"
            markdown += "**Components:**\n\n"

            for component in screen.components:
                markdown += f"- **{component.name}**: {component.description}\n\n"
                if component.code_snippet:
                    markdown += "  ```\n"
                    markdown += f"  {component.code_snippet}\n"
                    markdown += "  ```\n\n"
                if component.notes:
                    markdown += f"  *Notes: {component.notes}*\n\n"

        # Ensure output directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(markdown)

    @staticmethod
    def write_tickets(ticket_specs: Union[TicketSpec, list[TicketSpec]], output_path: Path) -> None:
        """Write Development Tickets to markdown

        Args:
            ticket_specs: TicketSpec object or list of TicketSpec objects to convert
            output_path: Path to output markdown file

        Format:
            # Development Tickets

            ## {milestone}

            ### [{ticket.id}] {ticket.title}

            **Priority:** {ticket.priority}
            **Complexity:** {ticket.complexity}

            {ticket.description}

            **Acceptance Criteria:**
            - {criterion 1}
            - {criterion 2}

            **Dependencies:** {dep1, dep2}
            **Assignee:** {assignee}
            **Due Date:** {due_date}
            **Tags:** {tag1, tag2}

            **Notes:** {notes}
        """
        # Handle both single TicketSpec and list of TicketSpec
        if isinstance(ticket_specs, TicketSpec):
            ticket_specs = [ticket_specs]

        markdown = "# Development Tickets\n\n"

        for spec in ticket_specs:
            markdown += f"## {spec.milestone}\n\n"

            for ticket in spec.tickets:
                markdown += f"### [{ticket.id}] {ticket.title}\n\n"
                markdown += f"**Priority:** {ticket.priority}  \n"
                markdown += f"**Complexity:** {ticket.complexity}\n\n"
                markdown += f"{ticket.description}\n\n"

                if ticket.acceptance_criteria:
                    markdown += "**Acceptance Criteria:**\n\n"
                    for criterion in ticket.acceptance_criteria:
                        markdown += f"- {criterion}\n"
                    markdown += "\n"

                # Optional fields
                details = []
                if ticket.dependencies:
                    details.append(f"**Dependencies:** {', '.join(ticket.dependencies)}")
                if ticket.assignee:
                    details.append(f"**Assignee:** {ticket.assignee}")
                if ticket.due_date:
                    details.append(f"**Due Date:** {ticket.due_date}")
                if ticket.tags:
                    details.append(f"**Tags:** {', '.join(ticket.tags)}")

                if details:
                    markdown += "  \n".join(details) + "\n\n"

                if ticket.notes:
                    markdown += f"**Notes:** {ticket.notes}\n\n"

                markdown += "---\n\n"

        # Ensure output directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(markdown)
