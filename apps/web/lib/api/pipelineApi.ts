const API_BASE_URL = 'http://localhost:8000/api';

export interface PipelineExecutionRequest {
  config: {
    vision: string;
    output_dir: string;
    llm?: Record<string, any>;
  };
  step: 'brd' | 'design' | 'tickets';
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
};
