'use client';

import { useState, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { X, Download, FileText, MessageSquare } from 'lucide-react';
import { pipelineApi, Document } from '@/lib/api/pipelineApi';

interface DocumentViewerProps {
  isOpen: boolean;
  onClose: () => void;
}

type TabType = 'brd' | 'design' | 'tickets';
type ViewMode = 'document' | 'qa';

export default function DocumentViewer({ isOpen, onClose }: DocumentViewerProps) {
  const [activeTab, setActiveTab] = useState<TabType>('brd');
  const [viewMode, setViewMode] = useState<ViewMode>('document');
  const [document, setDocument] = useState<Document | null>(null);
  const [qaDoc, setQADoc] = useState<Document | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [availableDocs, setAvailableDocs] = useState<any>(null);

  useEffect(() => {
    if (isOpen) {
      loadAvailableDocuments();
      loadDocument(activeTab);
    }
  }, [isOpen, activeTab]);

  const loadAvailableDocuments = async () => {
    try {
      const list = await pipelineApi.listDocuments();
      setAvailableDocs(list.documents);
    } catch (err) {
      console.error('Failed to load document list:', err);
    }
  };

  const loadDocument = async (step: TabType) => {
    setLoading(true);
    setError(null);
    setViewMode('document');

    try {
      const doc = await pipelineApi.getDocument(step);
      setDocument(doc);

      // Try to load Q&A if available (not for BRD)
      if (step !== 'brd') {
        try {
          const qa = await pipelineApi.getQAConversation(step);
          setQADoc(qa);
        } catch {
          setQADoc(null);
        }
      } else {
        setQADoc(null);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load document');
      setDocument(null);
      setQADoc(null);
    } finally {
      setLoading(false);
    }
  };

  const handleDownload = () => {
    if (!document) return;

    const content = viewMode === 'qa' && qaDoc ? qaDoc.content : document.content;
    const fileName = viewMode === 'qa' && qaDoc ? qaDoc.file_name : document.file_name;

    const blob = new Blob([content], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = window.document.createElement('a');
    a.href = url;
    a.download = fileName;
    a.click();
    URL.revokeObjectURL(url);
  };

  if (!isOpen) return null;

  const tabs: { id: TabType; label: string; icon: typeof FileText }[] = [
    { id: 'brd', label: 'BRD', icon: FileText },
    { id: 'design', label: 'Design Spec', icon: FileText },
    { id: 'tickets', label: 'Tickets', icon: FileText },
  ];

  const currentDoc = viewMode === 'qa' && qaDoc ? qaDoc : document;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-lg shadow-xl w-full max-w-6xl h-[90vh] flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-gray-200">
          <h2 className="text-xl font-semibold text-gray-900">Generated Documents</h2>
          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <X className="w-5 h-5 text-gray-500" />
          </button>
        </div>

        {/* Tabs */}
        <div className="flex items-center border-b border-gray-200 px-4">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            const isActive = activeTab === tab.id;
            const isAvailable = availableDocs?.[tab.id]?.exists;

            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                disabled={!isAvailable}
                className={`
                  flex items-center gap-2 px-4 py-3 border-b-2 transition-colors
                  ${isActive ? 'border-blue-600 text-blue-600' : 'border-transparent text-gray-600'}
                  ${!isAvailable ? 'opacity-50 cursor-not-allowed' : 'hover:text-blue-600'}
                `}
              >
                <Icon className="w-4 h-4" />
                {tab.label}
              </button>
            );
          })}
        </div>

        {/* View Mode Toggle */}
        {qaDoc && activeTab !== 'brd' && (
          <div className="flex items-center gap-2 px-4 py-2 bg-gray-50 border-b border-gray-200">
            <button
              onClick={() => setViewMode('document')}
              className={`
                flex items-center gap-2 px-3 py-1.5 rounded transition-colors text-sm
                ${viewMode === 'document' ? 'bg-white text-blue-600 shadow-sm' : 'text-gray-600 hover:bg-white'}
              `}
            >
              <FileText className="w-4 h-4" />
              Document
            </button>
            <button
              onClick={() => setViewMode('qa')}
              className={`
                flex items-center gap-2 px-3 py-1.5 rounded transition-colors text-sm
                ${viewMode === 'qa' ? 'bg-white text-blue-600 shadow-sm' : 'text-gray-600 hover:bg-white'}
              `}
            >
              <MessageSquare className="w-4 h-4" />
              Q&A Conversation
            </button>
          </div>
        )}

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-6">
          {loading && (
            <div className="flex items-center justify-center h-full">
              <div className="text-gray-500">Loading document...</div>
            </div>
          )}

          {error && (
            <div className="flex items-center justify-center h-full">
              <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
                <p className="text-red-600">{error}</p>
              </div>
            </div>
          )}

          {!loading && !error && currentDoc && (
            <div className="prose prose-sm max-w-none">
              <ReactMarkdown remarkPlugins={[remarkGfm]}>
                {currentDoc.content}
              </ReactMarkdown>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="flex items-center justify-between p-4 border-t border-gray-200">
          <div className="text-sm text-gray-500">
            {currentDoc && (
              <>
                File: <code className="text-xs bg-gray-100 px-1.5 py-0.5 rounded">{currentDoc.file_name}</code>
              </>
            )}
          </div>
          <div className="flex gap-2">
            <button
              onClick={handleDownload}
              disabled={!currentDoc}
              className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:bg-gray-400 disabled:cursor-not-allowed"
            >
              <Download className="w-4 h-4" />
              Download
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
