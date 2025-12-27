'use client';

import { useState, useEffect } from 'react';
import PipelineCanvas from '@/components/pipeline/PipelineCanvas';
import DocumentViewer from '@/components/documents/DocumentViewer';
import SettingsModal from '@/components/settings/SettingsModal';
import { usePipelineStore } from '@/lib/store/pipelineStore';
import { pipelineApi } from '@/lib/api/pipelineApi';
import { useWebSocket } from '@/hooks/useWebSocket';
import { hasAPIKeys } from '@/lib/utils/apiKeys';
import { Settings } from 'lucide-react';

export default function Home() {
  const { vision, setVision, llmProvider, setLLMProvider, isExecuting, setIsExecuting, setNodeStatus, setCurrentTaskId, currentTaskId, nodes } = usePipelineStore();
  const [error, setError] = useState<string | null>(null);
  const [showDocuments, setShowDocuments] = useState(false);
  const [showSettings, setShowSettings] = useState(false);
  const [hasKeys, setHasKeys] = useState(false);
  const [logs, setLogs] = useState<Array<{ step: string; message: string; timestamp: Date }>>([]);

  useEffect(() => {
    setHasKeys(hasAPIKeys());
  }, [showSettings]);

  // WebSocket connection for real-time updates
  useWebSocket({
    taskId: currentTaskId || '',
    onMessage: (message) => {
      console.log('WebSocket message:', message);

      // Parse the step from the message or use a default
      const step = message.result?.step || 'prd'; // Fallback to prd

      // Add log entry
      const logMessage = message.message || message.error || 'Processing...';
      setLogs((prev) => [...prev, {
        step: step.toUpperCase(),
        message: logMessage,
        timestamp: new Date()
      }]);

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

  const handleRunStep = async (step: 'prd' | 'design' | 'tickets') => {
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
      // Parse provider and model from llmProvider
      let provider = 'gemini';
      let model = llmProvider;

      if (llmProvider.startsWith('claude')) {
        provider = 'claude';
      } else if (llmProvider.startsWith('gpt') || llmProvider.startsWith('o1')) {
        provider = 'openai';
      } else if (llmProvider.startsWith('gemini')) {
        provider = 'gemini';
      }

      const config = {
        vision,
        output_dir: 'docs/product',
        llm: {
          strategist: { provider, model },
          designer: { provider, model },
          po: { provider, model },
        },
      };

      // Execute the specified step
      const response = await pipelineApi.executeStep({
        config,
        step,
      });

      setCurrentTaskId(response.task_id);

    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to start pipeline step');
      setIsExecuting(false);
    }
  };

  // Run all steps sequentially
  const handleRunAll = async () => {
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
      // Parse provider and model from llmProvider
      let provider = 'gemini';
      let model = llmProvider;

      if (llmProvider.startsWith('claude')) {
        provider = 'claude';
      } else if (llmProvider.startsWith('gpt') || llmProvider.startsWith('o1')) {
        provider = 'openai';
      } else if (llmProvider.startsWith('gemini')) {
        provider = 'gemini';
      }

      const config = {
        vision,
        output_dir: 'docs/product',
        llm: {
          strategist: { provider, model },
          designer: { provider, model },
          po: { provider, model },
        },
      };

      // Helper function to wait for task completion
      const waitForCompletion = async (taskId: string): Promise<void> => {
        return new Promise((resolve, reject) => {
          const pollInterval = setInterval(async () => {
            try {
              const status = await pipelineApi.getStatus(taskId);

              if (status.status === 'completed') {
                clearInterval(pollInterval);
                resolve();
              } else if (status.status === 'failed') {
                clearInterval(pollInterval);
                reject(new Error(status.error || 'Task failed'));
              }
            } catch (error) {
              clearInterval(pollInterval);
              reject(error);
            }
          }, 1000); // Poll every second
        });
      };

      // Execute PRD step
      const prdResponse = await pipelineApi.executeStep({ config, step: 'prd' });
      setCurrentTaskId(prdResponse.task_id);
      await waitForCompletion(prdResponse.task_id);

      // Execute Design step
      const designResponse = await pipelineApi.executeStep({ config, step: 'design' });
      setCurrentTaskId(designResponse.task_id);
      await waitForCompletion(designResponse.task_id);

      // Execute Tickets step
      const ticketsResponse = await pipelineApi.executeStep({ config, step: 'tickets' });
      setCurrentTaskId(ticketsResponse.task_id);
      await waitForCompletion(ticketsResponse.task_id);

      // All steps completed
      setIsExecuting(false);

    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to run full pipeline');
      setIsExecuting(false);
    }
  };

  // Run individual step (for node buttons)
  const handleRunPipeline = handleRunAll;

  return (
    <div className="flex flex-col h-screen">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 px-6 py-4 flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">
            Product Pipeline Toolkit
          </h1>
          <p className="text-sm text-gray-600">
            Vision → PRD → Design → Tickets
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
                className="w-full h-32 p-3 border border-gray-300 rounded-lg resize-none focus:outline-none focus:ring-2 focus:ring-blue-500 text-gray-900"
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
                  className="w-full p-2 border border-gray-300 rounded-lg text-gray-900"
                  value={llmProvider}
                  onChange={(e) => setLLMProvider(e.target.value)}
                  disabled={isExecuting}
                >
                  <optgroup label="Gemini (Google)">
                    <option value="gemini-3-flash-preview">Gemini 3 Flash Preview (Default)</option>
                    <option value="gemini-2.5-pro">Gemini 2.5 Pro</option>
                    <option value="gemini-2.5-flash">Gemini 2.5 Flash</option>
                    <option value="gemini-2.0-flash-exp">Gemini 2.0 Flash Exp</option>
                    <option value="gemini-2.0-flash-thinking-exp-01-21">Gemini 2.0 Flash Thinking</option>
                    <option value="gemini-1.5-pro">Gemini 1.5 Pro</option>
                    <option value="gemini-1.5-flash">Gemini 1.5 Flash</option>
                  </optgroup>
                  <optgroup label="Claude (Anthropic)">
                    <option value="claude-sonnet-4-20250514">Claude Sonnet 4</option>
                    <option value="claude-opus-4-20250514">Claude Opus 4</option>
                    <option value="claude-3-7-sonnet-20250219">Claude 3.7 Sonnet</option>
                    <option value="claude-3-5-haiku-20241022">Claude 3.5 Haiku</option>
                  </optgroup>
                  <optgroup label="OpenAI">
                    <option value="gpt-4o">GPT-4o</option>
                    <option value="gpt-4o-mini">GPT-4o Mini</option>
                    <option value="gpt-4-turbo">GPT-4 Turbo</option>
                    <option value="o1">O1</option>
                    <option value="o1-mini">O1 Mini</option>
                  </optgroup>
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
                onClick={handleRunAll}
                disabled={isExecuting || !hasKeys}
              >
                {isExecuting ? 'Running...' : 'Run All Steps'}
              </button>
              <div className="text-xs text-center text-gray-500 py-1">
                or click individual nodes to run steps separately
              </div>
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

            {/* Live Logs */}
            {logs.length > 0 && (
              <div>
                <h2 className="text-lg font-semibold text-gray-900 mb-3">
                  Live Logs
                </h2>
                <div className="bg-gray-900 rounded-lg p-3 max-h-64 overflow-y-auto font-mono text-xs">
                  {logs.map((log, idx) => (
                    <div key={idx} className="mb-1">
                      <span className="text-blue-400">[{log.step}]</span>{' '}
                      <span className="text-gray-300">{log.message}</span>
                    </div>
                  ))}
                </div>
                <button
                  onClick={() => setLogs([])}
                  className="mt-2 text-xs text-gray-500 hover:text-gray-700"
                >
                  Clear logs
                </button>
              </div>
            )}

            {/* Current Status Messages */}
            {isExecuting && (
              <div className="space-y-2">
                <h2 className="text-lg font-semibold text-gray-900">Status</h2>
                {Object.entries(nodes).map(([key, node]) =>
                  node.message && node.status === 'running' ? (
                    <div key={key} className="p-2 bg-blue-50 border border-blue-200 rounded text-xs">
                      <div className="font-semibold text-blue-900">{key.toUpperCase()}</div>
                      <div className="text-blue-700">{node.message}</div>
                    </div>
                  ) : null
                )}
              </div>
            )}
          </div>
        </aside>

        {/* Pipeline Canvas */}
        <div className="flex-1">
          <PipelineCanvas onRunStep={handleRunStep} />
        </div>
      </main>

      {/* Document Viewer Modal */}
      <DocumentViewer isOpen={showDocuments} onClose={() => setShowDocuments(false)} />

      {/* Settings Modal */}
      <SettingsModal isOpen={showSettings} onClose={() => setShowSettings(false)} />
    </div>
  );
}
