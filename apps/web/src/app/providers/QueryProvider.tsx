import * as React from "react";
import { QueryClientProvider } from "@tanstack/react-query";
import { defaultQueryClient } from "@/lib/queryClient";

interface QueryProviderProps {
  children: React.ReactNode;
}

export function QueryProvider({ children }: QueryProviderProps) {
  return <QueryClientProvider client={defaultQueryClient}>{children}</QueryClientProvider>;
}

