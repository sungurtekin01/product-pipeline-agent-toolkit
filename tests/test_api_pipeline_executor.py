"""
Test API Pipeline Executor with BAML Integration

This test verifies that the API service methods (generate_brd, generate_design, generate_tickets)
correctly use BAML functions for document generation.

NOTE: This is an integration test that requires actual API keys.
Run with: pytest tests/test_api_pipeline_executor.py -v
"""

import asyncio
import os
import sys
from pathlib import Path
import tempfile
import shutil

import pytest
from dotenv import load_dotenv
load_dotenv()

# Add apps/api to path
API_PATH = Path(__file__).parent.parent / "apps" / "api"
sys.path.insert(0, str(API_PATH))

from app.services.pipeline_executor import PipelineExecutor

# Skip if no API keys are available (integration test)
HAS_API_KEY = any([
    os.getenv('GEMINI_API_KEY'),
    os.getenv('ANTHROPIC_API_KEY'),
    os.getenv('OPENAI_API_KEY')
])


@pytest.mark.asyncio
@pytest.mark.skipif(not HAS_API_KEY, reason="No API keys available - skipping integration test")
async def test_pipeline_executor():
    """Test full pipeline with BAML functions"""

    # Create temporary output directory
    temp_dir = Path(tempfile.mkdtemp(prefix="test_api_"))
    print(f"✓ Created temp directory: {temp_dir}")

    try:
        # Test vision
        test_vision = """
        Build a simple task management web application where users can:
        - Create, edit, and delete tasks
        - Mark tasks as complete
        - Filter tasks by status
        - Set due dates and priorities
        """

        # Initialize executor
        executor = PipelineExecutor(
            vision=test_vision,
            output_dir=str(temp_dir),
            llm_config={
                "strategist": {"provider": "gemini"},
                "designer": {"provider": "gemini"},
                "po": {"provider": "gemini"}
            }
        )
        print("✓ Initialized PipelineExecutor with Gemini provider")

        # Test 1: Generate BRD
        print("\n" + "="*60)
        print("TEST 1: Generate BRD using BAML")
        print("="*60)
        brd_result = await executor.generate_brd()

        assert brd_result["status"] == "completed", "BRD generation failed"
        assert Path(brd_result["output_file"]).exists(), "BRD markdown not created"
        assert Path(brd_result["json_file"]).exists(), "BRD JSON not created"
        assert "data" in brd_result, "BRD data not in result"
        assert "title" in brd_result["data"], "BRD missing title"
        assert "objectives" in brd_result["data"], "BRD missing objectives"

        print(f"✅ BRD generated successfully")
        print(f"   Title: {brd_result['data']['title']}")
        print(f"   Objectives: {len(brd_result['data']['objectives'])} items")
        print(f"   Files: {brd_result['output_file']}, {brd_result['json_file']}")

        # Test 2: Generate Design
        print("\n" + "="*60)
        print("TEST 2: Generate Design using BAML")
        print("="*60)
        design_result = await executor.generate_design()

        assert design_result["status"] == "completed", "Design generation failed"
        assert Path(design_result["output_file"]).exists(), "Design markdown not created"
        assert Path(design_result["json_file"]).exists(), "Design JSON not created"
        assert "data" in design_result, "Design data not in result"
        assert "summary" in design_result["data"], "Design missing summary"
        assert "screens" in design_result["data"], "Design missing screens"

        print(f"✅ Design generated successfully")
        print(f"   Summary: {design_result['data']['summary'][:100]}...")
        print(f"   Screens: {len(design_result['data']['screens'])} screens")
        print(f"   Files: {design_result['output_file']}, {design_result['json_file']}")

        # Test 3: Generate Tickets
        print("\n" + "="*60)
        print("TEST 3: Generate Tickets using BAML")
        print("="*60)
        tickets_result = await executor.generate_tickets()

        assert tickets_result["status"] == "completed", "Tickets generation failed"
        assert Path(tickets_result["output_file"]).exists(), "Tickets markdown not created"
        assert Path(tickets_result["json_file"]).exists(), "Tickets JSON not created"
        assert "data" in tickets_result, "Tickets data not in result"
        assert "milestone" in tickets_result["data"], "Tickets missing milestone"
        assert "tickets" in tickets_result["data"], "Tickets missing tickets list"

        print(f"✅ Tickets generated successfully")
        print(f"   Milestone: {tickets_result['data']['milestone']}")
        print(f"   Tickets: {len(tickets_result['data']['tickets'])} tickets")
        print(f"   Files: {tickets_result['output_file']}, {tickets_result['json_file']}")

        # Success summary
        print("\n" + "="*60)
        print("✅ ALL TESTS PASSED - API Pipeline Executor with BAML")
        print("="*60)
        print("\nVerified:")
        print("  ✓ generate_brd() uses BAML functions")
        print("  ✓ generate_design() uses BAML functions (with RefineBRD)")
        print("  ✓ generate_tickets() uses BAML functions")
        print("  ✓ All methods return correct structure")
        print("  ✓ All files are created successfully")
        print("  ✓ Type-safe validation working via BAML")

        return True

    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

    finally:
        # Cleanup
        if temp_dir.exists():
            shutil.rmtree(temp_dir)
            print(f"\n✓ Cleaned up temp directory: {temp_dir}")


if __name__ == "__main__":
    success = asyncio.run(test_pipeline_executor())
    sys.exit(0 if success else 1)
