'use client'

import Link from 'next/link'
import { usePathname, useRouter } from 'next/navigation'
import { createBrowserClient } from '@supabase/ssr'
import { useEffect, useState } from 'react'
import { cn } from '@/lib/utils'

type NavItem = { label: string; href: string }
type Role = 'admin' | 'ops' | 'financier' | 'cfo' | 'risk' | 'commercial' | 'comptable'
type SidebarProps = { role: Role; items: NavItem[] }

const EXACT_MATCH_PATHS = ['/admin', '/ops', '/financier', '/cfo', '/risk', '/commercial', '/comptable']

function isActiveLink(href: string, pathname: string): boolean {
  if (EXACT_MATCH_PATHS.includes(href)) return pathname === href
  return pathname.startsWith(href)
}

const ROLE_LABELS: Record<Role, string> = {
  admin: 'ADV',
  ops: 'Opérations',
  financier: 'Financier',
  cfo: 'CFO',
  risk: 'Risques',
  commercial: 'Commercial',
  comptable: 'Comptabilité',
}

export function Sidebar({ role, items }: SidebarProps) {
  const pathname = usePathname()
  const router = useRouter()
  const [fullName, setFullName] = useState<string | null>(null)

  const supabase = createBrowserClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
  )

  useEffect(() => {
    supabase.auth.getUser().then(({ data: { user } }) => {
      setFullName(user?.user_metadata?.full_name ?? user?.email ?? null)
    })
  }, [])

  async function handleLogout() {
    await supabase.auth.signOut()
    router.push('/login')
    router.refresh()
  }

  return (
    <aside className="w-60 bg-navy-900 min-h-screen flex flex-col">
      <div className="px-6 py-5 border-b border-white/10 flex items-center justify-between">
        <img src="/logo.svg" alt="LeaseAI" className="h-7 w-auto brightness-0 invert" />
        <span className="text-white/40 text-xs">{ROLE_LABELS[role]}</span>
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

      <div className="px-3 py-4 border-t border-white/10">
        {fullName && (
          <p className="px-3 mb-2 text-xs text-white/40 truncate">{fullName}</p>
        )}
        <button
          onClick={handleLogout}
          className="w-full flex items-center gap-2 px-3 py-2 rounded-lg text-sm text-white/60 hover:text-white hover:bg-white/10 transition-colors text-left"
        >
          <svg className="w-4 h-4 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M15.75 9V5.25A2.25 2.25 0 0013.5 3h-6a2.25 2.25 0 00-2.25 2.25v13.5A2.25 2.25 0 007.5 21h6a2.25 2.25 0 002.25-2.25V15M12 9l-3 3m0 0l3 3m-3-3h12.75" />
          </svg>
          Se déconnecter
        </button>
      </div>
    </aside>
  )
}
