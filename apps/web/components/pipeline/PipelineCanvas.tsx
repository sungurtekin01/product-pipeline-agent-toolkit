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
import { usePipelineStore, PersonasResponse, PersonaInfo } from '@/lib/store/pipelineStore';

const nodeDefinitions = [
  {
    id: 'prd',
    label: 'PRD',
    description: 'Product Requirements Document',
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
    id: 'prd-design',
    source: 'prd',
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
  onRunStep?: (step: 'prd' | 'design' | 'tickets') => void;
  availablePersonas?: PersonasResponse | null;
  personaMapping?: Record<string, string>;
  onPersonaSelect?: (step: string, personaId: string) => void;
}

export default function PipelineCanvas({
  onRunStep,
  availablePersonas,
  personaMapping,
  onPersonaSelect,
}: PipelineCanvasProps) {
  const pipelineNodes = usePipelineStore((state) => state.nodes);

  // Helper to get personas for a step based on its role
  const getPersonasForStep = (stepId: string): PersonaInfo[] => {
    if (!availablePersonas) return [];

    const roleMapping: Record<string, keyof PersonasResponse['personas']> = {
      prd: 'strategist',
      design: 'designer',
      tickets: 'po',
    };

    const role = roleMapping[stepId];
    return role ? availablePersonas.personas[role] : [];
  };

  // Helper to get current persona for a step
  const getCurrentPersona = (stepId: string): PersonaInfo | undefined => {
    const personas = getPersonasForStep(stepId);
    const personaId = personaMapping?.[stepId];
    return personas.find((p) => p.id === personaId);
  };

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
      message: pipelineNodes[def.id]?.message,
      onRun: onRunStep ? () => onRunStep(def.id as 'prd' | 'design' | 'tickets') : undefined,
      availablePersonas: getPersonasForStep(def.id),
      currentPersona: getCurrentPersona(def.id),
      onPersonaSelect: onPersonaSelect ? (personaId) => onPersonaSelect(def.id, personaId) : undefined,
    },
  }));

  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);

  // Update nodes when pipeline store or persona selection changes
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
              message: storeNode.message,
              onRun: onRunStep ? () => onRunStep(node.id as 'prd' | 'design' | 'tickets') : undefined,
              availablePersonas: getPersonasForStep(node.id),
              currentPersona: getCurrentPersona(node.id),
              onPersonaSelect: onPersonaSelect ? (personaId) => onPersonaSelect(node.id, personaId) : undefined,
            },
          };
        }
        return node;
      })
    );
  }, [pipelineNodes, setNodes, onRunStep, availablePersonas, personaMapping, onPersonaSelect]);

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
        fitViewOptions={{ padding: 0.3, maxZoom: 1 }}
        minZoom={0.3}
        maxZoom={1.5}
        defaultViewport={{ x: 0, y: 0, zoom: 0.8 }}
        className="bg-gray-50"
      >
        <Background color="#e5e7eb" gap={16} />
        <Controls showInteractive={false} />
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
