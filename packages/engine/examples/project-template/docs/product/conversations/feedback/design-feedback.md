# Design Spec Feedback Template

Use this file to provide feedback on the generated Design Specification. When you rerun `generate_design.py`, this feedback will be automatically incorporated into the regenerated design spec.

## Instructions

1. Review the generated design-spec.md file
2. Add your feedback below using the provided sections
3. Rerun: `python scripts/generate_design.py --project /path/to/project`
4. The design spec will be regenerated incorporating your feedback

## Feedback Sections

### Screen Layout Issues
<!-- Feedback on screen layouts, user flows, navigation -->

Example:
- Login screen should include "Remember Me" checkbox
- Dashboard needs a search bar in the top navigation
- Settings screen is too cluttered; split into multiple tabs

### Component Changes
<!-- Suggest changes to specific UI components -->

Example:
- Replace dropdown with radio buttons for payment method selection
- Add loading spinner component for async operations
- Use a modal instead of inline form for adding new items

### Accessibility Concerns
<!-- Point out accessibility issues or improvements -->

Example:
- Need proper ARIA labels for all form inputs
- Color contrast ratio is too low on secondary buttons
- Missing keyboard navigation support for the main menu

### UX Improvements
<!-- Suggest user experience improvements -->

Example:
- Add confirmation dialog before deleting items
- Provide inline validation feedback on form fields
- Add tooltips to explain complex features

### Missing Screens or Flows
<!-- Identify missing screens or user flows -->

Example:
- Need a password reset flow
- Missing error state screens (404, 500, etc.)
- Add onboarding flow for first-time users

### Design System Consistency
<!-- Feedback on design consistency and patterns -->

Example:
- Button styles are inconsistent across screens
- Use consistent spacing (8px grid system)
- Standardize form field heights and borders

### Wireframe Clarity
<!-- Improve wireframe descriptions or add details -->

Example:
- Wireframe for checkout flow needs more detail on payment section
- Add example data to dashboard wireframe for better visualization
- Clarify the responsive behavior for mobile layout

### Other Design Feedback
<!-- Any other design-related feedback -->

Example:
- Consider adding dark mode support
- The color palette feels too corporate; make it more friendly
- Add micro-interactions for better user engagement

---

**Note:** After adding your feedback, save this file and rerun `generate_design.py`. The feedback will be incorporated along with the Q&A conversation context from the Designer and Strategist. You can iterate multiple times for refinement.
