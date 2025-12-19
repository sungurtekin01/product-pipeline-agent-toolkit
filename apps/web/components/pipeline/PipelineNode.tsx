'use client';

import { Handle, Position, NodeProps } from '@xyflow/react';
import { Play, CheckCircle, XCircle, Clock } from 'lucide-react';

export type PipelineNodeData = {
  label: string;
  description: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  progress?: number;
};

export default function PipelineNode({ data }: NodeProps<PipelineNodeData>) {
  const getStatusIcon = () => {
    switch (data.status) {
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
    switch (data.status) {
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

  return (
    <div
      className={`
        px-6 py-4 shadow-lg rounded-lg border-2 min-w-[200px]
        ${getStatusColor()}
        transition-all duration-200 hover:shadow-xl
      `}
    >
      <Handle type="target" position={Position.Left} className="w-3 h-3" />

      <div className="flex items-center gap-3 mb-2">
        {getStatusIcon()}
        <div className="font-semibold text-gray-800">{data.label}</div>
      </div>

      <div className="text-sm text-gray-600 mb-3">{data.description}</div>

      {data.status === 'running' && data.progress !== undefined && (
        <div className="w-full bg-gray-200 rounded-full h-2">
          <div
            className="bg-blue-500 h-2 rounded-full transition-all duration-300"
            style={{ width: `${data.progress}%` }}
          />
        </div>
      )}

      <Handle type="source" position={Position.Right} className="w-3 h-3" />
    </div>
  );
}
