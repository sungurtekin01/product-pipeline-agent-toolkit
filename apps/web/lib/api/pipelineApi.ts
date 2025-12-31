const API_BASE_URL = 'http://127.0.0.1:8000/api';

export interface PipelineExecutionRequest {
  config: {
    vision: string;
    output_dir: string;
    llm?: Record<string, any>;
    api_keys?: {
      gemini?: string;
      anthropic?: string;
      openai?: string;
    };
  };
  step: 'prd' | 'design' | 'tickets';
  feedback?: string;
}

export interface PipelineExecutionResponse {
  task_id: string;
  status: string;
  message: string;
}

export interface PipelineStatus {
  task_id: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  step: string;
  progress: number;
  result?: any;
  error?: string;
  started_at: string;
  completed_at?: string;
}

export interface Document {
  step: string;
  file_name: string;
  content: string;
  path: string;
}

export interface DocumentList {
  output_dir: string;
  documents: {
    [key: string]: {
      name: string;
      file: string;
      exists: boolean;
      qa?: boolean;
    };
  };
}

export interface Feedback {
  step: string;
  feedback: string;
  exists: boolean;
  path?: string;
}

export interface FeedbackSaveRequest {
  step: string;
  feedback: string;
}

export interface VisualizeRequest {
  provider?: string;
  model?: string;
  api_keys?: {
    gemini?: string;
    anthropic?: string;
    openai?: string;
  };
}

export interface VisualizeResponse {
  html: string;
  provider: string;
  model: string;
}

export const pipelineApi = {
  /**
   * Execute a pipeline step
   */
  async executeStep(request: PipelineExecutionRequest): Promise<PipelineExecutionResponse> {
    const response = await fetch(`${API_BASE_URL}/pipeline/execute`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    });

    if (!response.ok) {
      throw new Error(`Failed to execute step: ${response.statusText}`);
    }

    return response.json();
  },

  /**
   * Get status of a task
   */
  async getStatus(taskId: string): Promise<PipelineStatus> {
    const response = await fetch(`${API_BASE_URL}/pipeline/status/${taskId}`);

    if (!response.ok) {
      throw new Error(`Failed to get status: ${response.statusText}`);
    }

    return response.json();
  },

  /**
   * List all tasks
   */
  async listTasks(): Promise<{ tasks: PipelineStatus[] }> {
    const response = await fetch(`${API_BASE_URL}/pipeline/tasks`);

    if (!response.ok) {
      throw new Error(`Failed to list tasks: ${response.statusText}`);
    }

    return response.json();
  },

  /**
   * Health check
   */
  async healthCheck(): Promise<{ status: string }> {
    const response = await fetch(`${API_BASE_URL}/health`);

    if (!response.ok) {
      throw new Error(`Health check failed: ${response.statusText}`);
    }

    return response.json();
  },

  /**
   * Get a document by step
   */
  async getDocument(step: string, outputDir: string = 'docs/product'): Promise<Document> {
    const response = await fetch(`${API_BASE_URL}/documents/${step}?output_dir=${outputDir}`);

    if (!response.ok) {
      throw new Error(`Failed to get document: ${response.statusText}`);
    }

    return response.json();
  },

  /**
   * Get Q&A conversation for a step
   */
  async getQAConversation(step: string, outputDir: string = 'docs/product'): Promise<Document> {
    const response = await fetch(`${API_BASE_URL}/documents/${step}/qa?output_dir=${outputDir}`);

    if (!response.ok) {
      throw new Error(`Failed to get Q&A conversation: ${response.statusText}`);
    }

    return response.json();
  },

  /**
   * List all available documents
   */
  async listDocuments(outputDir: string = 'docs/product'): Promise<DocumentList> {
    const response = await fetch(`${API_BASE_URL}/documents/list?output_dir=${outputDir}`);

    if (!response.ok) {
      throw new Error(`Failed to list documents: ${response.statusText}`);
    }

    return response.json();
  },

  /**
   * Save feedback for a document step
   */
  async saveFeedback(request: FeedbackSaveRequest, outputDir: string = 'docs/product'): Promise<{ message: string; path: string; step: string }> {
    const response = await fetch(`${API_BASE_URL}/documents/${request.step}/feedback?output_dir=${outputDir}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    });

    if (!response.ok) {
      throw new Error(`Failed to save feedback: ${response.statusText}`);
    }

    return response.json();
  },

  /**
   * Get existing feedback for a step
   */
  async getFeedback(step: string, outputDir: string = 'docs/product'): Promise<Feedback> {
    const response = await fetch(`${API_BASE_URL}/documents/${step}/feedback?output_dir=${outputDir}`);

    if (!response.ok) {
      throw new Error(`Failed to get feedback: ${response.statusText}`);
    }

    return response.json();
  },

  /**
   * Generate HTML visualization of design spec
   */
  async visualizeDesign(request: VisualizeRequest = {}, outputDir: string = 'docs/product'): Promise<VisualizeResponse> {
    const response = await fetch(`${API_BASE_URL}/documents/design/visualize?output_dir=${outputDir}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    });

    if (!response.ok) {
      throw new Error(`Failed to visualize design: ${response.statusText}`);
    }

    return response.json();
  },
};
