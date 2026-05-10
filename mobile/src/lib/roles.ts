const KNOWN_ROLES = [
  'partner_user',
  'client_user',
  'admin_user',
  'ops_user',
  'risk_user',
  'financier_user',
  'cfo_user',
] as const

export type KnownRole = (typeof KNOWN_ROLES)[number]

export function isKnownRole(value: unknown): value is KnownRole {
  return typeof value === 'string' && (KNOWN_ROLES as readonly string[]).includes(value)
}
