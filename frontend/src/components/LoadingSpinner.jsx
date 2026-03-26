import { Loader2 } from 'lucide-react'
import { motion } from 'framer-motion'

export default function LoadingSpinner({ message = 'Loading…' }) {
  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="flex flex-col items-center justify-center gap-3 py-16 text-slate-400"
    >
      <Loader2 className="w-8 h-8 animate-spin text-brand-500" />
      <p className="text-sm">{message}</p>
    </motion.div>
  )
}

export function SkeletonCard() {
  return (
    <div className="card">
      <div className="flex items-start gap-4">
        <div className="skeleton w-8 h-8 rounded-lg flex-shrink-0" />
        <div className="flex-1 space-y-2">
          <div className="skeleton h-4 rounded w-3/4" />
          <div className="skeleton h-2 rounded w-full" />
          <div className="skeleton h-2 rounded w-1/2" />
        </div>
      </div>
    </div>
  )
}
