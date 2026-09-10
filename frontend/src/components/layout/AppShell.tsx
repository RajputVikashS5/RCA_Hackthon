import { useEffect, useState } from 'react'
import { NavLink, Outlet } from 'react-router-dom'
import {
  Activity,
  ChartNoAxesCombined,
  ChevronRight,
  HeartPulse,
  History,
  Settings,
  ShieldAlert,
  Sparkles,
  TrendingUp,
  X,
} from 'lucide-react'

const links = [
  { to: '/', label: 'Dashboard', icon: ChartNoAxesCombined },
  { to: '/activity', label: 'Incident Activity', icon: TrendingUp },
  { to: '/analyze', label: 'Analyze Incident', icon: Sparkles },
  { to: '/similar', label: 'Similar Incidents', icon: Activity },
  { to: '/incidents', label: 'Analysis History', icon: History },
  { to: '/system-health', label: 'System Health', icon: HeartPulse },
  { to: '/settings', label: 'Settings', icon: Settings },
]

type ThemeMode = 'light' | 'dark'
const THEME_KEY = 'rca-theme'

function applyTheme(mode: ThemeMode) {
  document.body.classList.toggle('theme-dark', mode === 'dark')
}

export function AppShell() {
  const [open, setOpen] = useState(false)

  useEffect(() => {
    const saved = localStorage.getItem(THEME_KEY)
    const initial: ThemeMode = saved === 'dark' ? 'dark' : 'light'
    applyTheme(initial)
  }, [])

  return (
    <div className="shell">
      <aside className={`sidebar ${open ? 'is-open' : ''}`}>
        <div className="brand">
          <span className="brand-mark">
            <ShieldAlert size={21} />
          </span>
          <span>RCA Assistant</span>
          <button className="mobile-close" onClick={() => setOpen(false)} aria-label="Close navigation">
            <X size={20} />
          </button>
        </div>
        <nav aria-label="Main navigation">
          {links.map(({ to, label, icon: Icon }) => (
            <NavLink key={to} to={to} end={to === '/'} onClick={() => setOpen(false)}>
              <Icon size={18} />
              <span>{label}</span>
              <ChevronRight className="nav-chevron" size={15} />
            </NavLink>
          ))}
        </nav>
      </aside>

      {open && <button className="sidebar-backdrop" aria-label="Close navigation" onClick={() => setOpen(false)} />}

      <main className="workspace">
        <div className="page">
          <Outlet />
        </div>
      </main>

      <nav className="mobile-nav">
        {links.slice(0, 4).map(({ to, label, icon: Icon }) => (
          <NavLink to={to} key={to} end={to === '/'}>
            <Icon size={18} />
            <span>{label.split(' ')[0]}</span>
          </NavLink>
        ))}
      </nav>
    </div>
  )
}