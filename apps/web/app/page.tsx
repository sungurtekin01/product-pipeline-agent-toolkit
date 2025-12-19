import PipelineCanvas from '@/components/pipeline/PipelineCanvas';

export default function Home() {
  return (
    <div className="flex flex-col h-screen">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 px-6 py-4">
        <h1 className="text-2xl font-bold text-gray-900">
          Product Pipeline Toolkit
        </h1>
        <p className="text-sm text-gray-600">
          Vision → BRD → Design → Tickets
        </p>
      </header>

      {/* Main Content */}
      <main className="flex-1 flex">
        {/* Sidebar */}
        <aside className="w-80 bg-white border-r border-gray-200 p-6">
          <div className="space-y-6">
            {/* Vision Editor */}
            <div>
              <h2 className="text-lg font-semibold text-gray-900 mb-3">
                Product Vision
              </h2>
              <textarea
                className="w-full h-32 p-3 border border-gray-300 rounded-lg resize-none focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Enter your product vision..."
              />
            </div>

            {/* LLM Config */}
            <div>
              <h2 className="text-lg font-semibold text-gray-900 mb-3">
                LLM Configuration
              </h2>
              <div className="space-y-3">
                <select className="w-full p-2 border border-gray-300 rounded-lg">
                  <option>Gemini 2.0 Flash</option>
                  <option>Claude Sonnet 4</option>
                  <option>GPT-4o</option>
                </select>
              </div>
            </div>

            {/* Actions */}
            <div className="space-y-2">
              <button className="w-full bg-blue-600 text-white py-2 px-4 rounded-lg hover:bg-blue-700 transition-colors">
                Run Pipeline
              </button>
              <button className="w-full bg-gray-200 text-gray-700 py-2 px-4 rounded-lg hover:bg-gray-300 transition-colors">
                View Documents
              </button>
            </div>
          </div>
        </aside>

        {/* Pipeline Canvas */}
        <div className="flex-1">
          <PipelineCanvas />
        </div>
      </main>
    </div>
  );
}
