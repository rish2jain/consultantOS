/**
 * Custom hook for WebSocket connection to live dashboards
 */

import { useEffect, useRef, useState } from 'react';

interface UseWebSocketOptions {
  onMessage?: (data: any) => void;
  onError?: (error: Event) => void;
  onOpen?: () => void;
  onClose?: () => void;
  reconnectAttempts?: number;
  reconnectInterval?: number;
}

interface UseWebSocketReturn {
  lastMessage: MessageEvent | null;
  sendMessage: (data: any) => void;
  isConnected: boolean;
  reconnect: () => void;
}

export function useWebSocket(
  url: string | null,
  options: UseWebSocketOptions = {}
): UseWebSocketReturn {
  const {
    onMessage,
    onError,
    onOpen,
    onClose,
    reconnectAttempts = 5,
    reconnectInterval = 3000,
  } = options;

  const [lastMessage, setLastMessage] = useState<MessageEvent | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectCountRef = useRef(0);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout>();

  const connect = () => {
    if (!url || wsRef.current?.readyState === WebSocket.OPEN) {
      return;
    }

    try {
      // Construct WebSocket URL
      const wsUrl = url.startsWith('ws://') || url.startsWith('wss://')
        ? url
        : `${window.location.protocol === 'https:' ? 'wss:' : 'ws:'}//${window.location.host}${url}`;

      const ws = new WebSocket(wsUrl);

      ws.onopen = () => {
        setIsConnected(true);
        reconnectCountRef.current = 0;
        onOpen?.();
      };

      ws.onmessage = (event) => {
        setLastMessage(event);
        if (onMessage) {
          try {
            const data = JSON.parse(event.data);
            onMessage(data);
          } catch {
            onMessage(event.data);
          }
        }
      };

      ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        onError?.(error);
      };

      ws.onclose = () => {
        setIsConnected(false);
        onClose?.();

        // Attempt reconnection
        if (reconnectCountRef.current < reconnectAttempts) {
          reconnectCountRef.current++;
          console.log(`Reconnecting... Attempt ${reconnectCountRef.current}`);
          reconnectTimeoutRef.current = setTimeout(
            connect,
            reconnectInterval * reconnectCountRef.current
          );
        }
      };

      wsRef.current = ws;
    } catch (error) {
      console.error('Failed to create WebSocket:', error);
    }
  };

  const disconnect = () => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
    }
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
  };

  const sendMessage = (data: any) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(
        typeof data === 'string' ? data : JSON.stringify(data)
      );
    } else {
      console.warn('WebSocket is not connected');
    }
  };

  const reconnect = () => {
    disconnect();
    reconnectCountRef.current = 0;
    connect();
  };

  useEffect(() => {
    if (url) {
      connect();
    }

    return () => {
      disconnect();
    };
  }, [url]);

  return {
    lastMessage,
    sendMessage,
    isConnected,
    reconnect,
  };
}
