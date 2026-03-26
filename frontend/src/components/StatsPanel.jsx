import { motion } from 'framer-motion'
import { Database, Dna, Activity, BarChart2 } from 'lucide-react'
import clsx from 'clsx'

const statConfig = [
  {
    key:   'total_associations',
    label: 'Associations',
    icon:  Database,
    color: 'text-brand-400',
    bg:    'bg-brand-900/30',
  },
  {
    key:   'unique_genes',
    label: 'Unique Genes',
    icon:  Dna,
    color: 'text-emerald-400',
    bg:    'bg-emerald-900/30',
  },
  {
    key:   'unique_diseases',
    label: 'Diseases',
    icon:  Activity,
    color: 'text-purple-400',
    bg:    'bg-purple-900/30',
  },
  {
    key:   'avg_diseases_per_gene',
    label: 'Avg Diseases / Gene',
    icon:  BarChart2,
    color: 'text-amber-400',
    bg:    'bg-amber-900/30',
    format: v => v.toFixed(1),
  },
]

function StatCard({ config, value, index }) {
  const Icon = config.icon
  const display = config.format ? config.format(value) : value?.toLocaleString() ?? '—'

  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.1 }}
      className="card flex items-center gap-4"
    >
      <div className={clsx('w-12 h-12 rounded-xl flex items-center justify-center flex-shrink-0', config.bg)}>
        <Icon className={clsx('w-6 h-6', config.color)} />
      </div>
      <div>
        <p className="text-2xl font-bold text-white tabular-nums">{display}</p>
        <p className="text-sm text-slate-400">{config.label}</p>
      </div>
    </motion.div>
  )
}

export default function StatsPanel({ stats }) {
  if (!stats) return null

  return (
    <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
      {statConfig.map((cfg, i) => (
        <StatCard
          key={cfg.key}
          config={cfg}
          value={stats[cfg.key]}
          index={i}
        />
      ))}
    </div>
  )
}
