// ============================================================================
// BAML Functions - Product Pipeline Toolkit
// ============================================================================
//
// This file defines type-safe LLM functions for document generation.
//
// Week 2: BRD Functions
// Week 3: Design, Tickets, and RefineBRD functions
//
// Key Features:
// - Persona prompts injected via Jinja2: {{ persona }}
// - Type-safe output validated against BAML schemas
// - Schema auto-injection: {{ ctx.output_format }}
// - Each function uses appropriate client (StrategistClient, DesignerClient, POClient)
//
// ============================================================================

// ============================================================================
// BRD Generation Functions
// ============================================================================

// Generate Business Requirements Document from product vision
// Uses: StrategistClient (configurable via ClientRegistry)
// Input: Product vision statement
// Output: Validated BRD with title, description, objectives
function GenerateBRD(vision: string, persona: string) -> BRD {
  client StrategistClient
  prompt #"
    {{ persona }}

    ## Task: Generate Business Requirements Document

    You are tasked with creating a comprehensive Business Requirements Document (BRD)
    from the product vision below.

    ### Product Vision:
    {{ vision }}

    ### Instructions:
    1. Analyze the product vision thoroughly
    2. Define a clear, concise product title
    3. Write a comprehensive description covering:
       - Product purpose and value proposition
       - Target audience and user needs
       - Key features and capabilities
       - Market context and competitive positioning
    4. Identify specific, measurable business objectives (3-7 objectives)
    5. Focus on WHAT and WHY, not HOW (avoid technical implementation details)

    ### Output Format:
    Generate a JSON object with this exact structure:
    {{ ctx.output_format }}

    ### Requirements:
    - Title should be concise (2-6 words)
    - Description should be comprehensive (2-4 paragraphs)
    - Objectives should be SMART (Specific, Measurable, Achievable, Relevant, Time-bound)
    - Each objective should be a complete sentence
    - Focus on business value and user outcomes

    Generate the BRD now as a valid JSON object.
  "#
}

// Regenerate BRD incorporating user feedback
// Uses: StrategistClient (configurable via ClientRegistry)
// Input: Product vision + previous feedback
// Output: Improved BRD addressing feedback
function GenerateBRDWithFeedback(vision: string, feedback: string, persona: string) -> BRD {
  client StrategistClient
  prompt #"
    {{ persona }}

    ## Task: Regenerate Business Requirements Document with Feedback

    You are tasked with creating an improved Business Requirements Document (BRD)
    that addresses the feedback provided below.

    ### Product Vision:
    {{ vision }}

    ### Previous Feedback:
    {{ feedback }}

    ### Instructions:
    1. Carefully review the feedback and identify specific concerns or requests
    2. Generate a new BRD that directly addresses each feedback point
    3. Maintain consistency with the product vision
    4. Improve clarity, specificity, and completeness based on feedback
    5. Ensure all feedback is incorporated thoughtfully

    ### Output Format:
    Generate a JSON object with this exact structure:
    {{ ctx.output_format }}

    ### Requirements:
    - Title should be concise (2-6 words)
    - Description should be comprehensive (2-4 paragraphs) and address feedback
    - Objectives should be SMART and reflect feedback insights
    - Each objective should be a complete sentence
    - Focus on business value and user outcomes
    - Explicitly address each point raised in the feedback

    Generate the improved BRD now as a valid JSON object.
  "#
}

// Refine BRD using insights from Q&A conversation
// Uses: StrategistClient (configurable via ClientRegistry)
// Input: Original BRD + Q&A conversation transcript
// Output: Refined BRD with improved clarity and depth
function RefineBRD(original_brd: string, qa_conversation: string, persona: string) -> BRD {
  client StrategistClient
  prompt #"
    {{ persona }}

    ## Task: Refine Business Requirements Document

    You are tasked with improving a Business Requirements Document (BRD) using insights
    gained from a Q&A conversation with other product team members.

    ### Original BRD:
    {{ original_brd }}

    ### Q&A Conversation Transcript:
    {{ qa_conversation }}

    ### Instructions:
    1. Review the original BRD and the Q&A conversation carefully
    2. Identify insights, clarifications, and additional context from the conversation
    3. Refine the BRD to incorporate these insights while maintaining its core structure
    4. Improve clarity, specificity, and completeness based on discussion points
    5. Ensure all valuable information from the Q&A is reflected in the refined BRD
    6. Maintain consistency with the original vision and objectives

    ### Output Format:
    Generate a JSON object with this exact structure:
    {{ ctx.output_format }}

    ### Requirements:
    - Title should remain consistent or be refined if conversation suggests improvement
    - Description should be enhanced with insights from Q&A (2-4 paragraphs)
    - Objectives should be refined to reflect conversation insights and remain SMART
    - Each objective should be a complete sentence
    - Focus on business value and user outcomes
    - Incorporate clarifications and additional context from the conversation

    Generate the refined BRD now as a valid JSON object.
  "#
}

// ============================================================================
// Design Spec Generation Functions
// ============================================================================

// Generate Design Specification from BRD and Q&A conversation
// Uses: DesignerClient (configurable via ClientRegistry)
// Input: BRD + Q&A conversation transcript
// Output: Validated DesignSpec with screens, components, wireframes
function GenerateDesign(brd: string, qa_conversation: string, persona: string) -> DesignSpec {
  client DesignerClient
  prompt #"
    {{ persona }}

    ## Task: Generate Design Specification

    You are tasked with creating a comprehensive Design Specification based on the
    Business Requirements Document (BRD) and insights from Q&A conversations.

    ### Business Requirements Document:
    {{ brd }}

    ### Q&A Conversation Transcript:
    {{ qa_conversation }}

    ### Instructions:
    1. Analyze the BRD and Q&A conversation to understand product requirements
    2. Create a design specification with:
       - Overall design summary (2-3 paragraphs)
       - Key screens with descriptions
       - Wireframes for each screen (text/markdown representation)
       - Core UI components with specifications
    3. Focus on user experience, visual design, and interaction patterns
    4. Ensure designs align with BRD objectives and user needs
    5. Incorporate insights from the Q&A conversation

    ### Output Format:
    Generate a JSON object with this exact structure:
    {{ ctx.output_format }}

    ### Requirements:
    - Summary should cover design philosophy, visual style, and key UX decisions
    - Include 3-10 key screens depending on product complexity
    - Each screen needs name, description, wireframe (text/ASCII art), and components
    - Components should have clear descriptions and usage notes
    - Wireframes can be text-based, markdown, or ASCII art representations
    - Focus on user flow, interaction patterns, and visual hierarchy

    Generate the Design Specification now as a valid JSON object.
  "#
}

// Regenerate Design Specification incorporating user feedback
// Uses: DesignerClient (configurable via ClientRegistry)
// Input: BRD + Q&A conversation + previous feedback
// Output: Improved DesignSpec addressing feedback
function GenerateDesignWithFeedback(brd: string, qa_conversation: string, feedback: string, persona: string) -> DesignSpec {
  client DesignerClient
  prompt #"
    {{ persona }}

    ## Task: Regenerate Design Specification with Feedback

    You are tasked with creating an improved Design Specification that addresses
    the feedback provided below.

    ### Business Requirements Document:
    {{ brd }}

    ### Q&A Conversation Transcript:
    {{ qa_conversation }}

    ### Previous Feedback:
    {{ feedback }}

    ### Instructions:
    1. Carefully review the feedback and identify specific concerns or requests
    2. Generate a new Design Specification that directly addresses each feedback point
    3. Maintain consistency with the BRD and Q&A insights
    4. Improve clarity, completeness, and design quality based on feedback
    5. Ensure all feedback is incorporated thoughtfully

    ### Output Format:
    Generate a JSON object with this exact structure:
    {{ ctx.output_format }}

    ### Requirements:
    - Summary should address feedback and improve design rationale
    - Update screens, wireframes, and components based on feedback
    - Maintain 3-10 key screens depending on product complexity
    - Ensure designs align with BRD objectives and user needs
    - Explicitly address each point raised in the feedback
    - Focus on user experience improvements

    Generate the improved Design Specification now as a valid JSON object.
  "#
}

// ============================================================================
// Tickets Generation Functions
// ============================================================================

// Generate development tickets from BRD, Design, and Q&A conversation
// Uses: POClient (configurable via ClientRegistry)
// Input: BRD + Design Spec + Q&A conversation transcript
// Output: Validated TicketSpec with milestone and tickets
function GenerateTickets(brd: string, design: string, qa_conversation: string, persona: string) -> TicketSpec {
  client POClient
  prompt #"
    {{ persona }}

    ## Task: Generate Development Tickets

    You are tasked with creating a comprehensive set of development tickets based on the
    Business Requirements Document (BRD), Design Specification, and insights from Q&A conversations.

    ### Business Requirements Document:
    {{ brd }}

    ### Design Specification:
    {{ design }}

    ### Q&A Conversation Transcript:
    {{ qa_conversation }}

    ### Instructions:
    1. Analyze the BRD, Design Spec, and Q&A conversation
    2. Break down the product into concrete, actionable development tickets
    3. Define milestone name that represents the product release or major phase
    4. Create tickets with:
       - Clear, specific titles
       - Detailed descriptions
       - Priority levels (High, Medium, Low)
       - Dependencies between tickets
       - Acceptance criteria for each ticket
       - Complexity estimates (Small, Medium, Large)
       - Relevant tags (UI, backend, API, testing, etc.)
    5. Ensure tickets are independently achievable and testable
    6. Order tickets logically based on dependencies

    ### Output Format:
    Generate a JSON object with this exact structure:
    {{ ctx.output_format }}

    ### Requirements:
    - Milestone should be a clear, concise name (e.g., "v1.0 MVP", "Initial Release")
    - Include 5-20 tickets depending on product complexity
    - Each ticket needs unique ID, title, description, priority, acceptance criteria
    - Dependencies should reference other ticket IDs
    - Acceptance criteria should be specific and testable
    - Tags should categorize work type (UI, backend, API, database, testing, etc.)
    - Focus on implementation details and technical tasks

    Generate the Ticket Specification now as a valid JSON object.
  "#
}

// Regenerate development tickets incorporating user feedback
// Uses: POClient (configurable via ClientRegistry)
// Input: BRD + Design Spec + Q&A conversation + previous feedback
// Output: Improved TicketSpec addressing feedback
function GenerateTicketsWithFeedback(brd: string, design: string, qa_conversation: string, feedback: string, persona: string) -> TicketSpec {
  client POClient
  prompt #"
    {{ persona }}

    ## Task: Regenerate Development Tickets with Feedback

    You are tasked with creating an improved set of development tickets that addresses
    the feedback provided below.

    ### Business Requirements Document:
    {{ brd }}

    ### Design Specification:
    {{ design }}

    ### Q&A Conversation Transcript:
    {{ qa_conversation }}

    ### Previous Feedback:
    {{ feedback }}

    ### Instructions:
    1. Carefully review the feedback and identify specific concerns or requests
    2. Generate a new set of tickets that directly addresses each feedback point
    3. Maintain consistency with the BRD, Design Spec, and Q&A insights
    4. Improve clarity, completeness, and ticket quality based on feedback
    5. Ensure all feedback is incorporated thoughtfully
    6. Adjust priorities, dependencies, and acceptance criteria as needed

    ### Output Format:
    Generate a JSON object with this exact structure:
    {{ ctx.output_format }}

    ### Requirements:
    - Milestone name should reflect product phase
    - Update tickets based on feedback (add, remove, modify as needed)
    - Include 5-20 tickets depending on product complexity
    - Each ticket must be actionable and testable
    - Dependencies should be clear and accurate
    - Acceptance criteria should address feedback concerns
    - Explicitly address each point raised in the feedback

    Generate the improved Ticket Specification now as a valid JSON object.
  "#
}
