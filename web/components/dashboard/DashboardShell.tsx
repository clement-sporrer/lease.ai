import type { ReactNode } from 'react'
import { Sidebar } from './Sidebar'

type NavItem = { label: string; href: string }
type Role = 'admin' | 'ops' | 'financier' | 'cfo' | 'risk' | 'commercial' | 'comptable'

type Props = {
  role: Role
  title: string
  subtitle?: string
  children: ReactNode
}

const NAV_ITEMS: Record<Role, NavItem[]> = {
  admin:      [{ label: 'Tableau de bord', href: '/admin' }, { label: "File d'attente", href: '/admin/queue' }],
  ops:        [{ label: 'Tableau de bord', href: '/ops' }],
  financier:  [{ label: 'Tableau de bord', href: '/financier' }],
  cfo:        [{ label: 'Tableau de bord', href: '/cfo' }],
  risk:       [{ label: 'Tableau de bord', href: '/risk' }],
  commercial: [{ label: 'Tableau de bord', href: '/commercial' }],
  comptable:  [{ label: 'Tableau de bord', href: '/comptable' }],
}

export function DashboardShell({ role, title, subtitle, children }: Props) {
  return (
    <div className="flex min-h-screen bg-gray-50">
      <Sidebar role={role} items={NAV_ITEMS[role]} />
      <div className="flex-1 flex flex-col min-w-0">
        <header className="bg-white border-b border-gray-100 px-8 py-5">
          <h1 className="text-[22px] font-bold tracking-tight text-navy-900 leading-none">
            {title}
          </h1>
          {subtitle && (
            <p className="text-sm text-gray-400 mt-1.5 font-normal">{subtitle}</p>
          )}
        </header>
        <main className="flex-1 p-8">{children}</main>
      </div>
    </div>
  )
}
