import { useAuth } from "@usace-watermanagement/groundwork-water";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import toast from "react-hot-toast";
import fetchWithAuth from "../../utils/fetchWithAuth";
import type {
  NotificationGroup,
  NotificationGroupCreate,
  NotificationGroupMember,
  NotificationGroupUpdate,
  NotificationTemplate,
  NotificationTemplateCreate,
  NotificationTemplateUpdate,
  RenderedNotification,
  ScriptNotificationRule,
  ScriptNotificationRuleCreate,
  ScriptNotificationRuleUpdate,
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
    const message = data?.detail ?? `Request failed with ${response.status}`;
    toast.error(message);
    throw new Error(message);
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
    const message = data?.detail ?? `Request failed with ${response.status}`;
    toast.error(message);
    throw new Error(message);
  }
};

export interface CdaUserList {
  "office-id": string;
  "user-list-id": string;
  description?: string | null;
}

export const useCdaUserLists = (office?: string) => {
  const auth = useAuth();
  const cdaRoot = import.meta.env.VITE_CDA_API_ROOT?.replace(/\/$/, "");
  return useQuery({
    queryKey: ["cda-user-lists", office],
    enabled: !!office && !!auth.token && !!cdaRoot,
    queryFn: async () => {
      const response = await fetch(
        `${cdaRoot}/user/list?office=${encodeURIComponent(office!)}`,
        { headers: { Authorization: `Bearer ${auth.token}` } },
      );
      if (!response.ok) {
        throw new Error(`CDA user lists are unavailable (${response.status})`);
      }
      const payload = await response.json();
      return (payload["user-lists"] ?? []) as CdaUserList[];
    },
  });
};

export const useNotificationTemplates = (office?: string) => {
  const auth = useAuth();
  return useQuery({
    queryKey: ["notification-templates", office],
    queryFn: () =>
      requestJson<NotificationTemplate[]>(
        office
          ? `/api/notifications/templates?office=${office}`
          : `/api/notifications/templates`,
        {},
        auth.token,
      ),
  });
};

export const useCreateNotificationTemplate = (office?: string) => {
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

export const useUpdateNotificationTemplate = (office?: string) => {
  const auth = useAuth();
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (args: { templateId: string; payload: NotificationTemplateUpdate }) =>
      requestJson<NotificationTemplate>(
        `/api/notifications/templates/${args.templateId}`,
        {
          method: "PUT",
          headers: jsonHeaders,
          body: JSON.stringify(args.payload),
        },
        auth.token,
      ),
    onSuccess: (template) => {
      queryClient.setQueryData<NotificationTemplate[]>(
        ["notification-templates", office],
        (old) => old?.map((item) => (item.id === template.id ? template : item)),
      );
    },
  });
};

export const useDeleteNotificationTemplate = (office?: string) => {
  const auth = useAuth();
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (templateId: string) =>
      requestNoContent(
        `/api/notifications/templates/${templateId}`,
        { method: "DELETE" },
        auth.token,
      ),
    onSuccess: (_data, templateId) => {
      queryClient.setQueryData<NotificationTemplate[]>(
        ["notification-templates", office],
        (old) => old?.filter((template) => template.id !== templateId),
      );
    },
  });
};

export const useNotificationGroups = (office?: string) => {
  const auth = useAuth();
  return useQuery({
    queryKey: ["notification-groups", office],
    queryFn: () =>
      requestJson<NotificationGroup[]>(
        office
          ? `/api/notifications/groups?office=${office}`
          : `/api/notifications/groups`,
        {},
        auth.token,
      ),
  });
};

export const useCreateNotificationGroup = (office?: string) => {
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

export const useUpdateNotificationGroup = (office?: string) => {
  const auth = useAuth();
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (args: { groupId: string; payload: NotificationGroupUpdate }) =>
      requestJson<NotificationGroup>(
        `/api/notifications/groups/${args.groupId}`,
        {
          method: "PUT",
          headers: jsonHeaders,
          body: JSON.stringify(args.payload),
        },
        auth.token,
      ),
    onSuccess: (group) => {
      queryClient.setQueryData<NotificationGroup[]>(
        ["notification-groups", office],
        (old) => old?.map((item) => (item.id === group.id ? group : item)),
      );
    },
  });
};

export const useDeleteNotificationGroup = (office?: string) => {
  const auth = useAuth();
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (groupId: string) =>
      requestNoContent(
        `/api/notifications/groups/${groupId}`,
        { method: "DELETE" },
        auth.token,
      ),
    onSuccess: (_data, groupId) => {
      queryClient.setQueryData<NotificationGroup[]>(
        ["notification-groups", office],
        (old) => old?.filter((group) => group.id !== groupId),
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
    mutationFn: (payload: { email: string; active: boolean; groupId?: string }) =>
      requestJson<NotificationGroupMember>(
        `/api/notifications/groups/${payload.groupId ?? groupId}/members`,
        {
          method: "POST",
          headers: jsonHeaders,
          body: JSON.stringify({ email: payload.email, active: payload.active }),
        },
        auth.token,
      ),
    onSuccess: (member) => {
      queryClient.setQueryData<NotificationGroupMember[]>(
        ["notification-group-members", member.groupId],
        (old) => (old ? [...old, member] : [member]),
      );
    },
  });
};

export const useDeleteNotificationGroupMember = (groupId?: string) => {
  const auth = useAuth();
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (memberId: string) =>
      requestNoContent(
        `/api/notifications/groups/members/${memberId}`,
        { method: "DELETE" },
        auth.token,
      ),
    onSuccess: (_data, memberId) => {
      queryClient.setQueryData<NotificationGroupMember[]>(
        ["notification-group-members", groupId],
        (old) => old?.filter((member) => member.id !== memberId),
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

export const useUpdateScriptNotificationRule = (scriptId?: string) => {
  const auth = useAuth();
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (args: { ruleId: string; payload: ScriptNotificationRuleUpdate }) =>
      requestJson<ScriptNotificationRule>(
        `/api/notifications/rules/${args.ruleId}`,
        {
          method: "PUT",
          headers: jsonHeaders,
          body: JSON.stringify(args.payload),
        },
        auth.token,
      ),
    onSuccess: (rule) => {
      queryClient.setQueryData<ScriptNotificationRule[]>(
        ["script-notification-rules", scriptId],
        (old) => old?.map((item) => (item.id === rule.id ? rule : item)),
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
      subjectTemplate?: string;
      bodyTemplate?: string;
    }) =>
      requestJson<RenderedNotification>(
        `/api/notifications/templates/${args.templateId}/preview`,
        {
          method: "POST",
          headers: jsonHeaders,
          body: JSON.stringify({
            jobId: args.jobId,
            data: args.data,
            subjectTemplate: args.subjectTemplate,
            bodyTemplate: args.bodyTemplate,
          }),
        },
        auth.token,
      ),
  });
};
