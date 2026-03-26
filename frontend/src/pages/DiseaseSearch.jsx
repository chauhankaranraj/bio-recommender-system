import { useState, useEffect } from 'react'
import { useSearchParams, useNavigate } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import { Activity, ChevronRight, Layers, SlidersHorizontal } from 'lucide-react'
import SearchBar from '../components/SearchBar'
import RecommendationCard from '../components/RecommendationCard'
import LoadingSpinner from '../components/LoadingSpinner'
import { getDisease, recommendGenesForDisease, similarDiseases } from '../services/api'

const MODELS = [
  { value: 'hybrid_rrf',           label: 'Hybrid RRF'  },
  { value: 'content_based',        label: 'TF-IDF'      },
  { value: 'matrix_factorization', label: 'NMF-MF'      },
  { value: 'graph_rwr',            label: 'Graph RWR'   },
]

export default function DiseaseSearch() {
  const [params, setParams] = useSearchParams()
  const navigate             = useNavigate()
  const queryDisease         = params.get('q') || ''

  const [disease, setDisease]       = useState(queryDisease)
  const [diseaseData, setDiseaseData] = useState(null)
  const [genes, setGenes]           = useState(null)
  const [similar, setSimilar]       = useState(null)
  const [loading, setLoading]       = useState(false)
  const [error, setError]           = useState('')
  const [topK, setTopK]             = useState(10)
  const [model, setModel]           = useState('hybrid_rrf')
  const [tab, setTab]               = useState('genes')

  const search = async (d) => {
    if (!d) return
    setLoading(true)
    setError('')
    setDiseaseData(null)
    setGenes(null)
    setSimilar(null)
    try {
      const [info, recs, sim] = await Promise.all([
        getDisease(d),
        recommendGenesForDisease(d, topK, model),
        similarDiseases(d, topK, model),
      ])
      setDiseaseData(info)
      setGenes(recs.results ?? [])
      setSimilar(sim.results ?? [])
      setParams({ q: d })
    } catch (e) {
      setError(e.response?.data?.detail ?? 'Disease not found. Please try another.')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { if (queryDisease) search(queryDisease) }, [])   // eslint-disable-line

  const handleSelect = (val) => { setDisease(val); search(val) }

  const maxScore = (tab === 'genes' ? genes : similar)
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
          <Activity className="text-purple-400 w-8 h-8" />
          Disease Explorer
        </h1>
        <p className="text-slate-400">
          Search for a disease to discover causal gene candidates and molecularly similar diseases.
        </p>
      </div>

      {/* Search + controls */}
      <div className="card space-y-4">
        <SearchBar type="disease" onSelect={handleSelect} initialValue={disease} />

        <div className="flex flex-wrap gap-3 items-center">
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
            onClick={() => search(disease)}
            disabled={!disease || loading}
            className="btn-primary"
          >
            Search <ChevronRight size={16} />
          </button>
        </div>
      </div>

      {error && (
        <div className="p-4 rounded-xl bg-red-900/30 border border-red-800 text-red-300 text-sm">{error}</div>
      )}

      {loading && <LoadingSpinner message={`Analysing "${disease}"…`} />}

      <AnimatePresence>
        {diseaseData && !loading && (
          <motion.div key="results" initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} className="space-y-6">
            {/* Disease info card */}
            <div className="card flex flex-wrap items-center gap-4">
              <div className="w-12 h-12 rounded-xl bg-purple-900/50 border border-purple-800 flex items-center justify-center">
                <Activity className="text-purple-400 w-6 h-6" />
              </div>
              <div>
                <h2 className="text-2xl font-bold text-white">{diseaseData.disease}</h2>
                <p className="text-slate-400 text-sm">{diseaseData.gene_count} associated genes</p>
              </div>
              <button
                onClick={() => navigate(`/network?entity=${encodeURIComponent(diseaseData.disease)}`)}
                className="ml-auto btn-ghost text-sm"
              >
                View Network
              </button>
            </div>

            {/* Tabs */}
            <div className="flex gap-1 p-1 bg-surface-card rounded-xl w-fit border border-surface-border">
              {[
                { key: 'genes',   label: `Gene Recs (${genes?.length ?? 0})` },
                { key: 'similar', label: `Similar Diseases (${similar?.length ?? 0})` },
              ].map(t => (
                <button
                  key={t.key}
                  onClick={() => setTab(t.key)}
                  className={`px-4 py-1.5 rounded-lg text-sm font-medium transition-all ${
                    tab === t.key ? 'bg-purple-600 text-white shadow' : 'text-slate-400 hover:text-slate-200'
                  }`}
                >
                  {t.label}
                </button>
              ))}
            </div>

            <div className="grid gap-2">
              {(tab === 'genes' ? genes : similar)?.map((r, i) => (
                <RecommendationCard
                  key={r.name}
                  result={r}
                  rank={i + 1}
                  type={tab === 'genes' ? 'gene' : 'disease'}
                  maxScore={maxScore}
                  onClick={(name) =>
                    tab === 'genes'
                      ? navigate(`/genes?q=${name}`)
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
