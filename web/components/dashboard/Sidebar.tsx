'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { cn } from '@/lib/utils'

type NavItem = { label: string; href: string }
type SidebarProps = { role: 'admin' | 'ops' | 'financier' | 'cfo'; items: NavItem[] }

const EXACT_MATCH_PATHS = ['/admin', '/ops', '/financier', '/cfo']

function isActiveLink(href: string, pathname: string): boolean {
  if (EXACT_MATCH_PATHS.includes(href)) return pathname === href
  return pathname.startsWith(href)
}

const ROLE_LABELS: Record<SidebarProps['role'], string> = {
  admin: 'Administrateur',
  ops: 'Opérations',
  financier: 'Financier',
  cfo: 'CFO',
}

export function Sidebar({ role, items }: SidebarProps) {
  const pathname = usePathname()

  return (
    <aside className="w-60 bg-navy-900 min-h-screen flex flex-col">
      <div className="px-6 py-5 border-b border-white/10">
        <span className="text-white font-bold text-lg">LeaseAI</span>
        <span className="ml-2 text-white/40 text-xs">{ROLE_LABELS[role]}</span>
      </div>
      <nav className="flex-1 px-3 py-4 space-y-1">
        {items.map((item) => (
          <Link
            key={item.href}
            href={item.href}
            className={cn(
              'flex items-center gap-3 px-3 py-2 rounded-lg text-sm transition-colors',
              isActiveLink(item.href, pathname)
                ? 'bg-blue-500 text-white font-medium'
                : 'text-white/60 hover:text-white hover:bg-white/10',
            )}
          >
            {item.label}
          </Link>
        ))}
      </nav>
    </aside>
  )
}
