import { useEffect, useRef, useCallback } from 'react';

interface WebSocketMessage {
  type: 'progress' | 'complete' | 'error' | 'ack';
  status: string;
  progress: number;
  message: string;
  result?: any;
  error?: string;
}

interface UseWebSocketOptions {
  taskId: string;
  onMessage?: (message: WebSocketMessage) => void;
  onOpen?: () => void;
  onClose?: () => void;
  onError?: (error: Event) => void;
}

export function useWebSocket({
  taskId,
  onMessage,
  onOpen,
  onClose,
  onError,
}: UseWebSocketOptions) {
  const ws = useRef<WebSocket | null>(null);
  const reconnectTimeout = useRef<NodeJS.Timeout | undefined>(undefined);

  const connect = useCallback(() => {
    if (!taskId) return;

    const apiHost = process.env.NEXT_PUBLIC_API_URL?.replace(/^https?:\/\//, '').replace(/\/api$/, '') || '127.0.0.1:8000';
    const wsProtocol = process.env.NEXT_PUBLIC_API_URL?.startsWith('https') ? 'wss' : 'ws';
    const wsUrl = `${wsProtocol}://${apiHost}/api/pipeline/ws/${taskId}`;
    ws.current = new WebSocket(wsUrl);

    ws.current.onopen = () => {
      onOpen?.();
    };

    ws.current.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data) as WebSocketMessage;
        onMessage?.(data);
      } catch (error) {
        console.error('Error parsing WebSocket message:', error);
      }
    };

    ws.current.onclose = () => {
      onClose?.();

      // Attempt to reconnect after 3 seconds
      reconnectTimeout.current = setTimeout(() => {
        connect();
      }, 3000);
    };

    ws.current.onerror = (error) => {
      onError?.(error);
    };
  }, [taskId, onMessage, onOpen, onClose, onError]);

  const disconnect = useCallback(() => {
    if (reconnectTimeout.current) {
      clearTimeout(reconnectTimeout.current);
    }
    if (ws.current) {
      ws.current.close();
      ws.current = null;
    }
  }, []);

  const sendMessage = useCallback((message: string) => {
    if (ws.current && ws.current.readyState === WebSocket.OPEN) {
      ws.current.send(message);
    }
  }, []);

  useEffect(() => {
    connect();

    return () => {
      disconnect();
    };
  }, [connect, disconnect]);

  return {
    sendMessage,
    disconnect,
    isConnected: ws.current?.readyState === WebSocket.OPEN,
  };
}
