import { useQueryClient } from "@tanstack/react-query";
import { useCallback, useEffect, useRef } from "react";
import { useStore } from "../store";

const WS_RECONNECT_DELAY = 3000;

export function useWebSocket() {
  const queryClient = useQueryClient();
  const setWsStatus = useStore((s) => s.setWsStatus);
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimer = useRef<number>(0);

  const connect = useCallback(() => {
    const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
    const url = `${protocol}//${window.location.host}/api/v1/ws`;

    setWsStatus("connecting");
    const ws = new WebSocket(url);
    wsRef.current = ws;

    ws.onopen = () => {
      setWsStatus("connected");
    };

    ws.onmessage = (event) => {
      try {
        const msg = JSON.parse(event.data);
        if (msg.type && msg.data) {
          if (msg.type === "greyline") {
            queryClient.setQueryData(["greyline"], msg.data);
          } else {
            queryClient.setQueryData(["space-weather", msg.type], msg.data);
          }
        }
      } catch {
        // ignore parse errors
      }
    };

    ws.onclose = () => {
      setWsStatus("disconnected");
      wsRef.current = null;
      reconnectTimer.current = window.setTimeout(connect, WS_RECONNECT_DELAY);
    };

    ws.onerror = () => {
      ws.close();
    };
  }, [queryClient, setWsStatus]);

  useEffect(() => {
    connect();
    return () => {
      clearTimeout(reconnectTimer.current);
      wsRef.current?.close();
    };
  }, [connect]);
}
