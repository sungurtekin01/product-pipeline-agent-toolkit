'use client';

import { useCallback, useMemo } from 'react';
import {
  ReactFlow,
  Background,
  Controls,
  MiniMap,
  Node,
  Edge,
  useNodesState,
  useEdgesState,
  addEdge,
  Connection,
  MarkerType,
} from '@xyflow/react';
import '@xyflow/react/dist/style.css';

import PipelineNode, { PipelineNodeData } from './PipelineNode';

const initialNodes: Node<PipelineNodeData>[] = [
  {
    id: 'brd',
    type: 'pipelineNode',
    position: { x: 100, y: 200 },
    data: {
      label: 'BRD',
      description: 'Business Requirements Document',
      status: 'pending',
    },
  },
  {
    id: 'design',
    type: 'pipelineNode',
    position: { x: 400, y: 200 },
    data: {
      label: 'Design Spec',
      description: 'UI/UX Design Specification',
      status: 'pending',
    },
  },
  {
    id: 'tickets',
    type: 'pipelineNode',
    position: { x: 700, y: 200 },
    data: {
      label: 'Dev Tickets',
      description: 'Development Tickets',
      status: 'pending',
    },
  },
];

const initialEdges: Edge[] = [
  {
    id: 'brd-design',
    source: 'brd',
    target: 'design',
    type: 'smoothstep',
    animated: false,
    markerEnd: {
      type: MarkerType.ArrowClosed,
    },
  },
  {
    id: 'design-tickets',
    source: 'design',
    target: 'tickets',
    type: 'smoothstep',
    animated: false,
    markerEnd: {
      type: MarkerType.ArrowClosed,
    },
  },
];

export default function PipelineCanvas() {
  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);

  const nodeTypes = useMemo(
    () => ({
      pipelineNode: PipelineNode,
    }),
    []
  );

  const onConnect = useCallback(
    (params: Connection) => setEdges((eds) => addEdge(params, eds)),
    [setEdges]
  );

  return (
    <div className="w-full h-full bg-gray-50">
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onConnect={onConnect}
        nodeTypes={nodeTypes}
        fitView
        className="bg-gray-50"
      >
        <Background color="#e5e7eb" gap={16} />
        <Controls />
        <MiniMap
          nodeColor={(node) => {
            const data = node.data as PipelineNodeData;
            switch (data.status) {
              case 'completed':
                return '#10b981';
              case 'running':
                return '#3b82f6';
              case 'failed':
                return '#ef4444';
              default:
                return '#d1d5db';
            }
          }}
          className="bg-white border border-gray-200"
        />
      </ReactFlow>
    </div>
  );
}
