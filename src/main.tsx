import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import "./index.css";
import App from "./App.tsx";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import {
  AuthProvider,
  createKeycloakAuthMethod,
} from "@usace-watermanagement/groundwork-water";
import createMockAuthMethod from "./features/auth/mockAuthMethod.ts";

const buildMode = import.meta.env.MODE;
const authHost = import.meta.env.VITE_AUTH_HOST;
const authRealm = import.meta.env.VITE_AUTH_REALM;

const authMethod = (() => {
  if (buildMode === "dev-cda-compose") {
    return createKeycloakAuthMethod({
      host: authHost,
      realm: authRealm,
      client: "cwms",
      flow: "direct-grant",
      username: "h2lrltest",
      password: "h2lrltest",
    });
  } else {
    return createMockAuthMethod();
  }
})();

const queryClient = new QueryClient();

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <QueryClientProvider client={queryClient}>
      <AuthProvider method={authMethod}>
        <App />
      </AuthProvider>
    </QueryClientProvider>
  </StrictMode>
);
