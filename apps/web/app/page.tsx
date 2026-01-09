'use client';

import { useState, useEffect } from 'react';
import PipelineCanvas from '@/components/pipeline/PipelineCanvas';
import DocumentViewer from '@/components/documents/DocumentViewer';
import SettingsModal from '@/components/settings/SettingsModal';
import { usePipelineStore } from '@/lib/store/pipelineStore';
import { pipelineApi } from '@/lib/api/pipelineApi';
import { useWebSocket } from '@/hooks/useWebSocket';
import { hasAPIKeys, getAPIKeys } from '@/lib/utils/apiKeys';
import { Settings } from 'lucide-react';

export default function Home() {
  const {
    vision,
    setVision,
    llmProvider,
    setLLMProvider,
    isExecuting,
    setIsExecuting,
    setNodeStatus,
    setCurrentTaskId,
    currentTaskId,
    nodes,
    personaMapping,
    availablePersonas,
    setPersonaForStep,
    setAvailablePersonas,
  } = usePipelineStore();
  const [error, setError] = useState<string | null>(null);
  const [showDocuments, setShowDocuments] = useState(false);
  const [showSettings, setShowSettings] = useState(false);
  const [hasKeys, setHasKeys] = useState(false);
  const [logs, setLogs] = useState<Array<{ step: string; message: string; timestamp: Date }>>([]);
  const [visionExpanded, setVisionExpanded] = useState(false);

  // Load available personas on mount
  useEffect(() => {
    const loadPersonas = async () => {
      try {
        const personas = await pipelineApi.getPersonas();
        setAvailablePersonas(personas);
      } catch (err) {
        console.error('Failed to load personas:', err);
      }
    };
    loadPersonas();
  }, [setAvailablePersonas]);

  useEffect(() => {
    setHasKeys(hasAPIKeys());
  }, [showSettings]);

  // WebSocket connection for real-time updates
  useWebSocket({
    taskId: currentTaskId || '',
    onMessage: (message) => {
      // Parse the step from the message
      const step = message.result?.step;

      if (!step) {
        return; // Skip messages without a step
      }

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
        api_keys: getAPIKeys(),
        personas: personaMapping, // Include persona selection
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
        api_keys: getAPIKeys(),
        personas: personaMapping, // Include persona selection
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

  // Handle persona selection
  const handlePersonaSelect = (step: string, personaId: string) => {
    setPersonaForStep(step, personaId);
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
        <div className="flex items-center gap-3">
          {/* LLM Provider Selector - Compact */}
          <select
            className="px-3 py-2 border border-gray-300 rounded-lg text-sm text-gray-900 focus:outline-none focus:ring-2 focus:ring-blue-500"
            value={llmProvider}
            onChange={(e) => setLLMProvider(e.target.value)}
            disabled={isExecuting}
          >
            <optgroup label="Gemini (Google)">
              <option value="gemini-3-flash-preview">Gemini 3 Flash Preview</option>
              <option value="gemini-2.5-pro">Gemini 2.5 Pro</option>
              <option value="gemini-2.5-flash">Gemini 2.5 Flash</option>
              <option value="gemini-2.0-flash-exp">Gemini 2.0 Flash Exp</option>
            </optgroup>
            <optgroup label="Claude (Anthropic)">
              <option value="claude-sonnet-4-20250514">Claude Sonnet 4</option>
              <option value="claude-opus-4-20250514">Claude Opus 4</option>
            </optgroup>
            <optgroup label="OpenAI">
              <option value="gpt-4o">GPT-4o</option>
              <option value="gpt-4o-mini">GPT-4o Mini</option>
            </optgroup>
          </select>
          <button
            onClick={() => setShowSettings(true)}
            className="flex items-center gap-2 px-4 py-2 text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
          >
            <Settings className="w-4 h-4" />
            Settings
          </button>
        </div>
      </header>

      {/* Vision Input - Collapsible */}
      <div
        className={`bg-white border-b border-gray-200 transition-all duration-300 ease-in-out ${
          visionExpanded ? 'min-h-[60vh] max-h-[70vh]' : 'h-auto'
        }`}
      >
        {!visionExpanded ? (
          // Collapsed State
          <div className="px-6 py-4">
            <div
              onClick={() => !isExecuting && setVisionExpanded(true)}
              className={`cursor-pointer ${isExecuting ? 'opacity-50' : ''}`}
            >
              <div className="flex items-center justify-between mb-2">
                <h2 className="text-sm font-semibold text-gray-700">Product Vision</h2>
                <span className="text-xs text-gray-500">Click to expand</span>
              </div>
              <div className="p-3 border-2 border-gray-300 rounded-lg hover:border-blue-400 transition-colors bg-gray-50">
                <p className="text-gray-600 text-sm truncate">
                  {vision || "Enter your product vision..."}
                </p>
              </div>
            </div>
          </div>
        ) : (
          // Expanded State - Full height
          <div className="h-full flex flex-col px-6 py-4">
            <div className="flex items-center justify-between mb-3">
              <div>
                <h2 className="text-lg font-semibold text-gray-900">Product Vision</h2>
                <p className="text-xs text-gray-500 mt-1">
                  💡 Describe what you want to build and why it matters
                </p>
              </div>
              <button
                onClick={() => setVisionExpanded(false)}
                className="px-4 py-2 bg-blue-600 text-white text-sm rounded-lg hover:bg-blue-700 transition-colors flex-shrink-0"
              >
                Done
              </button>
            </div>
            <textarea
              autoFocus
              className="flex-1 w-full p-4 border-2 border-blue-400 rounded-lg resize-none focus:outline-none focus:ring-2 focus:ring-blue-500 text-gray-900 placeholder:text-gray-400 text-base leading-relaxed overflow-y-auto"
              style={{ minHeight: '400px' }}
              placeholder="Example: A mobile app that helps remote teams stay connected through async video messages..."
              value={vision}
              onChange={(e) => setVision(e.target.value)}
              disabled={isExecuting}
            />
            <div className="flex items-center justify-between mt-3 flex-shrink-0">
              <p className="text-xs text-gray-500">
                {vision.length} characters
              </p>
              <p className="text-xs text-gray-500">
                Tip: Be specific about the problem, users, and value proposition
              </p>
            </div>
          </div>
        )}
      </div>

      {/* Main Content - Canvas */}
      <main className="flex-1 flex overflow-hidden relative">
        {/* Canvas Area */}
        <div className="flex-1 bg-gray-50 overflow-auto p-6 relative">
          {/* Error Message - Floating */}
          {error && (
            <div className="absolute top-4 left-1/2 -translate-x-1/2 z-10 p-4 bg-red-50 border border-red-200 rounded-lg shadow-lg max-w-md">
              <p className="text-red-600 text-sm">{error}</p>
            </div>
          )}

          {/* Action Buttons - Floating Top Right */}
          <div className="absolute top-4 right-4 z-10 flex gap-2">
            <button
              onClick={handleRunAll}
              disabled={isExecuting || !vision.trim()}
              className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:bg-gray-400 disabled:cursor-not-allowed shadow-md"
            >
              {isExecuting ? 'Running...' : 'Run All Steps'}
            </button>
            <button
              onClick={() => setShowDocuments(true)}
              className="flex items-center gap-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors shadow-md"
            >
              View Documents
            </button>
          </div>

          {/* Activity Logs - Floating Bottom Right */}
          {logs.length > 0 && (
            <div className="absolute bottom-4 right-4 z-10 w-96 bg-white border border-gray-200 rounded-lg shadow-lg p-4">
              <div className="flex items-center justify-between mb-2">
                <h3 className="text-sm font-semibold text-gray-900">Activity Log</h3>
                <button
                  onClick={() => setLogs([])}
                  className="text-xs text-gray-500 hover:text-gray-700"
                >
                  Clear
                </button>
              </div>
              <div className="space-y-2 max-h-64 overflow-y-auto">
                {logs.slice(-10).reverse().map((log, idx) => (
                  <div key={idx} className="p-2 bg-gray-50 border border-gray-200 rounded text-xs">
                    <div className="flex items-center gap-2">
                      <span className="font-semibold text-blue-600">{log.step}</span>
                      <span className="text-gray-400">•</span>
                      <span className="text-gray-500">
                        {log.timestamp.toLocaleTimeString()}
                      </span>
                    </div>
                    <p className="text-gray-700 mt-1">{log.message}</p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Pipeline Canvas */}
          <PipelineCanvas
            onRunStep={handleRunStep}
            availablePersonas={availablePersonas}
            personaMapping={personaMapping}
            onPersonaSelect={handlePersonaSelect}
          />
        </div>
      </main>

      {/* Document Viewer Modal */}
      <DocumentViewer isOpen={showDocuments} onClose={() => setShowDocuments(false)} />

      {/* Settings Modal */}
      <SettingsModal isOpen={showSettings} onClose={() => setShowSettings(false)} />
    </div>
  );
}
