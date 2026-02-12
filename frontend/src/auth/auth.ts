export interface Session {
  token: string
  role: 'Admin' | 'SiteUser'
  site?: string
}

export const setSession = (session: Session) => {
  localStorage.setItem('token', session.token)
  localStorage.setItem('role', session.role)
  if (session.site) localStorage.setItem('site', session.site)
}

export const getSession = (): Session | null => {
  const token = localStorage.getItem('token')
  const role = localStorage.getItem('role') as 'Admin' | 'SiteUser' | null
  const site = localStorage.getItem('site') || undefined
  if (!token || !role) return null
  return { token, role, site }
}

export const clearSession = () => {
  localStorage.clear()
}
