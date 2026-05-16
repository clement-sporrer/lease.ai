import { createServerClient } from '@supabase/ssr'
import { NextResponse, type NextRequest } from 'next/server'

const PUBLIC_ROUTES = ['/login']

const ROLE_PREFIXES: Record<string, string[]> = {
  admin:      ['/admin'],
  ops:        ['/ops', '/admin'],
  risk:       ['/risk'],
  commercial: ['/commercial'],
  financier:  ['/financier'],
  cfo:        ['/cfo'],
  comptable:  ['/comptable'],
  partner:    [],
  client:     [],
}

function getAllowedPrefixes(role: string | undefined): string[] {
  if (!role) return []
  return ROLE_PREFIXES[role] ?? []
}

export async function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl

  // Static files, API routes — skip
  if (
    pathname.startsWith('/_next') ||
    pathname.startsWith('/api') ||
    pathname.includes('.')
  ) {
    return NextResponse.next()
  }

  let supabaseResponse = NextResponse.next({ request })

  const supabase = createServerClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
    {
      cookies: {
        getAll() {
          return request.cookies.getAll()
        },
        setAll(cookiesToSet) {
          cookiesToSet.forEach(({ name, value }) => request.cookies.set(name, value))
          supabaseResponse = NextResponse.next({ request })
          cookiesToSet.forEach(({ name, value, options }) =>
            supabaseResponse.cookies.set(name, value, options),
          )
        },
      },
    },
  )

  // Refresh session — critical for token rotation
  const { data: { user } } = await supabase.auth.getUser()

  // Not logged in → redirect to /login
  if (!user) {
    if (PUBLIC_ROUTES.includes(pathname)) return supabaseResponse
    const loginUrl = request.nextUrl.clone()
    loginUrl.pathname = '/login'
    return NextResponse.redirect(loginUrl)
  }

  // Already logged in, trying to access /login → redirect to role home
  if (PUBLIC_ROUTES.includes(pathname)) {
    const role = user.user_metadata?.active_role as string | undefined
    const allowed = getAllowedPrefixes(role)
    const home = allowed[0] ?? '/admin'
    const homeUrl = request.nextUrl.clone()
    homeUrl.pathname = home
    return NextResponse.redirect(homeUrl)
  }

  // RBAC — check role can access this path
  const role = user.user_metadata?.active_role as string | undefined
  const allowed = getAllowedPrefixes(role)
  const canAccess = pathname === '/' || allowed.some((prefix) => pathname.startsWith(prefix))

  if (!canAccess) {
    // Redirect to role's home page instead of 403
    const home = allowed[0] ?? '/admin'
    const homeUrl = request.nextUrl.clone()
    homeUrl.pathname = home
    return NextResponse.redirect(homeUrl)
  }

  return supabaseResponse
}

export const config = {
  matcher: [
    '/((?!_next/static|_next/image|favicon.ico|.*\\.(?:svg|png|jpg|jpeg|gif|webp)$).*)',
  ],
}
