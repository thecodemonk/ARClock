import { useQuery } from "@tanstack/react-query";
import { fetchJson } from "../lib/api";

export function useSFI() {
  return useQuery({
    queryKey: ["space-weather", "sfi"],
    queryFn: () => fetchJson("/space-weather/sfi"),
    staleTime: 15 * 60_000,
  });
}

export function useKp() {
  return useQuery({
    queryKey: ["space-weather", "kp"],
    queryFn: () => fetchJson("/space-weather/kp"),
    staleTime: 5 * 60_000,
  });
}

export function useXRay() {
  return useQuery({
    queryKey: ["space-weather", "xray"],
    queryFn: () => fetchJson("/space-weather/xray"),
    staleTime: 60_000,
  });
}

export function useSSN() {
  return useQuery({
    queryKey: ["space-weather", "ssn"],
    queryFn: () => fetchJson("/space-weather/ssn"),
    staleTime: 60 * 60_000,
  });
}

export function useGreyLine() {
  return useQuery({
    queryKey: ["greyline"],
    queryFn: () => fetchJson("/greyline"),
    staleTime: 60_000,
  });
}
