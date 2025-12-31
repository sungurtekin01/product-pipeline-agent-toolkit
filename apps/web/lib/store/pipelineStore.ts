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

export interface PersonaInfo {
  id: string;
  name: string;
  description: string;
}

export interface PersonasResponse {
  personas: {
    strategist: PersonaInfo[];
    designer: PersonaInfo[];
    po: PersonaInfo[];
  };
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

  // Persona selection
  personaMapping: Record<string, string>; // {"prd": "strategist", "design": "designer", "tickets": "po"}
  availablePersonas: PersonasResponse | null;

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
  setPersonaForStep: (step: string, personaId: string) => void;
  setAvailablePersonas: (personas: PersonasResponse) => void;
  resetNodes: () => void;
}

const initialNodes: Record<string, PipelineNodeState> = {
  prd: {
    id: 'prd',
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
  llmProvider: 'gemini-3-flash-preview',
  llmModel: 'gemini-3-flash-preview',
  personaMapping: {
    prd: 'strategist',
    design: 'designer',
    tickets: 'po',
  },
  availablePersonas: null,

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

  setPersonaForStep: (step, personaId) =>
    set((state) => ({
      personaMapping: {
        ...state.personaMapping,
        [step]: personaId,
      },
    })),

  setAvailablePersonas: (personas) => set({ availablePersonas: personas }),

  resetNodes: () => set({ nodes: initialNodes }),
}));
