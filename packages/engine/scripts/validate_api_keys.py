"""
API Key Validation Script

Validates that BAML clients can authenticate with configured LLM providers.
Tests all providers that have API keys in .env file.
"""

import sys
import os
from pathlib import Path

# Add engine to Python path
ENGINE_PATH = Path(__file__).parent.parent
sys.path.insert(0, str(ENGINE_PATH))

from dotenv import load_dotenv

# Load environment variables
env_file = Path(__file__).parent.parent.parent.parent / ".env"
load_dotenv(env_file)


def check_api_keys():
    """Check which API keys are configured in .env"""
    providers = {
        "gemini": os.getenv("GEMINI_API_KEY"),
        "claude": os.getenv("ANTHROPIC_API_KEY"),
        "openai": os.getenv("OPENAI_API_KEY"),
    }

    configured = {}
    missing = []

    for provider, key in providers.items():
        if key:
            configured[provider] = key
        else:
            missing.append(provider)

    return configured, missing


def validate_gemini_key(api_key: str) -> bool:
    """Validate Gemini API key by making a test request"""
    try:
        import google.generativeai as genai

        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-2.0-flash-exp")

        # Simple test prompt
        response = model.generate_content("Say 'test' and nothing else")

        if response.text:
            print("✅ Gemini API key validated successfully")
            return True
        else:
            print("❌ Gemini API key validation failed: Empty response")
            return False

    except Exception as e:
        print(f"❌ Gemini API key validation failed: {str(e)}")
        return False


def validate_claude_key(api_key: str) -> bool:
    """Validate Anthropic Claude API key by making a test request"""
    try:
        import anthropic

        client = anthropic.Anthropic(api_key=api_key)

        # Simple test prompt
        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=10,
            messages=[{"role": "user", "content": "Say 'test' and nothing else"}],
        )

        if message.content:
            print("✅ Claude API key validated successfully")
            return True
        else:
            print("❌ Claude API key validation failed: Empty response")
            return False

    except Exception as e:
        print(f"❌ Claude API key validation failed: {str(e)}")
        return False


def validate_openai_key(api_key: str) -> bool:
    """Validate OpenAI API key by making a test request"""
    try:
        from openai import OpenAI

        client = OpenAI(api_key=api_key)

        # Simple test prompt
        response = client.chat.completions.create(
            model="gpt-4o",
            max_tokens=10,
            messages=[{"role": "user", "content": "Say 'test' and nothing else"}],
        )

        if response.choices:
            print("✅ OpenAI API key validated successfully")
            return True
        else:
            print("❌ OpenAI API key validation failed: Empty response")
            return False

    except Exception as e:
        print(f"❌ OpenAI API key validation failed: {str(e)}")
        return False


def main():
    """Main validation function"""
    print("=" * 60)
    print("API Key Validation for BAML Clients")
    print("=" * 60)
    print()

    configured, missing = check_api_keys()

    if missing:
        print(f"⚠️  Missing API keys for: {', '.join(missing)}")
        print("   (This is OK - only configured providers will be tested)")
        print()

    if not configured:
        print("❌ No API keys configured in .env file")
        print()
        print("Please add at least one API key to .env:")
        print("  GEMINI_API_KEY=your_key_here")
        print("  ANTHROPIC_API_KEY=your_key_here")
        print("  OPENAI_API_KEY=your_key_here")
        sys.exit(1)

    print(f"Testing {len(configured)} configured provider(s)...")
    print()

    validators = {
        "gemini": validate_gemini_key,
        "claude": validate_claude_key,
        "openai": validate_openai_key,
    }

    results = {}
    for provider, api_key in configured.items():
        print(f"Testing {provider.upper()}...")
        validator = validators[provider]
        results[provider] = validator(api_key)
        print()

    # Summary
    print("=" * 60)
    print("Validation Summary")
    print("=" * 60)

    passed = [p for p, r in results.items() if r]
    failed = [p for p, r in results.items() if not r]

    if passed:
        print(f"✅ Passed: {', '.join(passed)}")

    if failed:
        print(f"❌ Failed: {', '.join(failed)}")

    if missing:
        print(f"⚠️  Not tested (no API key): {', '.join(missing)}")

    print()

    if failed:
        print("⚠️  Some providers failed validation. Check API keys in .env")
        sys.exit(1)
    else:
        print("✅ All configured providers validated successfully!")
        sys.exit(0)


if __name__ == "__main__":
    main()
