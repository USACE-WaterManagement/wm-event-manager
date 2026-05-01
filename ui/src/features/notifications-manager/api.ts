import { useAuth } from "@usace-watermanagement/groundwork-water";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import fetchWithAuth from "../../utils/fetchWithAuth";
import type {
  NotificationGroup,
  NotificationGroupCreate,
  NotificationGroupMember,
  NotificationTemplate,
  NotificationTemplateCreate,
  RenderedNotification,
  ScriptNotificationRule,
  ScriptNotificationRuleCreate,
} from "./types";

const jsonHeaders = { "Content-Type": "application/json" };

const requestJson = async <T>(
  input: RequestInfo | URL,
  options: RequestInit,
  token?: string,
): Promise<T> => {
  const response = await fetchWithAuth(input, options, token);
  if (!response.ok) {
    const data = await response.json().catch(() => undefined);
    throw new Error(data?.detail ?? `Request failed with ${response.status}`);
  }
  return response.json();
};

const requestNoContent = async (
  input: RequestInfo | URL,
  options: RequestInit,
  token?: string,
) => {
  const response = await fetchWithAuth(input, options, token);
  if (!response.ok) {
    const data = await response.json().catch(() => undefined);
    throw new Error(data?.detail ?? `Request failed with ${response.status}`);
  }
};

export const useNotificationTemplates = (office: string) => {
  const auth = useAuth();
  return useQuery({
    queryKey: ["notification-templates", office],
    queryFn: () =>
      requestJson<NotificationTemplate[]>(
        `/api/notifications/templates?office=${office}`,
        {},
        auth.token,
      ),
  });
};

export const useCreateNotificationTemplate = (office: string) => {
  const auth = useAuth();
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload: NotificationTemplateCreate) =>
      requestJson<NotificationTemplate>(
        `/api/notifications/templates`,
        {
          method: "POST",
          headers: jsonHeaders,
          body: JSON.stringify(payload),
        },
        auth.token,
      ),
    onSuccess: (template) => {
      queryClient.setQueryData<NotificationTemplate[]>(
        ["notification-templates", office],
        (old) => (old ? [...old, template] : [template]),
      );
    },
  });
};

export const useNotificationGroups = (office: string) => {
  const auth = useAuth();
  return useQuery({
    queryKey: ["notification-groups", office],
    queryFn: () =>
      requestJson<NotificationGroup[]>(
        `/api/notifications/groups?office=${office}`,
        {},
        auth.token,
      ),
  });
};

export const useCreateNotificationGroup = (office: string) => {
  const auth = useAuth();
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload: NotificationGroupCreate) =>
      requestJson<NotificationGroup>(
        `/api/notifications/groups`,
        {
          method: "POST",
          headers: jsonHeaders,
          body: JSON.stringify(payload),
        },
        auth.token,
      ),
    onSuccess: (group) => {
      queryClient.setQueryData<NotificationGroup[]>(
        ["notification-groups", office],
        (old) => (old ? [...old, group] : [group]),
      );
    },
  });
};

export const useNotificationGroupMembers = (groupId?: string) => {
  const auth = useAuth();
  return useQuery({
    queryKey: ["notification-group-members", groupId],
    enabled: !!groupId,
    queryFn: () =>
      requestJson<NotificationGroupMember[]>(
        `/api/notifications/groups/${groupId}/members`,
        {},
        auth.token,
      ),
  });
};

export const useCreateNotificationGroupMember = (groupId?: string) => {
  const auth = useAuth();
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload: { email: string; active: boolean }) =>
      requestJson<NotificationGroupMember>(
        `/api/notifications/groups/${groupId}/members`,
        {
          method: "POST",
          headers: jsonHeaders,
          body: JSON.stringify(payload),
        },
        auth.token,
      ),
    onSuccess: (member) => {
      queryClient.setQueryData<NotificationGroupMember[]>(
        ["notification-group-members", groupId],
        (old) => (old ? [...old, member] : [member]),
      );
    },
  });
};

export const useScriptNotificationRules = (scriptId?: string) => {
  const auth = useAuth();
  return useQuery({
    queryKey: ["script-notification-rules", scriptId],
    enabled: !!scriptId,
    queryFn: () =>
      requestJson<ScriptNotificationRule[]>(
        `/api/notifications/rules?script_id=${scriptId}`,
        {},
        auth.token,
      ),
  });
};

export const useCreateScriptNotificationRule = (scriptId?: string) => {
  const auth = useAuth();
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload: ScriptNotificationRuleCreate) =>
      requestJson<ScriptNotificationRule>(
        `/api/notifications/rules`,
        {
          method: "POST",
          headers: jsonHeaders,
          body: JSON.stringify(payload),
        },
        auth.token,
      ),
    onSuccess: (rule) => {
      queryClient.setQueryData<ScriptNotificationRule[]>(
        ["script-notification-rules", scriptId],
        (old) => (old ? [...old, rule] : [rule]),
      );
    },
  });
};

export const useDeleteScriptNotificationRule = (scriptId?: string) => {
  const auth = useAuth();
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (ruleId: string) =>
      requestNoContent(
        `/api/notifications/rules/${ruleId}`,
        { method: "DELETE" },
        auth.token,
      ),
    onSuccess: (_data, ruleId) => {
      queryClient.setQueryData<ScriptNotificationRule[]>(
        ["script-notification-rules", scriptId],
        (old) => old?.filter((rule) => rule.id !== ruleId),
      );
    },
  });
};

export const usePreviewNotificationTemplate = () => {
  const auth = useAuth();
  return useMutation({
    mutationFn: (args: {
      templateId: string;
      jobId?: string;
      data: Record<string, string | null>;
    }) =>
      requestJson<RenderedNotification>(
        `/api/notifications/templates/${args.templateId}/preview`,
        {
          method: "POST",
          headers: jsonHeaders,
          body: JSON.stringify({ jobId: args.jobId, data: args.data }),
        },
        auth.token,
      ),
  });
};
