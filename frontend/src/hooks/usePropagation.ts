import { useQuery } from "@tanstack/react-query";
import { fetchJson } from "../lib/api";
import { useStore } from "../store";

export function usePropagation() {
  const dx = useStore((s) => s.dxLocation);
  const station = useStore((s) => s.stationConfig);

  const params = dx
    ? `?rx_lat=${dx.latitude}&rx_lon=${dx.longitude}`
    : "";

  return useQuery({
    queryKey: ["propagation", dx?.latitude ?? null, dx?.longitude ?? null],
    queryFn: () => fetchJson(`/propagation${params}`),
    staleTime: 5 * 60_000,
    refetchInterval: 5 * 60_000,
    enabled: !!station,
  });
}
