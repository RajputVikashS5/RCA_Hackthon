import { useEffect, useState } from 'react'
import { NavLink, Outlet, useNavigate } from 'react-router-dom'
import {
  Activity,
  Bell,
  Bot,
  ChartNoAxesCombined,
  ChevronRight,
  HeartPulse,
  History,
  Menu,
  Moon,
  Search,
  Settings,
  ShieldAlert,
  Sparkles,
  Sun,
  User,
  X,
} from 'lucide-react'

const links = [
  { to: '/', label: 'Dashboard', icon: ChartNoAxesCombined },
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
  const navigate = useNavigate()
  const [open, setOpen] = useState(false)
  const [search, setSearch] = useState('')
  const [theme, setTheme] = useState<ThemeMode>('light')
  const [profileOpen, setProfileOpen] = useState(false)

  useEffect(() => {
    const saved = localStorage.getItem(THEME_KEY)
    const initial: ThemeMode = saved === 'dark' ? 'dark' : 'light'
    setTheme(initial)
    applyTheme(initial)
  }, [])

  const goSearch = (e: React.FormEvent) => {
    e.preventDefault()
    const term = search.trim()
    if (!term) return
    navigate(`/similar?q=${encodeURIComponent(term)}`)
  }

  const toggleTheme = () => {
    setTheme((current) => {
      const next: ThemeMode = current === 'dark' ? 'light' : 'dark'
      localStorage.setItem(THEME_KEY, next)
      applyTheme(next)
      return next
    })
  }

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
        <div className="sidebar-foot">
          <a href="mailto:support@example.com">
            <Bot size={18} />
            Help & support
          </a>
          <p>
            Evidence-grounded RCA
            <br />
            for operations teams
          </p>
        </div>
      </aside>

      {open && <button className="sidebar-backdrop" aria-label="Close navigation" onClick={() => setOpen(false)} />}

      <main className="workspace">
        <header className="topbar">
          <button className="icon-button menu-button" aria-label="Open navigation" onClick={() => setOpen(true)}>
            <Menu size={20} />
          </button>

          <form className="global-search" onSubmit={goSearch}>
            <Search size={17} />
            <input
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search historical incidents..."
              aria-label="Search historical incidents"
            />
          </form>

          <div className="top-actions">
            <button
              className="icon-button"
              aria-label="Open system health"
              title="Open system health"
              onClick={() => navigate('/system-health')}
            >
              <Bell size={18} />
            </button>
            <button
              className="icon-button"
              aria-label="Toggle theme"
              title={theme === 'dark' ? 'Switch to light mode' : 'Switch to dark mode'}
              onClick={toggleTheme}
            >
              {theme === 'dark' ? <Sun size={18} /> : <Moon size={18} />}
            </button>

            <div className="profile-menu" onBlur={() => setProfileOpen(false)}>
              <button
                type="button"
                className="profile-placeholder"
                title="Open user menu"
                onClick={() => setProfileOpen((x) => !x)}
                aria-haspopup="menu"
                aria-expanded={profileOpen}
              >
                OP
              </button>
              {profileOpen && (
                <div className="profile-dropdown" role="menu">
                  <button type="button" onClick={() => navigate('/settings')}>
                    <User size={15} />
                    Profile settings
                  </button>
                  <button type="button" onClick={() => navigate('/incidents')}>
                    <History size={15} />
                    Analysis history
                  </button>
                </div>
              )}
            </div>
          </div>
        </header>

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