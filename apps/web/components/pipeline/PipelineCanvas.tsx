'use client';

import { useCallback, useMemo, useEffect } from 'react';
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
  NodeTypes,
} from '@xyflow/react';
import '@xyflow/react/dist/style.css';

import PipelineNode, { PipelineNodeData } from './PipelineNode';
import { usePipelineStore } from '@/lib/store/pipelineStore';

const nodeDefinitions = [
  {
    id: 'brd',
    label: 'BRD',
    description: 'Business Requirements Document',
    position: { x: 100, y: 200 },
  },
  {
    id: 'design',
    label: 'Design Spec',
    description: 'UI/UX Design Specification',
    position: { x: 400, y: 200 },
  },
  {
    id: 'tickets',
    label: 'Dev Tickets',
    description: 'Development Tickets',
    position: { x: 700, y: 200 },
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

interface PipelineCanvasProps {
  onRunStep?: (step: 'brd' | 'design' | 'tickets') => void;
}

export default function PipelineCanvas({ onRunStep }: PipelineCanvasProps) {
  const pipelineNodes = usePipelineStore((state) => state.nodes);

  // Build React Flow nodes from pipeline store
  const initialNodes: Node<PipelineNodeData>[] = nodeDefinitions.map((def) => ({
    id: def.id,
    type: 'pipelineNode',
    position: def.position,
    data: {
      label: def.label,
      description: def.description,
      status: pipelineNodes[def.id]?.status || 'pending',
      progress: pipelineNodes[def.id]?.progress || 0,
      onRun: onRunStep ? () => onRunStep(def.id as 'brd' | 'design' | 'tickets') : undefined,
    },
  }));

  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);

  // Update nodes when pipeline store changes
  useEffect(() => {
    setNodes((nds) =>
      nds.map((node) => {
        const storeNode = pipelineNodes[node.id];
        if (storeNode) {
          return {
            ...node,
            data: {
              ...node.data,
              status: storeNode.status,
              progress: storeNode.progress,
              onRun: onRunStep ? () => onRunStep(node.id as 'brd' | 'design' | 'tickets') : undefined,
            },
          };
        }
        return node;
      })
    );
  }, [pipelineNodes, setNodes, onRunStep]);

  const nodeTypes = useMemo(
    () => ({
      pipelineNode: PipelineNode as any,
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
