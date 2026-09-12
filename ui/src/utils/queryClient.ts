import { MutationCache, QueryCache, QueryClient } from "@tanstack/react-query";
import { ApiError } from "./fetchWithAuth";
import { dismissError, notifyError } from "./errorNotifications";

const message = (error: unknown) => error instanceof Error ? error.message : "Something went wrong. Please try again.";

export const queryClient = new QueryClient({
  queryCache: new QueryCache({
    onError: (error, query) => notifyError({
      id: query.queryHash,
      message: message(error),
      retry: () => { void query.fetch().catch(() => {}); },
    }),
    onSuccess: (_data, query) => dismissError(query.queryHash),
  }),
  mutationCache: new MutationCache({
    onError: (error, _variables, _context, mutation) => notifyError({
      id: `mutation-${mutation.mutationId}`, message: message(error),
    }),
  }),
  defaultOptions: {
    queries: {
      retry: (failureCount, error) => failureCount < 1 && !(error instanceof ApiError && error.status >= 400 && error.status < 500),
      retryOnMount: false,
      refetchOnWindowFocus: false,
      refetchOnReconnect: false,
    },
    // Retrying a write could create a duplicate job after a lost response.
    mutations: { retry: false },
  },
});
