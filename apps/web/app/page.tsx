'use client';

import { useState, useEffect } from 'react';
import PipelineCanvas from '@/components/pipeline/PipelineCanvas';
import DocumentViewer from '@/components/documents/DocumentViewer';
import SettingsModal from '@/components/settings/SettingsModal';
import { usePipelineStore } from '@/lib/store/pipelineStore';
import { pipelineApi } from '@/lib/api/pipelineApi';
import { useWebSocket } from '@/hooks/useWebSocket';
import { hasAPIKeys, getAPIKeyEnvMap } from '@/lib/utils/apiKeys';
import { Settings } from 'lucide-react';

export default function Home() {
  const { vision, setVision, llmProvider, setLLMProvider, isExecuting, setIsExecuting, setNodeStatus, setCurrentTaskId, currentTaskId } = usePipelineStore();
  const [error, setError] = useState<string | null>(null);
  const [showDocuments, setShowDocuments] = useState(false);
  const [showSettings, setShowSettings] = useState(false);
  const [hasKeys, setHasKeys] = useState(false);

  useEffect(() => {
    setHasKeys(hasAPIKeys());
  }, [showSettings]);

  // WebSocket connection for real-time updates
  useWebSocket({
    taskId: currentTaskId || '',
    onMessage: (message) => {
      console.log('WebSocket message:', message);

      // Parse the step from the message or use a default
      const step = message.result?.step || 'brd'; // Fallback to brd

      // Update node status based on message
      if (message.type === 'progress') {
        setNodeStatus(step, 'running', message.progress, message.message);
      } else if (message.type === 'complete') {
        setNodeStatus(step, 'completed', 100, message.message);
      } else if (message.type === 'error') {
        setNodeStatus(step, 'failed', 0, message.error);
      }
    },
  });

  const handleRunPipeline = async () => {
    if (!vision.trim()) {
      setError('Please enter a product vision');
      return;
    }

    if (!hasAPIKeys()) {
      setError('Please configure your API keys in Settings first');
      setShowSettings(true);
      return;
    }

    setError(null);
    setIsExecuting(true);

    try {
      // Get API keys from localStorage
      const apiKeyEnvMap = getAPIKeyEnvMap();

      // Execute BRD step with API keys
      const brdResponse = await pipelineApi.executeStep({
        config: {
          vision,
          output_dir: 'docs/product',
          // Send API keys with request
          api_keys: apiKeyEnvMap,
        },
        step: 'brd',
      });

      setCurrentTaskId(brdResponse.task_id);

      // Wait for BRD completion (you could also poll or use WebSocket)
      // For now, we'll rely on WebSocket updates

    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to start pipeline');
      setIsExecuting(false);
    }
  };

  return (
    <div className="flex flex-col h-screen">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 px-6 py-4 flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">
            Product Pipeline Toolkit
          </h1>
          <p className="text-sm text-gray-600">
            Vision → BRD → Design → Tickets
          </p>
        </div>
        <button
          onClick={() => setShowSettings(true)}
          className="flex items-center gap-2 px-4 py-2 text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
        >
          <Settings className="w-4 h-4" />
          Settings
        </button>
      </header>

      {/* Main Content */}
      <main className="flex-1 flex">
        {/* Sidebar */}
        <aside className="w-80 bg-white border-r border-gray-200 p-6 overflow-y-auto">
          <div className="space-y-6">
            {/* Vision Editor */}
            <div>
              <h2 className="text-lg font-semibold text-gray-900 mb-3">
                Product Vision
              </h2>
              <textarea
                className="w-full h-32 p-3 border border-gray-300 rounded-lg resize-none focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Enter your product vision..."
                value={vision}
                onChange={(e) => setVision(e.target.value)}
                disabled={isExecuting}
              />
            </div>

            {/* LLM Config */}
            <div>
              <h2 className="text-lg font-semibold text-gray-900 mb-3">
                LLM Configuration
              </h2>
              <div className="space-y-3">
                <select
                  className="w-full p-2 border border-gray-300 rounded-lg"
                  value={llmProvider}
                  onChange={(e) => setLLMProvider(e.target.value)}
                  disabled={isExecuting}
                >
                  <option value="gemini">Gemini 2.0 Flash</option>
                  <option value="claude">Claude Sonnet 4</option>
                  <option value="openai">GPT-4o</option>
                </select>
              </div>
            </div>

            {/* Actions */}
            <div className="space-y-2">
              {!hasKeys && (
                <div className="p-3 bg-amber-50 border border-amber-200 rounded-lg mb-2">
                  <p className="text-xs text-amber-800">
                    ⚠️ Configure API keys in Settings to run the pipeline
                  </p>
                </div>
              )}
              <button
                className="w-full bg-blue-600 text-white py-2 px-4 rounded-lg hover:bg-blue-700 transition-colors disabled:bg-gray-400 disabled:cursor-not-allowed"
                onClick={handleRunPipeline}
                disabled={isExecuting || !hasKeys}
              >
                {isExecuting ? 'Running...' : 'Run Pipeline'}
              </button>
              <button
                className="w-full bg-gray-200 text-gray-700 py-2 px-4 rounded-lg hover:bg-gray-300 transition-colors"
                onClick={() => setShowDocuments(true)}
              >
                View Documents
              </button>
            </div>

            {/* Error Display */}
            {error && (
              <div className="p-3 bg-red-50 border border-red-200 rounded-lg">
                <p className="text-sm text-red-600">{error}</p>
              </div>
            )}
          </div>
        </aside>

        {/* Pipeline Canvas */}
        <div className="flex-1">
          <PipelineCanvas />
        </div>
      </main>

      {/* Document Viewer Modal */}
      <DocumentViewer isOpen={showDocuments} onClose={() => setShowDocuments(false)} />

      {/* Settings Modal */}
      <SettingsModal isOpen={showSettings} onClose={() => setShowSettings(false)} />
    </div>
  );
}
