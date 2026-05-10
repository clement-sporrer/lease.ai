import type { ReactNode } from 'react'
import { Sidebar } from './Sidebar'

type NavItem = { label: string; href: string }
type Role = 'admin' | 'ops' | 'financier' | 'cfo'

type Props = {
  role: Role
  title: string
  subtitle?: string
  children: ReactNode
}

const NAV_ITEMS: Record<Role, NavItem[]> = {
  admin: [
    { label: 'Dashboard', href: '/admin' },
    { label: 'Dossiers', href: '/admin/deals' },
    { label: "File d'attente", href: '/admin/queue' },
    { label: 'Utilisateurs', href: '/admin/users' },
  ],
  ops: [
    { label: 'Dashboard', href: '/ops' },
    { label: 'Dossiers', href: '/ops/deals' },
    { label: 'Tâches', href: '/ops/tasks' },
    { label: 'Documents', href: '/ops/documents' },
  ],
  financier: [
    { label: 'Dashboard', href: '/financier' },
    { label: 'Packages refi', href: '/financier/packages' },
    { label: 'Décisions', href: '/financier/decisions' },
  ],
  cfo: [
    { label: 'Dashboard', href: '/cfo' },
    { label: 'Portfolio', href: '/cfo/portfolio' },
    { label: 'Indicateurs', href: '/cfo/kpis' },
    { label: 'Rapports', href: '/cfo/reports' },
  ],
}

export function DashboardShell({ role, title, subtitle, children }: Props) {
  return (
    <div className="flex min-h-screen bg-gray-50">
      <Sidebar role={role} items={NAV_ITEMS[role]} />
      <div className="flex-1 flex flex-col">
        <header className="bg-white border-b border-gray-200 px-8 py-4">
          <h1 className="text-xl font-bold text-navy-900">{title}</h1>
          {subtitle && <p className="text-sm text-gray-500 mt-0.5">{subtitle}</p>}
        </header>
        <main className="flex-1 p-8">{children}</main>
      </div>
    </div>
  )
}
