import { createFileRoute } from "@tanstack/react-router";
import { NotificationsManager } from "../features/notifications-manager/NotificationsManager";

export const Route = createFileRoute("/setup")({
  component: NotificationsManager,
});
