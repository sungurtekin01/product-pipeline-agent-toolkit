# Development Tickets Feedback Template

Use this file to provide feedback on the generated development tickets. When you rerun `generate_tickets.py`, this feedback will be automatically incorporated into the regenerated tickets.

## Instructions

1. Review the generated development-tickets.md file
2. Add your feedback below using the provided sections
3. Rerun: `python scripts/generate_tickets.py --project /path/to/project`
4. The tickets will be regenerated incorporating your feedback

## Feedback Sections

### Missing Tickets
<!-- Identify features or tasks that need tickets but are missing -->

Example:
- Need a ticket for database migration scripts
- Missing ticket for API documentation
- Add ticket for setting up CI/CD pipeline

### Ticket Scope Issues
<!-- Flag tickets that are too large or too small -->

Example:
- "User authentication system" ticket is too large; break into smaller tickets
- Tickets for individual button components are too granular; combine into "UI component library" ticket
- Split "Payment integration" into separate tickets for each payment provider

### Priority Adjustments
<!-- Suggest changes to ticket priorities -->

Example:
- "Database setup" should be High priority, not Medium
- "Advanced analytics" is marked Urgent but should be Low for MVP
- Move "User profile editing" to earlier milestone

### Dependency Corrections
<!-- Fix incorrect or missing dependencies -->

Example:
- "User dashboard" depends on "Authentication" but dependency not listed
- "Email notifications" should depend on "Email service integration"
- Remove dependency: "Search feature" doesn't actually need "Analytics setup"

### Acceptance Criteria Improvements
<!-- Improve or add acceptance criteria -->

Example:
- Add acceptance criteria for "Login page": "User can reset password via email"
- Clarify "Payment processing": Need specific success/failure scenarios
- Missing acceptance criteria for error handling in "File upload" ticket

### Complexity Ratings
<!-- Adjust complexity estimates -->

Example:
- "API integration" marked as Simple but should be Moderate
- "Basic CRUD operations" is marked Complex but should be Simple
- Adjust "Search with filters" from Moderate to Complex

### Milestone Organization
<!-- Reorganize tickets across milestones -->

Example:
- Move "Admin panel" from Milestone 2 to Milestone 3
- "Email verification" should be in MVP milestone
- Create new milestone "Post-Launch Enhancements" for analytics tickets

### Technical Details
<!-- Add technical specifications or constraints -->

Example:
- Add note to "Database setup": Use PostgreSQL 14+
- Specify "API framework": Use FastAPI, not Flask
- Add constraint to "File storage": Maximum 10MB per file

### Assignee Suggestions
<!-- Suggest team member assignments -->

Example:
- Assign all frontend tickets to Frontend team
- "Database design" should go to Backend Lead
- Split "Mobile app" tickets between iOS and Android developers

### Other Ticket Feedback
<!-- Any other feedback about the tickets -->

Example:
- Add tags for "frontend", "backend", "devops" to make filtering easier
- Include estimated hours for each ticket
- Add "Definition of Done" section to template
- Consider adding "Testing" tickets for QA

---

**Note:** After adding your feedback, save this file and rerun `generate_tickets.py`. The feedback will be incorporated along with the Q&A conversation context from the PO, Designer, and Strategist. You can iterate multiple times to refine the tickets until they're ready for your sprint planning.
