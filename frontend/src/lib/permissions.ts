import type { UserRead } from "../types";

export const permissions = {
  root: "root",
  usersRead: "admin.users.read",
  usersCreate: "admin.users.create",
  usersUpdate: "admin.users.update",
  usersPermissionsWrite: "admin.users.permissions.write",
  orgsRead: "admin.organizations.read",
  orgsCreate: "admin.organizations.create",
  personnelManage: "admin.personnel.manage",
  adminLogsRead: "admin.logs.read",
  oauthAppsRead: "admin.oauth_apps.read",
  oauthAppsReview: "admin.oauth_apps.review",
  newsManage: "news.manage",
  billsManage: "bills.manage",
  referendaManage: "referenda.manage",
  ratublesMint: "ratubles.mint",
} as const;

export function hasPermission(
  profile: UserRead | null | undefined,
  permission: string,
) {
  if (!profile) {
    return false;
  }
  return (
    profile.permissions.includes("*") || profile.permissions.includes(permission)
  );
}
