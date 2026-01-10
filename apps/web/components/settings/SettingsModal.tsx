'use client';

import { useState, useEffect } from 'react';
import { X, Save, Eye, EyeOff, AlertCircle, CheckCircle2, ExternalLink, Trash2 } from 'lucide-react';

interface SettingsModalProps {
  isOpen: boolean;
  onClose: () => void;
}

interface APIKeys {
  gemini: string;
  anthropic: string;
  openai: string;
}

const API_KEY_LINKS = {
  gemini: 'https://aistudio.google.com/apikey',
  anthropic: 'https://console.anthropic.com/',
  openai: 'https://platform.openai.com/api-keys',
};

export default function SettingsModal({ isOpen, onClose }: SettingsModalProps) {
  const [apiKeys, setApiKeys] = useState<APIKeys>({
    gemini: '',
    anthropic: '',
    openai: '',
  });
  const [showKeys, setShowKeys] = useState<Record<keyof APIKeys, boolean>>({
    gemini: false,
    anthropic: false,
    openai: false,
  });
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    if (isOpen) {
      loadAPIKeys();
      setSaved(false);
    }
  }, [isOpen]);

  const loadAPIKeys = () => {
    try {
      const stored = localStorage.getItem('api_keys');
      if (stored) {
        const keys = JSON.parse(stored);
        setApiKeys(keys);
      }
    } catch (error) {
      console.error('Failed to load API keys:', error);
    }
  };

  const handleSave = () => {
    try {
      localStorage.setItem('api_keys', JSON.stringify(apiKeys));
      setSaved(true);
      setTimeout(() => {
        onClose();
      }, 1500);
    } catch (error) {
      console.error('Failed to save API keys:', error);
    }
  };

  const handleClear = () => {
    if (confirm('Are you sure you want to clear all API keys? This cannot be undone.')) {
      try {
        localStorage.removeItem('api_keys');
        setApiKeys({ gemini: '', anthropic: '', openai: '' });
        setSaved(false);
      } catch (error) {
        console.error('Failed to clear API keys:', error);
      }
    }
  };

  const toggleShowKey = (provider: keyof APIKeys) => {
    setShowKeys(prev => ({ ...prev, [provider]: !prev[provider] }));
  };

  const hasAnyKey = apiKeys.gemini || apiKeys.anthropic || apiKeys.openai;

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-lg shadow-xl w-full max-w-2xl max-h-[90vh] flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <div>
            <h2 className="text-2xl font-bold text-gray-900">Settings</h2>
            <p className="text-sm text-gray-500 mt-1">Configure your LLM API keys</p>
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <X className="w-5 h-5 text-gray-500" />
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6">
          {/* Security Notice */}
          <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
            <div className="flex items-start gap-3">
              <AlertCircle className="w-5 h-5 text-blue-600 mt-0.5 flex-shrink-0" />
              <div className="text-sm">
                <p className="font-semibold text-blue-900">Your API keys are stored locally</p>
                <p className="text-blue-700 mt-1">
                  Keys are saved in your browser's local storage and sent directly to the LLM providers.
                  They are <strong>never stored on our servers</strong>.
                </p>
              </div>
            </div>
          </div>

          {/* API Key Configuration */}
          <div className="space-y-5">
            {/* Gemini */}
            <div>
              <div className="flex items-center justify-between mb-2">
                <label className="block text-sm font-semibold text-gray-900">
                  Google Gemini API Key
                </label>
                <a
                  href={API_KEY_LINKS.gemini}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-xs text-blue-600 hover:text-blue-700 flex items-center gap-1"
                >
                  Get API Key <ExternalLink className="w-3 h-3" />
                </a>
              </div>
              <div className="relative">
                <input
                  type={showKeys.gemini ? 'text' : 'password'}
                  className="w-full px-3 py-2 pr-10 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 font-mono text-sm text-gray-900 placeholder:text-gray-400"
                  placeholder="AIza..."
                  value={apiKeys.gemini}
                  onChange={(e) => setApiKeys({ ...apiKeys, gemini: e.target.value })}
                />
                <button
                  onClick={() => toggleShowKey('gemini')}
                  className="absolute right-2 top-1/2 -translate-y-1/2 p-1.5 hover:bg-gray-100 rounded"
                >
                  {showKeys.gemini ? (
                    <EyeOff className="w-4 h-4 text-gray-500" />
                  ) : (
                    <Eye className="w-4 h-4 text-gray-500" />
                  )}
                </button>
              </div>
              <p className="text-xs text-gray-500 mt-1">
                Free tier: 60 requests/minute • Model: Gemini 2.0 Flash
              </p>
            </div>

            {/* Anthropic Claude */}
            <div>
              <div className="flex items-center justify-between mb-2">
                <label className="block text-sm font-semibold text-gray-900">
                  Anthropic API Key (Claude)
                </label>
                <a
                  href={API_KEY_LINKS.anthropic}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-xs text-blue-600 hover:text-blue-700 flex items-center gap-1"
                >
                  Get API Key <ExternalLink className="w-3 h-3" />
                </a>
              </div>
              <div className="relative">
                <input
                  type={showKeys.anthropic ? 'text' : 'password'}
                  className="w-full px-3 py-2 pr-10 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 font-mono text-sm text-gray-900 placeholder:text-gray-400"
                  placeholder="sk-ant-..."
                  value={apiKeys.anthropic}
                  onChange={(e) => setApiKeys({ ...apiKeys, anthropic: e.target.value })}
                />
                <button
                  onClick={() => toggleShowKey('anthropic')}
                  className="absolute right-2 top-1/2 -translate-y-1/2 p-1.5 hover:bg-gray-100 rounded"
                >
                  {showKeys.anthropic ? (
                    <EyeOff className="w-4 h-4 text-gray-500" />
                  ) : (
                    <Eye className="w-4 h-4 text-gray-500" />
                  )}
                </button>
              </div>
              <p className="text-xs text-gray-500 mt-1">
                $5 free credit • Model: Claude Sonnet 4
              </p>
            </div>

            {/* OpenAI */}
            <div>
              <div className="flex items-center justify-between mb-2">
                <label className="block text-sm font-semibold text-gray-900">
                  OpenAI API Key
                </label>
                <a
                  href={API_KEY_LINKS.openai}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-xs text-blue-600 hover:text-blue-700 flex items-center gap-1"
                >
                  Get API Key <ExternalLink className="w-3 h-3" />
                </a>
              </div>
              <div className="relative">
                <input
                  type={showKeys.openai ? 'text' : 'password'}
                  className="w-full px-3 py-2 pr-10 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 font-mono text-sm text-gray-900 placeholder:text-gray-400"
                  placeholder="sk-..."
                  value={apiKeys.openai}
                  onChange={(e) => setApiKeys({ ...apiKeys, openai: e.target.value })}
                />
                <button
                  onClick={() => toggleShowKey('openai')}
                  className="absolute right-2 top-1/2 -translate-y-1/2 p-1.5 hover:bg-gray-100 rounded"
                >
                  {showKeys.openai ? (
                    <EyeOff className="w-4 h-4 text-gray-500" />
                  ) : (
                    <Eye className="w-4 h-4 text-gray-500" />
                  )}
                </button>
              </div>
              <p className="text-xs text-gray-500 mt-1">
                $5 free credit (new accounts) • Model: GPT-4o
              </p>
            </div>
          </div>

          {/* Info */}
          <div className="pt-4 border-t border-gray-200">
            <p className="text-sm text-gray-600">
              <strong>Note:</strong> You need at least one API key to use the pipeline. We recommend starting with
              Gemini (fastest and free tier available).
            </p>
          </div>

          {/* Success Message */}
          {saved && (
            <div className="p-3 bg-green-50 border border-green-200 rounded-lg flex items-center gap-2">
              <CheckCircle2 className="w-5 h-5 text-green-600" />
              <p className="text-sm font-medium text-green-800">Settings saved successfully!</p>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="flex items-center justify-between p-6 border-t border-gray-200 bg-gray-50">
          <button
            onClick={handleClear}
            className="flex items-center gap-2 px-4 py-2 text-red-700 bg-white border border-red-300 rounded-lg hover:bg-red-50 transition-colors"
          >
            <Trash2 className="w-4 h-4" />
            Clear All Keys
          </button>
          <div className="flex items-center gap-3">
            <button
              onClick={onClose}
              className="px-4 py-2 text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
            >
              Cancel
            </button>
            <button
              onClick={handleSave}
              disabled={!hasAnyKey}
              className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:bg-gray-400 disabled:cursor-not-allowed"
            >
              <Save className="w-4 h-4" />
              Save Settings
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
