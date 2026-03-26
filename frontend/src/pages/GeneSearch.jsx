import { useState, useEffect } from 'react'
import { useSearchParams, useNavigate } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import { Dna, ChevronRight, Layers, SlidersHorizontal } from 'lucide-react'
import SearchBar from '../components/SearchBar'
import RecommendationCard from '../components/RecommendationCard'
import LoadingSpinner from '../components/LoadingSpinner'
import { getGene, recommendDiseasesForGene, similarGenes } from '../services/api'

const MODELS = [
  { value: 'hybrid_rrf',          label: 'Hybrid RRF'   },
  { value: 'content_based',       label: 'TF-IDF'       },
  { value: 'matrix_factorization',label: 'NMF-MF'       },
  { value: 'graph_rwr',           label: 'Graph RWR'    },
]

export default function GeneSearch() {
  const [params, setParams] = useSearchParams()
  const navigate             = useNavigate()
  const queryGene            = params.get('q') || ''

  const [gene, setGene]       = useState(queryGene)
  const [geneData, setGeneData] = useState(null)
  const [diseases, setDiseases] = useState(null)
  const [similar, setSimilar]   = useState(null)
  const [loading, setLoading]   = useState(false)
  const [error, setError]       = useState('')
  const [topK, setTopK]         = useState(10)
  const [model, setModel]       = useState('hybrid_rrf')
  const [tab, setTab]           = useState('diseases')   // 'diseases' | 'similar'

  const search = async (g) => {
    if (!g) return
    setLoading(true)
    setError('')
    setGeneData(null)
    setDiseases(null)
    setSimilar(null)
    try {
      const [info, recs, sim] = await Promise.all([
        getGene(g),
        recommendDiseasesForGene(g, topK, model),
        similarGenes(g, topK, model),
      ])
      setGeneData(info)
      setDiseases(recs.results ?? [])
      setSimilar(sim.results ?? [])
      setParams({ q: g })
    } catch (e) {
      setError(e.response?.data?.detail ?? 'Gene not found. Please try another.')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { if (queryGene) search(queryGene) }, [])   // eslint-disable-line

  const handleSelect = (val) => { setGene(val); search(val) }

  const maxScore = (tab === 'diseases' ? diseases : similar)
    ?.reduce((m, r) => Math.max(m, r.score), 0) ?? 1

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-10 space-y-8"
    >
      {/* Header */}
      <div className="space-y-1">
        <h1 className="text-3xl font-bold text-white flex items-center gap-3">
          <Dna className="text-brand-400 w-8 h-8" />
          Gene Explorer
        </h1>
        <p className="text-slate-400">Search for a gene to discover disease associations and functionally similar genes.</p>
      </div>

      {/* Search + controls */}
      <div className="card space-y-4">
        <SearchBar type="gene" onSelect={handleSelect} initialValue={gene} />

        <div className="flex flex-wrap gap-3 items-center">
          {/* Model picker */}
          <div className="flex items-center gap-2">
            <SlidersHorizontal size={14} className="text-slate-500" />
            <select
              value={model}
              onChange={e => setModel(e.target.value)}
              className="bg-surface border border-surface-border text-slate-300 rounded-lg px-3 py-1.5 text-sm outline-none focus:border-brand-500"
            >
              {MODELS.map(m => <option key={m.value} value={m.value}>{m.label}</option>)}
            </select>
          </div>

          {/* Top-K picker */}
          <div className="flex items-center gap-2">
            <Layers size={14} className="text-slate-500" />
            <select
              value={topK}
              onChange={e => setTopK(Number(e.target.value))}
              className="bg-surface border border-surface-border text-slate-300 rounded-lg px-3 py-1.5 text-sm outline-none focus:border-brand-500"
            >
              {[5, 10, 20, 30].map(k => <option key={k} value={k}>Top {k}</option>)}
            </select>
          </div>

          <button
            onClick={() => search(gene)}
            disabled={!gene || loading}
            className="btn-primary"
          >
            Search <ChevronRight size={16} />
          </button>
        </div>
      </div>

      {/* Error */}
      {error && (
        <div className="p-4 rounded-xl bg-red-900/30 border border-red-800 text-red-300 text-sm">
          {error}
        </div>
      )}

      {/* Loading */}
      {loading && <LoadingSpinner message={`Fetching recommendations for ${gene}…`} />}

      {/* Results */}
      <AnimatePresence>
        {geneData && !loading && (
          <motion.div
            key="results"
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            className="space-y-6"
          >
            {/* Gene info card */}
            <div className="card flex flex-wrap items-center gap-4">
              <div className="w-12 h-12 rounded-xl bg-brand-900/50 border border-brand-800 flex items-center justify-center">
                <Dna className="text-brand-400 w-6 h-6" />
              </div>
              <div>
                <h2 className="text-2xl font-bold text-white">{geneData.gene}</h2>
                <p className="text-slate-400 text-sm">{geneData.disease_count} known disease associations</p>
              </div>

              <button
                onClick={() => navigate(`/network?entity=${geneData.gene}`)}
                className="ml-auto btn-ghost text-sm"
              >
                View Network
              </button>
            </div>

            {/* Tabs */}
            <div className="flex gap-1 p-1 bg-surface-card rounded-xl w-fit border border-surface-border">
              {[
                { key: 'diseases', label: `Disease Recs (${diseases?.length ?? 0})` },
                { key: 'similar',  label: `Similar Genes (${similar?.length ?? 0})` },
              ].map(t => (
                <button
                  key={t.key}
                  onClick={() => setTab(t.key)}
                  className={`px-4 py-1.5 rounded-lg text-sm font-medium transition-all ${
                    tab === t.key
                      ? 'bg-brand-600 text-white shadow'
                      : 'text-slate-400 hover:text-slate-200'
                  }`}
                >
                  {t.label}
                </button>
              ))}
            </div>

            {/* Recommendation list */}
            <div className="grid gap-2">
              {(tab === 'diseases' ? diseases : similar)?.map((r, i) => (
                <RecommendationCard
                  key={r.name}
                  result={r}
                  rank={i + 1}
                  type={tab === 'diseases' ? 'disease' : 'gene'}
                  maxScore={maxScore}
                  onClick={(name) =>
                    tab === 'diseases'
                      ? navigate(`/diseases?q=${encodeURIComponent(name)}`)
                      : search(name)
                  }
                />
              ))}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  )
}
