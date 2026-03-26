import { motion } from 'framer-motion'
import { TrendingUp, Info } from 'lucide-react'
import clsx from 'clsx'

/**
 * Renders a single recommendation result with score bar and rank badge.
 *
 * Props:
 *   result   : { name, score, reason }
 *   rank     : 1-based position
 *   type     : 'gene' | 'disease'
 *   onClick  : callback(name)
 *   maxScore : highest score in the list (for normalising bar width)
 */
export default function RecommendationCard({ result, rank, type = 'gene', onClick, maxScore = 1 }) {
  const pct = Math.min(100, (result.score / Math.max(maxScore, 1e-9)) * 100)

  return (
    <motion.div
      layout
      initial={{ opacity: 0, x: -8 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ delay: rank * 0.04 }}
      onClick={() => onClick?.(result.name)}
      className={clsx(
        'group flex items-start gap-4 p-4 rounded-xl border transition-all duration-200 cursor-pointer',
        'bg-surface-card border-surface-border hover:border-brand-600/50 hover:shadow-lg hover:shadow-brand-900/20',
      )}
    >
      {/* Rank badge */}
      <div className={clsx(
        'flex-shrink-0 w-8 h-8 rounded-lg flex items-center justify-center text-xs font-bold',
        rank <= 3
          ? 'bg-brand-600/20 text-brand-400 ring-1 ring-brand-600/40'
          : 'bg-surface text-slate-500',
      )}>
        {rank}
      </div>

      {/* Main content */}
      <div className="flex-1 min-w-0">
        <div className="flex items-center justify-between gap-2 mb-1">
          <span className="font-semibold text-slate-100 truncate group-hover:text-brand-300 transition-colors">
            {result.name}
          </span>
          <span className="flex-shrink-0 text-xs font-mono text-slate-400 bg-surface px-2 py-0.5 rounded-md">
            {result.score.toFixed(4)}
          </span>
        </div>

        {/* Score bar */}
        <div className="h-1 bg-surface rounded-full mb-2">
          <motion.div
            className="score-bar h-1 rounded-full"
            initial={{ width: 0 }}
            animate={{ width: `${pct}%` }}
            transition={{ delay: rank * 0.04 + 0.2, duration: 0.6, ease: 'easeOut' }}
          />
        </div>

        {/* Reason tooltip */}
        {result.reason && (
          <p className="text-xs text-slate-500 flex items-center gap-1 truncate">
            <Info size={10} className="flex-shrink-0" />
            {result.reason}
          </p>
        )}
      </div>
    </motion.div>
  )
}
