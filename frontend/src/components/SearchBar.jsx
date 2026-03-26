import { useState, useRef, useEffect, useCallback } from 'react'
import { Search, X, Loader2 } from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'
import clsx from 'clsx'
import { listGenes, listDiseases } from '../services/api'

/**
 * Smart search bar with live autocomplete for genes and diseases.
 *
 * Props:
 *   type        : 'gene' | 'disease' | 'both'
 *   placeholder : hint text
 *   onSelect    : callback(value, type)
 *   initialValue: pre-filled value
 */
export default function SearchBar({ type = 'both', placeholder, onSelect, initialValue = '' }) {
  const [query, setQuery]           = useState(initialValue)
  const [suggestions, setSuggestions] = useState([])
  const [loading, setLoading]       = useState(false)
  const [open, setOpen]             = useState(false)
  const ref                         = useRef(null)
  const debounceRef                 = useRef(null)

  const fetchSuggestions = useCallback(async (q) => {
    if (!q || q.length < 2) { setSuggestions([]); return }
    setLoading(true)
    try {
      const fetchers = []
      if (type === 'gene' || type === 'both')
        fetchers.push(listGenes(1, 8, q).then(r => r.results.map(g => ({ label: g, kind: 'gene' }))))
      if (type === 'disease' || type === 'both')
        fetchers.push(listDiseases(1, 8, q).then(r => r.results.map(d => ({ label: d, kind: 'disease' }))))
      const results = (await Promise.all(fetchers)).flat().slice(0, 12)
      setSuggestions(results)
      setOpen(results.length > 0)
    } catch {
      setSuggestions([])
    } finally {
      setLoading(false)
    }
  }, [type])

  const handleChange = (e) => {
    const val = e.target.value
    setQuery(val)
    clearTimeout(debounceRef.current)
    debounceRef.current = setTimeout(() => fetchSuggestions(val), 280)
  }

  const handleSelect = (item) => {
    setQuery(item.label)
    setOpen(false)
    onSelect?.(item.label, item.kind)
  }

  const handleClear = () => {
    setQuery('')
    setSuggestions([])
    setOpen(false)
  }

  // Close dropdown on outside click
  useEffect(() => {
    const listener = (e) => { if (!ref.current?.contains(e.target)) setOpen(false) }
    document.addEventListener('mousedown', listener)
    return () => document.removeEventListener('mousedown', listener)
  }, [])

  return (
    <div ref={ref} className="relative w-full">
      <div className="relative">
        <Search className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-500 w-4 h-4" />
        <input
          value={query}
          onChange={handleChange}
          onFocus={() => suggestions.length > 0 && setOpen(true)}
          placeholder={placeholder ?? (type === 'gene' ? 'Search gene (e.g. BRCA1, TP53)' : 'Search disease…')}
          className={clsx('input-field pl-10 pr-10', loading && 'pr-12')}
        />
        {loading && (
          <Loader2 className="absolute right-4 top-1/2 -translate-y-1/2 text-slate-500 w-4 h-4 animate-spin" />
        )}
        {!loading && query && (
          <button onClick={handleClear} className="absolute right-4 top-1/2 -translate-y-1/2 text-slate-500 hover:text-slate-300">
            <X size={14} />
          </button>
        )}
      </div>

      <AnimatePresence>
        {open && suggestions.length > 0 && (
          <motion.ul
            initial={{ opacity: 0, y: -6 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -6 }}
            transition={{ duration: 0.15 }}
            className="absolute z-50 w-full mt-1 bg-surface-card border border-surface-border rounded-xl shadow-2xl overflow-hidden"
          >
            {suggestions.map((s, i) => (
              <li
                key={`${s.kind}-${s.label}-${i}`}
                onMouseDown={() => handleSelect(s)}
                className="flex items-center justify-between px-4 py-2.5 hover:bg-brand-600/10 cursor-pointer transition-colors"
              >
                <span className="text-slate-200 text-sm truncate">{s.label}</span>
                <span className={clsx('text-xs px-2 py-0.5 rounded-full ml-2 flex-shrink-0',
                  s.kind === 'gene'
                    ? 'bg-brand-900/60 text-brand-400'
                    : 'bg-purple-900/60 text-purple-400'
                )}>
                  {s.kind}
                </span>
              </li>
            ))}
          </motion.ul>
        )}
      </AnimatePresence>
    </div>
  )
}
