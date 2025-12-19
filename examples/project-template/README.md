# Example Project Template

This directory provides a template structure for using the Product Pipeline Toolkit with your own projects.

## Quick Start

### 1. Copy Template to Your Project

```bash
# Copy this template to your project directory
cp -r examples/project-template/* /path/to/your/project/
```

### 2. Configure Your Project

Edit `product.config.json`:

```json
{
  "vision": "Build a task management app for remote teams...",
  "output_dir": "docs/product",
  "llm": {
    "strategist": {
      "provider": "gemini",
      "model": "gemini-2.0-flash-exp",
      "api_key_env": "GEMINI_API_KEY"
    },
    "designer": {
      "provider": "claude",
      "model": "claude-sonnet-4-20250514",
      "api_key_env": "ANTHROPIC_API_KEY"
    },
    "po": {
      "provider": "openai",
      "model": "gpt-4o",
      "api_key_env": "OPENAI_API_KEY"
    }
  }
}
```

### 3. Set Environment Variables

```bash
export GEMINI_API_KEY="your-gemini-api-key"
export ANTHROPIC_API_KEY="your-anthropic-api-key"
export OPENAI_API_KEY="your-openai-api-key"
```

Or create a `.env` file in your project:

```bash
GEMINI_API_KEY=your-gemini-api-key
ANTHROPIC_API_KEY=your-anthropic-api-key
OPENAI_API_KEY=your-openai-api-key
```

### 4. Generate Documents

```bash
# Generate BRD
python scripts/generate_brd.py --project /path/to/your/project

# Generate Design Spec (after reviewing BRD)
python scripts/generate_design.py --project /path/to/your/project

# Generate Development Tickets (after reviewing design spec)
python scripts/generate_tickets.py --project /path/to/your/project
```

## Directory Structure

After running all scripts, your project will have:

```
your-project/
├── product.config.json          # LLM and project configuration
├── docs/product/
│   ├── BRD.md                   # Business Requirements Document (markdown)
│   ├── brd.json                 # BRD (JSON for inter-script compatibility)
│   ├── design-spec.md           # Design Specification (markdown)
│   ├── design-spec.json         # Design spec (JSON)
│   ├── development-tickets.md   # Development tickets (markdown)
│   ├── development-tickets.json # Tickets (JSON)
│   └── conversations/
│       ├── design-qa.md         # Q&A: Designer ↔ Strategist
│       ├── tickets-qa.md        # Q&A: PO ↔ Designer & Strategist
│       └── feedback/
│           ├── brd-feedback.md      # Feedback for BRD refinement
│           ├── design-feedback.md   # Feedback for design refinement
│           └── tickets-feedback.md  # Feedback for tickets refinement
```

## Feedback Loop Workflow

### 1. Initial Generation
```bash
python scripts/generate_brd.py --project /path/to/project
```

### 2. Review and Add Feedback
Edit `docs/product/conversations/feedback/brd-feedback.md`:
```markdown
### Missing Requirements
- Need to include offline mode support
- Add data export functionality

### Scope Adjustments
- Remove advanced analytics from MVP
```

### 3. Regenerate with Feedback
```bash
python scripts/generate_brd.py --project /path/to/project
```

The script will detect your feedback and regenerate the BRD incorporating your changes.

### 4. Iterate
Repeat steps 2-3 as many times as needed until you're satisfied with the output.

## Configuration Options

### LLM Providers

You can mix and match providers per agent:

- **Gemini**: Fast, cost-effective (Google)
- **Claude**: Excellent reasoning (Anthropic)
- **OpenAI**: Versatile, reliable (OpenAI)

### CLI Overrides

Override provider/model from command line:

```bash
# Use Claude for strategist (overrides config)
python scripts/generate_brd.py --project /path/to/project --provider claude

# Use specific model
python scripts/generate_design.py --project /path/to/project --model gpt-4o

# Override both
python scripts/generate_tickets.py --project /path/to/project --provider gemini --model gemini-2.0-flash-exp
```

### Priority Order

Configuration priority: **CLI args > agent config > defaults**

## Multi-Agent Q&A Sessions

The toolkit automatically runs Q&A sessions between agents:

### Design Generation
- **Designer** asks **Strategist** questions about the BRD
- Conversation saved to `docs/product/conversations/design-qa.md`
- Context included in design generation prompt

### Tickets Generation
- **Product Owner** asks **Designer** and **Strategist** questions
- PO gets clarification on both BRD and design spec
- Conversation saved to `docs/product/conversations/tickets-qa.md`
- Context included in tickets generation prompt

## Tips

1. **Start Simple**: Use a clear, focused product vision
2. **Review Carefully**: Check generated documents before moving to next step
3. **Use Feedback**: Provide specific, actionable feedback for best results
4. **Iterate**: Don't expect perfection on first generation
5. **Mix Providers**: Different agents can use different LLM providers
6. **Save API Keys**: Use `.env` file to avoid setting environment variables each time

## Example Vision

Good product vision example:

```
Build a task management application for remote teams that enables seamless
collaboration, real-time updates, and progress tracking. The app should support
multiple projects, team member assignments, deadline tracking, and basic reporting.
Target users are small to medium-sized remote teams (5-50 people) in tech companies.

Key features:
- Project and task management
- Team collaboration (comments, mentions)
- Real-time notifications
- Mobile-responsive design
- Basic analytics and reporting

Success metrics:
- 1000 active users within 6 months
- 70% user retention rate
- Average session duration of 15+ minutes
```

## Troubleshooting

### Issue: "Config file not found"
**Solution**: Make sure `product.config.json` is in your project root directory.

### Issue: "API key not found"
**Solution**: Set environment variables or create `.env` file with API keys.

### Issue: "BAML validation error"
**Solution**: The LLM output doesn't match expected schema. Try regenerating or using a different model.

### Issue: "Feedback not being incorporated"
**Solution**: Make sure feedback file path is `docs/product/conversations/feedback/[brd|design|tickets]-feedback.md`

## Next Steps

1. Copy this template to your project
2. Edit `product.config.json` with your product vision
3. Set up API keys
4. Run the scripts in order: BRD → Design → Tickets
5. Review outputs and use feedback loop for refinement
6. Use generated tickets for sprint planning!
