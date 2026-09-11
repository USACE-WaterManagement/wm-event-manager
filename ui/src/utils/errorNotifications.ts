export interface ErrorNotification {
  id: string;
  message: string;
  retry?: () => void;
}

let notifications: ErrorNotification[] = [];
const listeners = new Set<() => void>();
const emit = () => listeners.forEach(listener => listener());

export const subscribe = (listener: () => void) => {
  listeners.add(listener);
  return () => { listeners.delete(listener); };
};
export const getNotifications = () => notifications;
export function notifyError(notification: ErrorNotification) {
  notifications = [...notifications.filter(item => item.id !== notification.id), notification].slice(-5);
  emit();
}
export function dismissError(id: string) {
  notifications = notifications.filter(item => item.id !== id);
  emit();
}
