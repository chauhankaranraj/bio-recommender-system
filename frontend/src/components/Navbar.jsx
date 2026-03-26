import { NavLink } from 'react-router-dom'
import { Dna, Network, Search, BookOpen, FlaskConical } from 'lucide-react'
import { motion } from 'framer-motion'
import clsx from 'clsx'

const links = [
  { to: '/',         label: 'Dashboard', icon: FlaskConical },
  { to: '/genes',    label: 'Genes',     icon: Search       },
  { to: '/diseases', label: 'Diseases',  icon: BookOpen     },
  { to: '/network',  label: 'Network',   icon: Network      },
  { to: '/about',    label: 'About',     icon: Dna          },
]

export default function Navbar() {
  return (
    <motion.header
      initial={{ y: -20, opacity: 0 }}
      animate={{ y: 0,   opacity: 1 }}
      transition={{ duration: 0.4 }}
      className="sticky top-0 z-50 border-b border-surface-border bg-surface/80 backdrop-blur-xl"
    >
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <NavLink to="/" className="flex items-center gap-2.5 group">
            <div className="w-8 h-8 rounded-lg bg-brand-600 flex items-center justify-center
                            group-hover:bg-brand-500 transition-colors shadow-lg shadow-brand-900/50">
              <Dna size={18} className="text-white" />
            </div>
            <div>
              <span className="font-bold text-white text-sm tracking-tight">GeneDiseaseAI</span>
              <span className="block text-[10px] text-slate-500 leading-none">Recommender System</span>
            </div>
          </NavLink>

          {/* Navigation links */}
          <nav className="hidden md:flex items-center gap-1">
            {links.map(({ to, label, icon: Icon }) => (
              <NavLink
                key={to}
                to={to}
                end={to === '/'}
                className={({ isActive }) =>
                  clsx(
                    'flex items-center gap-1.5 px-3 py-2 rounded-lg text-sm font-medium transition-all duration-200',
                    isActive
                      ? 'bg-brand-600/20 text-brand-400'
                      : 'text-slate-400 hover:text-slate-200 hover:bg-surface-card'
                  )
                }
              >
                <Icon size={15} />
                {label}
              </NavLink>
            ))}
          </nav>

          {/* GitHub badge */}
          <a
            href="https://github.com/ShivaniPimparkar111/biology-recommender"
            target="_blank"
            rel="noopener noreferrer"
            className="btn-ghost text-sm hidden sm:flex"
          >
            <svg viewBox="0 0 24 24" className="w-4 h-4 fill-current">
              <path d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385
                       .6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555
                       -3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225
                       -1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815
                       2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46
                       -1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53
                       .12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04
                       .135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12
                       3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475
                       5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0
                       .315.225.69.825.57A12.02 12.02 0 0024 12c0-6.63-5.37-12-12-12z" />
            </svg>
            GitHub
          </a>
        </div>
      </div>
    </motion.header>
  )
}
