import { useState, useEffect, useRef } from 'react'
import { useSearchParams } from 'react-router-dom'
import { motion } from 'framer-motion'
import { Network, ZoomIn, ZoomOut, RefreshCw, Download } from 'lucide-react'
import SearchBar from '../components/SearchBar'
import NetworkGraph from '../components/NetworkGraph'
import LoadingSpinner from '../components/LoadingSpinner'
import { getNetwork } from '../services/api'

export default function NetworkPage() {
  const [params, setParams] = useSearchParams()
  const initialEntity        = params.get('entity') || ''

  const [entity, setEntity]   = useState(initialEntity)
  const [graphData, setGraph] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError]     = useState('')
  const [depth, setDepth]     = useState(2)
  const [maxNodes, setMaxNodes] = useState(80)

  const fetchGraph = async (e) => {
    if (!e) return
    setLoading(true)
    setError('')
    try {
      const data = await getNetwork(e, depth, maxNodes)
      setGraph(data)
      setParams({ entity: e })
    } catch (err) {
      setError(err.response?.data?.detail ?? 'Entity not found in the network.')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { if (initialEntity) fetchGraph(initialEntity) }, [])  // eslint-disable-line

  const handleSelect = (val) => { setEntity(val); fetchGraph(val) }

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10 space-y-6"
    >
      {/* Header */}
      <div className="space-y-1">
        <h1 className="text-3xl font-bold text-white flex items-center gap-3">
          <Network className="text-emerald-400 w-8 h-8" />
          Knowledge Graph
        </h1>
        <p className="text-slate-400">
          Explore the bipartite gene–disease network. Drag nodes to rearrange. Scroll to zoom.
        </p>
      </div>

      {/* Controls */}
      <div className="card space-y-4">
        <SearchBar type="both" onSelect={handleSelect} initialValue={entity}
          placeholder="Enter gene (e.g. BRCA1) or disease…" />

        <div className="flex flex-wrap gap-4 items-center">
          <label className="flex items-center gap-2 text-sm text-slate-400">
            Depth:
            <select
              value={depth}
              onChange={e => setDepth(Number(e.target.value))}
              className="bg-surface border border-surface-border text-slate-300 rounded-lg px-2 py-1 text-sm outline-none focus:border-brand-500"
            >
              {[1, 2, 3].map(d => <option key={d} value={d}>{d}</option>)}
            </select>
          </label>

          <label className="flex items-center gap-2 text-sm text-slate-400">
            Max nodes:
            <select
              value={maxNodes}
              onChange={e => setMaxNodes(Number(e.target.value))}
              className="bg-surface border border-surface-border text-slate-300 rounded-lg px-2 py-1 text-sm outline-none focus:border-brand-500"
            >
              {[40, 80, 120, 200].map(n => <option key={n} value={n}>{n}</option>)}
            </select>
          </label>

          <button
            onClick={() => fetchGraph(entity)}
            disabled={!entity || loading}
            className="btn-primary"
          >
            <RefreshCw size={15} className={loading ? 'animate-spin' : ''} />
            {loading ? 'Loading…' : 'Render Graph'}
          </button>
        </div>
      </div>

      {error && (
        <div className="p-4 rounded-xl bg-red-900/30 border border-red-800 text-red-300 text-sm">{error}</div>
      )}

      {loading && <LoadingSpinner message="Building network graph…" />}

      {graphData && !loading && (
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="space-y-4">
          {/* Graph metadata */}
          <div className="flex items-center gap-4 text-sm text-slate-400">
            <span>{graphData.nodes.length} nodes</span>
            <span>·</span>
            <span>{graphData.links.length} edges</span>
            <span>·</span>
            <span>
              {graphData.nodes.filter(n => n.type === 'gene').length} genes,&nbsp;
              {graphData.nodes.filter(n => n.type === 'disease').length} diseases
            </span>
          </div>

          {/* D3 Network */}
          <NetworkGraph data={graphData} width={1200} height={580} />

          {/* Legend */}
          <div className="flex gap-6 text-xs text-slate-400">
            <span className="flex items-center gap-1.5">
              <span className="w-3 h-3 rounded-full bg-brand-500 inline-block" /> Gene node
            </span>
            <span className="flex items-center gap-1.5">
              <span className="w-3 h-3 rounded-full bg-purple-600 inline-block" /> Disease node
            </span>
            <span className="flex items-center gap-1.5">
              Node size ∝ degree (larger = more connections)
            </span>
          </div>
        </motion.div>
      )}
    </motion.div>
  )
}
