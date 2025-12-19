# BRD Feedback Template

Use this file to provide feedback on the generated Business Requirements Document. When you rerun `generate_brd.py`, this feedback will be automatically incorporated into the regenerated BRD.

## Instructions

1. Review the generated BRD.md file
2. Add your feedback below using the provided sections
3. Rerun: `python scripts/generate_brd.py --project /path/to/project`
4. The BRD will be regenerated incorporating your feedback

## Feedback Sections

### Missing Requirements
<!-- List any requirements that should be added to the BRD -->

Example:
- Need to include offline mode support
- Missing requirement for data export functionality

### Incorrect or Unclear Requirements
<!-- Point out any requirements that are incorrect or need clarification -->

Example:
- The user authentication requirement doesn't specify whether we support social login
- Technical constraints section doesn't mention browser compatibility

### Scope Adjustments
<!-- Suggest changes to the project scope -->

Example:
- Remove advanced analytics from MVP scope
- Add basic reporting as a core feature

### Target Audience Refinement
<!-- Refine the target audience description -->

Example:
- Target audience should focus more on enterprise users
- Need to add "small business owners" as a secondary audience

### Success Metrics
<!-- Suggest changes to success metrics and KPIs -->

Example:
- Add "user retention rate" as a success metric
- Change MAU target from 10K to 5K for MVP

### Other Feedback
<!-- Any other feedback that doesn't fit the above categories -->

Example:
- The tone is too technical; make it more accessible to non-technical stakeholders
- Add a section about competitive landscape

---

**Note:** After adding your feedback, save this file and rerun `generate_brd.py`. The feedback will be incorporated, and you can review the updated BRD. You can iterate multiple times by updating this file and regenerating.
