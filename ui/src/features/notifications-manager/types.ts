import { components } from "../../generated/api-types";

type Schemas = components["schemas"];

export type NotificationTemplate = Schemas["NotificationTemplateRead"];
export type NotificationTemplateCreate = Schemas["NotificationTemplateCreate"];
export type NotificationGroup = Schemas["NotificationGroupRead"];
export type NotificationGroupCreate = Schemas["NotificationGroupCreate"];
export type NotificationGroupMember = Schemas["NotificationGroupMemberRead"];
export type ScriptNotificationRule = Schemas["ScriptNotificationRuleRead"];
export type ScriptNotificationRuleCreate =
  Schemas["ScriptNotificationRuleCreate"];
export type RenderedNotification = Schemas["RenderedNotification"];
