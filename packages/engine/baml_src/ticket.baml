class TicketSpec {
  milestone string        // Name or identifier of the milestone
  tickets Ticket[]        // Array of tickets associated with this milestone
}

class Ticket {
  id string               // Unique ticket identifier (optional if auto-generated)
  title string            // Concise task title
  description string      // Detailed task description
  priority string         // Priority level (e.g., High, Medium, Low)
  dependencies string[]   // List of dependent ticket IDs
  acceptance_criteria string[]  // List of conditions for task completion validation
  complexity string       // Estimated complexity or story points (e.g., Small, Medium, Large)
  assignee string         // Optional assigned developer or team
  due_date string         // Optional due or milestone target date
  tags string[]           // Optional tags for categorization (e.g., UI, backend, accessibility)
  notes string            // Additional notes or clarifications
}

