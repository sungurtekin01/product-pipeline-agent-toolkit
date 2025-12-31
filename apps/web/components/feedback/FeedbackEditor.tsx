'use client';

import { useState, useEffect } from 'react';
import { X, Save, AlertCircle, CheckCircle2 } from 'lucide-react';
import { pipelineApi } from '@/lib/api/pipelineApi';

interface FeedbackEditorProps {
  isOpen: boolean;
  onClose: () => void;
  step: 'prd' | 'design' | 'tickets';
  stepLabel: string;
}

export default function FeedbackEditor({ isOpen, onClose, step, stepLabel }: FeedbackEditorProps) {
  const [feedback, setFeedback] = useState('');
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  useEffect(() => {
    if (isOpen) {
      loadExistingFeedback();
      setSuccess(false);
      setError(null);
    }
  }, [isOpen, step]);

  const loadExistingFeedback = async () => {
    setLoading(true);
    setError(null);

    try {
      const result = await pipelineApi.getFeedback(step);
      setFeedback(result.feedback || '');
    } catch (err) {
      console.error('Failed to load existing feedback:', err);
      setFeedback('');
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    if (!feedback.trim()) {
      setError('Please enter some feedback before saving');
      return;
    }

    setSaving(true);
    setError(null);
    setSuccess(false);

    try {
      await pipelineApi.saveFeedback({
        step,
        feedback: feedback.trim(),
      });

      setSuccess(true);
      setTimeout(() => {
        onClose();
      }, 1500);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to save feedback');
    } finally {
      setSaving(false);
    }
  };

  if (!isOpen) return null;

  const feedbackPrompts = {
    prd: [
      'Are any key requirements missing?',
      'Are the user stories clear and complete?',
      'Are the success metrics well-defined?',
      'Do the non-functional requirements need adjustment?',
    ],
    design: [
      'Are the UI/UX designs clear and intuitive?',
      'Are any screen flows missing or unclear?',
      'Do the design patterns align with best practices?',
      'Are accessibility considerations addressed?',
    ],
    tickets: [
      'Are the tickets clear and actionable?',
      'Are any dependencies or blockers missing?',
      'Are acceptance criteria well-defined?',
      'Is the scope of each ticket appropriate?',
    ],
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-lg shadow-xl w-full max-w-3xl max-h-[90vh] flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-gray-200">
          <div>
            <h2 className="text-xl font-semibold text-gray-900">Provide Feedback</h2>
            <p className="text-sm text-gray-500 mt-1">For {stepLabel}</p>
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <X className="w-5 h-5 text-gray-500" />
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-6">
          {loading ? (
            <div className="flex items-center justify-center py-8">
              <div className="text-gray-500">Loading existing feedback...</div>
            </div>
          ) : (
            <>
              {/* Prompts */}
              <div className="mb-6">
                <h3 className="text-sm font-semibold text-gray-700 mb-3">
                  Things to consider:
                </h3>
                <ul className="space-y-2">
                  {feedbackPrompts[step].map((prompt, idx) => (
                    <li key={idx} className="flex items-start gap-2 text-sm text-gray-600">
                      <span className="text-blue-600 mt-0.5">•</span>
                      <span>{prompt}</span>
                    </li>
                  ))}
                </ul>
              </div>

              {/* Feedback Input */}
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">
                  Your Feedback
                </label>
                <textarea
                  className="w-full h-64 p-3 border border-gray-300 rounded-lg resize-none focus:outline-none focus:ring-2 focus:ring-blue-500 font-mono text-sm text-gray-900 placeholder:text-gray-400"
                  placeholder={`Enter your feedback for the ${stepLabel} here. Be specific about what needs improvement or what's missing.\n\nFor example:\n- Add more details about the authentication flow\n- Include error handling requirements\n- Clarify the scope of the MVP\n\nWhen you save this feedback and re-run the pipeline, the AI will incorporate your suggestions.`}
                  value={feedback}
                  onChange={(e) => setFeedback(e.target.value)}
                  disabled={saving}
                />
                <p className="text-xs text-gray-500 mt-2">
                  Supports markdown formatting. Be specific and constructive.
                </p>
              </div>

              {/* Success Message */}
              {success && (
                <div className="mt-4 p-3 bg-green-50 border border-green-200 rounded-lg flex items-start gap-2">
                  <CheckCircle2 className="w-5 h-5 text-green-600 mt-0.5" />
                  <div>
                    <p className="text-sm font-medium text-green-800">Feedback saved successfully!</p>
                    <p className="text-xs text-green-600 mt-1">
                      Re-run the pipeline to incorporate this feedback.
                    </p>
                  </div>
                </div>
              )}

              {/* Error Message */}
              {error && (
                <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded-lg flex items-start gap-2">
                  <AlertCircle className="w-5 h-5 text-red-600 mt-0.5" />
                  <p className="text-sm text-red-600">{error}</p>
                </div>
              )}
            </>
          )}
        </div>

        {/* Footer */}
        <div className="flex items-center justify-between p-4 border-t border-gray-200 bg-gray-50">
          <div className="text-sm text-gray-600">
            Feedback will be saved to: <code className="text-xs bg-gray-200 px-1.5 py-0.5 rounded">conversations/feedback/{step}-feedback.md</code>
          </div>
          <div className="flex gap-2">
            <button
              onClick={onClose}
              disabled={saving}
              className="px-4 py-2 text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors disabled:opacity-50"
            >
              Cancel
            </button>
            <button
              onClick={handleSave}
              disabled={saving || !feedback.trim()}
              className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:bg-gray-400 disabled:cursor-not-allowed text-sm"
            >
              <Save className="w-4 h-4" />
              {saving ? 'Saving...' : 'Save'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
