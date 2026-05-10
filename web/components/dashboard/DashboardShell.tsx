import { Sidebar } from './Sidebar'

type NavItem = { label: string; href: string }
type Role = 'admin' | 'ops' | 'financier' | 'cfo'

type Props = {
  role: Role
  title: string
  subtitle?: string
  children: React.ReactNode
}

const NAV_ITEMS: Record<Role, NavItem[]> = {
  admin: [
    { label: 'Dashboard', href: '/' },
    { label: 'Dossiers', href: '/deals' },
    { label: "File d'attente", href: '/queue' },
    { label: 'Utilisateurs', href: '/users' },
  ],
  ops: [
    { label: 'Dashboard', href: '/' },
    { label: 'Dossiers', href: '/deals' },
    { label: 'Tâches', href: '/tasks' },
    { label: 'Documents', href: '/documents' },
  ],
  financier: [
    { label: 'Dashboard', href: '/' },
    { label: 'Packages refi', href: '/packages' },
    { label: 'Décisions', href: '/decisions' },
  ],
  cfo: [
    { label: 'Dashboard', href: '/' },
    { label: 'Portfolio', href: '/portfolio' },
    { label: 'Indicateurs', href: '/kpis' },
    { label: 'Rapports', href: '/reports' },
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
