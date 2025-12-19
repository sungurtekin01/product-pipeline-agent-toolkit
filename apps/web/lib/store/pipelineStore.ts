import { create } from 'zustand';

export type NodeStatus = 'pending' | 'running' | 'completed' | 'failed';

export interface PipelineNodeState {
  id: string;
  status: NodeStatus;
  progress: number;
  message?: string;
  error?: string;
  result?: any;
}

interface PipelineState {
  // Node states
  nodes: Record<string, PipelineNodeState>;

  // Current execution
  currentTaskId: string | null;
  isExecuting: boolean;

  // User inputs
  vision: string;
  llmProvider: string;
  llmModel: string;

  // Actions
  setNodeStatus: (nodeId: string, status: NodeStatus, progress?: number, message?: string) => void;
  setNodeProgress: (nodeId: string, progress: number) => void;
  setNodeError: (nodeId: string, error: string) => void;
  setNodeResult: (nodeId: string, result: any) => void;
  setCurrentTaskId: (taskId: string | null) => void;
  setIsExecuting: (isExecuting: boolean) => void;
  setVision: (vision: string) => void;
  setLLMProvider: (provider: string) => void;
  setLLMModel: (model: string) => void;
  resetNodes: () => void;
}

const initialNodes: Record<string, PipelineNodeState> = {
  brd: {
    id: 'brd',
    status: 'pending',
    progress: 0,
  },
  design: {
    id: 'design',
    status: 'pending',
    progress: 0,
  },
  tickets: {
    id: 'tickets',
    status: 'pending',
    progress: 0,
  },
};

export const usePipelineStore = create<PipelineState>((set) => ({
  // Initial state
  nodes: initialNodes,
  currentTaskId: null,
  isExecuting: false,
  vision: '',
  llmProvider: 'gemini',
  llmModel: 'gemini-2.0-flash-exp',

  // Actions
  setNodeStatus: (nodeId, status, progress = 0, message) =>
    set((state) => ({
      nodes: {
        ...state.nodes,
        [nodeId]: {
          ...state.nodes[nodeId],
          status,
          progress,
          message,
        },
      },
    })),

  setNodeProgress: (nodeId, progress) =>
    set((state) => ({
      nodes: {
        ...state.nodes,
        [nodeId]: {
          ...state.nodes[nodeId],
          progress,
        },
      },
    })),

  setNodeError: (nodeId, error) =>
    set((state) => ({
      nodes: {
        ...state.nodes,
        [nodeId]: {
          ...state.nodes[nodeId],
          status: 'failed',
          error,
        },
      },
    })),

  setNodeResult: (nodeId, result) =>
    set((state) => ({
      nodes: {
        ...state.nodes,
        [nodeId]: {
          ...state.nodes[nodeId],
          result,
        },
      },
    })),

  setCurrentTaskId: (taskId) => set({ currentTaskId: taskId }),

  setIsExecuting: (isExecuting) => set({ isExecuting }),

  setVision: (vision) => set({ vision }),

  setLLMProvider: (provider) => set({ llmProvider: provider }),

  setLLMModel: (model) => set({ llmModel: model }),

  resetNodes: () => set({ nodes: initialNodes }),
}));
