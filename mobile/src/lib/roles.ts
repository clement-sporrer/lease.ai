const ROLE_ALIASES = {
  partner: 'partner',
  partner_user: 'partner',
  client: 'client',
  client_user: 'client',
  admin: 'admin',
  admin_user: 'admin',
  ops: 'ops',
  ops_user: 'ops',
  risk_user: 'risk',
  financier: 'financier',
  financier_user: 'financier',
  cfo: 'cfo',
  cfo_user: 'cfo',
} as const

export type KnownRole = keyof typeof ROLE_ALIASES
export type NormalizedRole = (typeof ROLE_ALIASES)[KnownRole]

export function isKnownRole(value: unknown): value is KnownRole {
  return typeof value === 'string' && value in ROLE_ALIASES
}

export function normalizeRole(value: unknown): NormalizedRole | null {
  if (!isKnownRole(value)) return null
  return ROLE_ALIASES[value]
}
