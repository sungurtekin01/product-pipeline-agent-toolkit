// ============================================================================
// BAML Client Definitions - Product Pipeline Toolkit
// ============================================================================
//
// This file defines 6 BAML clients total:
// - 3 Provider Clients: One per LLM provider (Gemini, Claude, OpenAI)
// - 3 Function Clients: One per persona role (Strategist, Designer, PO)
//
// Design Principle: NO hardcoded persona-to-provider mappings
// - Any persona can use any provider at runtime
// - ClientRegistry maps function clients to provider clients dynamically
// - API keys from .env file
// - Model selection eventually from UI → API → ClientRegistry
//
// ============================================================================

// ============================================================================
// Provider Clients (one per provider, NOT tied to personas)
// ============================================================================

client<llm> GeminiClient {
  provider google-ai
  options {
    model "gemini-2.0-flash-exp"  // default, overridable at runtime
    api_key env.GEMINI_API_KEY
  }
}

client<llm> ClaudeClient {
  provider anthropic
  options {
    model "claude-sonnet-4-20250514"  // default, overridable at runtime
    api_key env.ANTHROPIC_API_KEY
  }
}

client<llm> OpenAIClient {
  provider openai
  options {
    model "gpt-4o"  // default, overridable at runtime
    api_key env.OPENAI_API_KEY
  }
}

// ============================================================================
// Function Client Aliases (used by BAML functions, mapped at runtime)
// ============================================================================
//
// These clients are used by BAML functions and can be overridden at runtime
// via ClientRegistry to use any provider client above.
//
// Default: All use Gemini
// Future: ClientRegistry maps based on API parameters (eventually from UI)
//
// Example runtime mapping:
//   {"StrategistClient": "ClaudeClient"} → Uses Claude for BRD generation
//
// ============================================================================

client<llm> StrategistClient {
  provider google-ai  // default provider
  options {
    model "gemini-2.0-flash-exp"
    api_key env.GEMINI_API_KEY
  }
}

client<llm> DesignerClient {
  provider google-ai  // default provider
  options {
    model "gemini-2.0-flash-exp"
    api_key env.GEMINI_API_KEY
  }
}

client<llm> POClient {
  provider google-ai  // default provider
  options {
    model "gemini-2.0-flash-exp"
    api_key env.GEMINI_API_KEY
  }
}
