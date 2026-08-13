/** Wildcard ``*`` does not grant these codes (Admin may not create complaints). */
export const WILDCARD_EXCLUDED_PERMISSIONS = new Set(["complaints:create"]);

export function principalHasPermission(
  permissions: readonly string[],
  permission: string,
): boolean {
  if (permissions.includes(permission)) {
    return true;
  }
  if (WILDCARD_EXCLUDED_PERMISSIONS.has(permission)) {
    return false;
  }
  return permissions.includes("*");
}
