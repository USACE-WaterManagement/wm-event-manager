import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import "./index.css";
import App from "./App.tsx";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import {
  AuthProvider,
  createKeycloakAuthMethod,
} from "@usace-watermanagement/groundwork-water";

const queryClient = new QueryClient();

const authMethod = createKeycloakAuthMethod({
  host: "http://localhost:8081/auth",
  realm: "cwms",
  client: "cwms",
  flow: "direct-grant",
  username: "h2lrltest",
  password: "h2lrltest",
});

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <QueryClientProvider client={queryClient}>
      <AuthProvider method={authMethod}>
        <App />
      </AuthProvider>
    </QueryClientProvider>
  </StrictMode>
);
