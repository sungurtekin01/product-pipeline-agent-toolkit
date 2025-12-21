/**
 * Client-side API key management
 * Keys are stored in localStorage and never sent to our servers
 */

export interface APIKeys {
  gemini?: string;
  anthropic?: string;
  openai?: string;
}

const STORAGE_KEY = 'api_keys';

/**
 * Get API keys from localStorage
 */
export function getAPIKeys(): APIKeys {
  if (typeof window === 'undefined') return {};

  try {
    const stored = localStorage.getItem(STORAGE_KEY);
    return stored ? JSON.parse(stored) : {};
  } catch (error) {
    console.error('Failed to load API keys:', error);
    return {};
  }
}

/**
 * Save API keys to localStorage
 */
export function saveAPIKeys(keys: APIKeys): void {
  if (typeof window === 'undefined') return;

  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(keys));
  } catch (error) {
    console.error('Failed to save API keys:', error);
  }
}

/**
 * Check if user has configured any API keys
 */
export function hasAPIKeys(): boolean {
  const keys = getAPIKeys();
  return !!(keys.gemini || keys.anthropic || keys.openai);
}

/**
 * Get API key for a specific provider
 */
export function getProviderKey(provider: 'gemini' | 'anthropic' | 'openai'): string | undefined {
  const keys = getAPIKeys();
  return keys[provider];
}

/**
 * Clear all API keys from localStorage
 */
export function clearAPIKeys(): void {
  if (typeof window === 'undefined') return;

  try {
    localStorage.removeItem(STORAGE_KEY);
  } catch (error) {
    console.error('Failed to clear API keys:', error);
  }
}

/**
 * Get API key environment variable names for backend
 */
export function getAPIKeyEnvMap(): Record<string, string> {
  const keys = getAPIKeys();
  const envMap: Record<string, string> = {};

  if (keys.gemini) envMap.GEMINI_API_KEY = keys.gemini;
  if (keys.anthropic) envMap.ANTHROPIC_API_KEY = keys.anthropic;
  if (keys.openai) envMap.OPENAI_API_KEY = keys.openai;

  return envMap;
}
