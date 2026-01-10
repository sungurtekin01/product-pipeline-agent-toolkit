'use client';

import { Handle, Position, NodeProps } from '@xyflow/react';
import { Play, CheckCircle, XCircle, Clock } from 'lucide-react';
import PersonaMenu from './PersonaMenu';
import type { PersonaInfo } from '@/lib/store/pipelineStore';

export type PipelineNodeData = {
  label: string;
  description: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  progress?: number;
  message?: string;
  onRun?: () => void;
  // Persona selection
  availablePersonas?: PersonaInfo[];
  currentPersona?: PersonaInfo;
  onPersonaSelect?: (personaId: string) => void;
};

export default function PipelineNode({ data }: NodeProps) {
  const nodeData = data as PipelineNodeData;

  const getStatusIcon = () => {
    switch (nodeData.status) {
      case 'completed':
        return <CheckCircle className="w-5 h-5 text-green-500" />;
      case 'running':
        return <Clock className="w-5 h-5 text-blue-500 animate-spin" />;
      case 'failed':
        return <XCircle className="w-5 h-5 text-red-500" />;
      default:
        return <Play className="w-5 h-5 text-gray-400" />;
    }
  };

  const getStatusColor = () => {
    switch (nodeData.status) {
      case 'completed':
        return 'border-green-500 bg-green-50';
      case 'running':
        return 'border-blue-500 bg-blue-50';
      case 'failed':
        return 'border-red-500 bg-red-50';
      default:
        return 'border-gray-300 bg-white';
    }
  };

  const isRunning = nodeData.status === 'running';

  return (
    <div
      className={`
        px-4 py-3 shadow-lg rounded-lg border-2 min-w-[180px] max-w-[220px]
        ${getStatusColor()}
        transition-all duration-200 hover:shadow-xl
      `}
    >
      <Handle type="target" position={Position.Left} className="w-3 h-3" />

      <div className="flex items-center justify-between gap-2 mb-2">
        <div className="flex items-center gap-2 flex-1 min-w-0">
          {getStatusIcon()}
          <div className="font-semibold text-gray-800 text-sm truncate">{nodeData.label}</div>
        </div>
        {nodeData.availablePersonas && nodeData.availablePersonas.length > 0 && (
          <PersonaMenu
            personas={nodeData.availablePersonas}
            selectedPersonaId={nodeData.currentPersona?.id || ''}
            onSelect={(personaId) => nodeData.onPersonaSelect?.(personaId)}
            disabled={isRunning}
          />
        )}
      </div>

      <div className="text-xs text-gray-600 mb-2">{nodeData.description}</div>

      {nodeData.currentPersona && (
        <div className="text-xs text-gray-500 mb-2 italic">
          Persona: {nodeData.currentPersona.description || nodeData.currentPersona.name}
        </div>
      )}

      {nodeData.status === 'running' && nodeData.progress !== undefined && (
        <>
          <div className="w-full bg-gray-200 rounded-full h-1.5 mb-2">
            <div
              className="bg-blue-500 h-1.5 rounded-full transition-all duration-300"
              style={{ width: `${nodeData.progress}%` }}
            />
          </div>
          {nodeData.message && (
            <div className="text-xs text-blue-700 mb-2 truncate" title={nodeData.message}>
              {nodeData.message}
            </div>
          )}
        </>
      )}

      {nodeData.onRun && nodeData.status !== 'running' && (
        <button
          onClick={(e) => {
            e.stopPropagation();
            nodeData.onRun?.();
          }}
          className="w-full mt-2 px-3 py-1.5 bg-blue-600 text-white text-sm rounded hover:bg-blue-700 transition-colors"
        >
          {nodeData.status === 'completed' ? 'Re-run' : 'Run'}
        </button>
      )}

      <Handle type="source" position={Position.Right} className="w-3 h-3" />
    </div>
  );
}
