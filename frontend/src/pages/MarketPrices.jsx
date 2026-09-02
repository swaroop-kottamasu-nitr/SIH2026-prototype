import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import axios from 'axios'
import { motion } from 'framer-motion'
import AppLayout from '../components/AppLayout'
import AdvisoryMarkdown from '../components/AdvisoryMarkdown'
import { 
  FiArrowLeft, FiTrendingUp, FiTrendingDown, FiMinus, 
  FiMapPin, FiInfo, FiZap, FiCheckCircle, FiCompass, FiShield 
} from 'react-icons/fi'
import './FeaturePage.css'

const POPULAR = [
  { name: 'Rice', key: 'rice' },
  { name: 'Chilli', key: 'chilli' },
  { name: 'Cotton', key: 'cotton' },
  { name: 'Groundnut', key: 'groundnut' },
  { name: 'Maize', key: 'maize' },
  { name: 'Tomato', key: 'tomato' },
  { name: 'Onion', key: 'onion' },
  { name: 'Turmeric', key: 'turmeric' }
]

export default function MarketPrices({ user, onLogout, onUserUpdate }) {
  const { t } = useTranslation()
  const [activeTab, setActiveTab] = useState('overview') // 'overview' | 'compare'

  // Overview states
  const [crop, setCrop] = useState('')
  const [prices, setPrices] = useState(null)
  const [seasonData, setSeasonData] = useState(null)
  const [loading, setLoading] = useState(false)
  const [seasonLoading, setSeasonLoading] = useState(true)

  const [states, setStates] = useState(['Andhra Pradesh'])
  const [cities, setCities] = useState([])
  const [selectedState, setSelectedState] = useState('Andhra Pradesh')
  const [selectedCity, setSelectedCity] = useState('')

  const location = selectedCity || selectedState || 'Andhra Pradesh'

  // Comparison states
  const [compareCrop, setCompareCrop] = useState('Chilli')
  const [compareData, setCompareData] = useState(null)
  const [compareLoading, setCompareLoading] = useState(false)

  // Minimal AI Advisory Integration
  const [aiLoading, setAiLoading] = useState(false)
  const [aiAdvisory, setAiAdvisory] = useState(null)

  useEffect(() => {
    axios.get('/api/market/states')
      .then(res => {
        const list = res.data?.states || []
        if (list.length) setStates(list)
      })
      .catch(() => {})
  }, [])

  useEffect(() => {
    if (!selectedState) {
      setCities([])
      setSelectedCity('')
      return
    }
    axios.get(`/api/market/cities/${encodeURIComponent(selectedState)}`)
      .then(res => {
        setCities(res.data?.cities || [])
      })
      .catch(() => setCities([]))
  }, [selectedState])

  useEffect(() => {
    if (!location) return
    setSeasonLoading(true)
    axios.post('/api/market/season-prices', { location })
      .then(res => setSeasonData(res.data))
      .catch(() => setSeasonData(null))
      .finally(() => setSeasonLoading(false))
  }, [location])

  const searchCrop = (name) => {
    const n = name || crop
    if (!n) return
    setLoading(true)
    axios.get(`/api/market/prices/${encodeURIComponent(n)}`, { params: { location } })
      .then(res => setPrices(res.data))
      .catch(() => { setPrices(null); alert(t('market.noPriceFound', { defaultValue: 'No prices found for this crop' })) })
      .finally(() => setLoading(false))
  }

  const fetchComparison = async (cName) => {
    const targetCrop = cName || compareCrop
    setCompareLoading(true)
    try {
      const res = await axios.post('/api/v1/market/compare', {
        crop: targetCrop,
        location,
        language: getEffectiveLanguage(user)
      })
      if (res.data) {
        setCompareData(res.data)
      }
    } catch (err) {
      console.error('Comparison fetch error:', err)
    } finally {
      setCompareLoading(false)
    }
  }

  useEffect(() => {
    if (activeTab === 'compare') {
      fetchComparison(compareCrop)
    }
  }, [activeTab, compareCrop, location, i18n.language, user?.language])

  const handleAskMarketAdvisory = async () => {
    if (aiLoading) return
    setAiLoading(true)
    try {
      const prompt = `Current market price advisory for ${compareCrop || 'crops'} in ${location}. Should I sell now or wait?`
      const res = await axios.post('/api/v1/advisory', {
        question: prompt,
        language: user?.language || 'en',
        context: {
          crop: compareCrop,
          location
        }
      }, { timeout: 15000 })
      if (res.data?.advisory) {
        setAiAdvisory(res.data.advisory)
      }
    } catch (err) {
      console.error('Market advisory error:', err)
    } finally {
      setAiLoading(false)
    }
  }

  return (
    <AppLayout user={user} onLogout={onLogout} onUserUpdate={onUserUpdate}>
      <div className="feature-page">
        <div className="container">
          <Link to="/dashboard" className="back-link"><FiArrowLeft size={16} /> {t('common.back', { defaultValue: 'Back to Dashboard' })}</Link>
          
          <div className="page-header" style={{ marginBottom: 'var(--space-4)' }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: 'var(--space-2)' }}>
              <h1 className="page-title">{t('market.title', { defaultValue: 'Live Mandi & Market Prices' })}</h1>
              <span className="source-badge source-sample" style={{ fontSize: '11px', padding: '4px 12px', borderRadius: '20px', background: 'rgba(31, 122, 69, 0.12)', color: 'var(--brand-primary)', border: '1px solid rgba(31, 122, 69, 0.3)', fontWeight: 700 }}>
                📊 {t('market.sample_badge', { defaultValue: 'SAMPLE MARKET DATA' })}
              </span>
            </div>
            <p className="page-subtitle">
              {seasonData
                ? t('market.subtitleSeason', { season: seasonData.season, state: seasonData.state, defaultValue: `Prevailing mandi rates for ${seasonData.season} season in ${seasonData.state}` })
                : t('market.subtitleDefault', { defaultValue: 'Real-time price intelligence across APMC yards' })}
            </p>

            {/* State & City Filter */}
            <div className="market-location-select" style={{ display: 'flex', flexWrap: 'wrap', gap: 'var(--space-3)', marginTop: 'var(--space-2)', alignItems: 'center' }}>
              <div>
                <label className="param-label" style={{ display: 'block', marginBottom: 'var(--space-1)', fontSize: '12px', fontWeight: 600 }}>{t('market.selectState', { defaultValue: 'State' })}</label>
                <select
                  className="param-select"
                  value={selectedState}
                  onChange={(e) => { setSelectedState(e.target.value); setSelectedCity('') }}
                  style={{ padding: '6px 12px', borderRadius: 'var(--radius-md)', border: '1px solid var(--color-border)', background: 'var(--color-surface)' }}
                >
                  {states.map((s) => (
                    <option key={s} value={s}>{s}</option>
                  ))}
                </select>
              </div>
              <div>
                <label className="param-label" style={{ display: 'block', marginBottom: 'var(--space-1)', fontSize: '12px', fontWeight: 600 }}>{t('market.selectCity', { defaultValue: 'City / Mandi' })}</label>
                <select
                  className="param-select"
                  value={selectedCity}
                  onChange={(e) => setSelectedCity(e.target.value)}
                  style={{ padding: '6px 12px', borderRadius: 'var(--radius-md)', border: '1px solid var(--color-border)', background: 'var(--color-surface)' }}
                >
                  <option value="">{t('market.allMandis', { defaultValue: 'All Mandis in State' })}</option>
                  {cities.map((c) => (
                    <option key={c} value={c}>{c}</option>
                  ))}
                </select>
              </div>
            </div>
          </div>

          {/* Navigation Tabs */}
          <div style={{ display: 'flex', gap: 'var(--space-2)', marginBottom: 'var(--space-6)', borderBottom: '1px solid var(--color-border)', paddingBottom: 'var(--space-2)' }}>
            <button
              type="button"
              className={`btn ${activeTab === 'overview' ? 'btn-primary' : 'btn-secondary'}`}
              onClick={() => setActiveTab('overview')}
              style={{ padding: '8px 16px', borderRadius: 'var(--radius-md)', fontSize: '13px', fontWeight: 700 }}
            >
              📈 {t('market.title', { defaultValue: 'Market Overview' })}
            </button>
            <button
              type="button"
              className={`btn ${activeTab === 'compare' ? 'btn-primary' : 'btn-secondary'}`}
              onClick={() => setActiveTab('compare')}
              style={{ padding: '8px 16px', borderRadius: 'var(--radius-md)', fontSize: '13px', fontWeight: 700 }}
            >
              ⚖️ {t('market.compare.title', { defaultValue: 'Mandi Comparison' })}
            </button>
          </div>

          {/* TAB 1: OVERVIEW */}
          {activeTab === 'overview' && (
            <div>
              {/* Popular Commodities */}
              <div className="card" style={{ marginBottom: 'var(--space-6)' }}>
                <h3 className="card-title" style={{ fontSize: 'var(--text-base)', marginBottom: 'var(--space-3)' }}>
                  🌾 {t('market.popularCrops', { defaultValue: 'Popular Commodities' })}
                </h3>
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: 'var(--space-2)' }}>
                  {POPULAR.map((p) => (
                    <button
                      key={p.name}
                      type="button"
                      className={`btn ${crop === p.name ? 'btn-primary' : 'btn-secondary'}`}
                      onClick={() => { setCrop(p.name); searchCrop(p.name); }}
                      style={{ padding: '6px 14px', borderRadius: '20px', fontSize: '12px' }}
                    >
                      {t(`crops.${p.key}`, { defaultValue: p.name })}
                    </button>
                  ))}
                </div>
              </div>

              {/* Season Commodities Grid */}
              <div className="card">
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 'var(--space-4)' }}>
                  <h3 className="card-title">
                    {t('market.seasonPrices', { defaultValue: 'Prevailing APMC Mandi Rates' })}
                  </h3>
                  <span style={{ fontSize: '12px', color: 'var(--color-text-tertiary)' }}>
                    {seasonData?.state || location}
                  </span>
                </div>

                {seasonLoading ? (
                  <div className="loading-state">{t('common.loading', { defaultValue: 'Loading market data...' })}</div>
                ) : seasonData?.crops && seasonData.crops.length > 0 ? (
                  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(260px, 1fr))', gap: 'var(--space-4)' }}>
                    {seasonData.crops.map((c, i) => (
                      <div 
                        key={i} 
                        style={{
                          background: 'var(--color-background-secondary)',
                          border: '1px solid var(--color-border)',
                          borderRadius: 'var(--radius-lg)',
                          padding: 'var(--space-4)',
                          display: 'flex',
                          flexDirection: 'column',
                          justifyContent: 'space-between'
                        }}
                      >
                        <div>
                          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 'var(--space-2)' }}>
                            <span style={{ fontWeight: 800, fontSize: 'var(--text-base)', color: 'var(--brand-primary)' }}>
                              {t(`crops.${c.crop_name.toLowerCase().replace(/[^a-z]/g, '')}`, { defaultValue: c.crop_name })}
                            </span>
                            <span style={{ 
                              fontSize: '11px', 
                              fontWeight: 700, 
                              padding: '2px 8px', 
                              borderRadius: '12px',
                              background: c.trend === 'up' ? 'rgba(31, 122, 69, 0.12)' : c.trend === 'down' ? 'rgba(220, 38, 38, 0.12)' : 'rgba(107, 114, 128, 0.12)',
                              color: c.trend === 'up' ? 'var(--brand-primary)' : c.trend === 'down' ? '#DC2626' : '#4B5563'
                            }}>
                              {c.trend === 'up' ? '↑ ' + t('trend.up', { defaultValue: 'UP' }) : c.trend === 'down' ? '↓ ' + t('trend.down', { defaultValue: 'DOWN' }) : '→ ' + t('trend.stable', { defaultValue: 'STABLE' })} ({Math.abs(c.change_percent)}%)
                            </span>
                          </div>
                          <div style={{ fontSize: 'var(--text-xl)', fontWeight: 800, color: 'var(--color-text-primary)', marginBottom: '4px' }}>
                            ₹{c.latest_price?.toLocaleString('en-IN')}/q
                          </div>
                          <div style={{ fontSize: '12px', color: 'var(--color-text-secondary)', display: 'flex', alignItems: 'center', gap: '4px' }}>
                            <FiMapPin size={12} /> {c.latest_market || 'APMC Yard'}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="empty-state">{t('market.noData', { defaultValue: 'No market records available for selected location.' })}</div>
                )}
              </div>
            </div>
          )}

          {/* TAB 2: MARKET COMPARISON */}
          {activeTab === 'compare' && (
            <div className="card">
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: 'var(--space-3)', marginBottom: 'var(--space-4)' }}>
                <div>
                  <h3 className="card-title" style={{ margin: 0 }}>
                    ⚖️ {t('market.compare.title', { defaultValue: 'Regional Mandi Price Comparison' })}
                  </h3>
                  <p style={{ fontSize: '12px', color: 'var(--color-text-secondary)', margin: '2px 0 0' }}>
                    Compare prevailing rates across nearby district mandis
                  </p>
                </div>

                <div style={{ display: 'flex', gap: 'var(--space-2)', alignItems: 'center' }}>
                  <label style={{ fontSize: '12px', fontWeight: 600 }}>{t('market.crop', { defaultValue: 'Crop:' })}</label>
                  <select
                    className="param-select"
                    value={compareCrop}
                    onChange={(e) => setCompareCrop(e.target.value)}
                    style={{ padding: '6px 12px', borderRadius: 'var(--radius-md)', border: '1px solid var(--color-border)', background: 'var(--color-surface)', fontSize: '13px' }}
                  >
                    {POPULAR.map((p) => (
                      <option key={p.name} value={p.name}>{t(`crops.${p.key}`, { defaultValue: p.name })}</option>
                    ))}
                  </select>
                </div>
              </div>

              {/* Decision Summary Hero Box */}
              {compareData?.decision_summary && (
                <div style={{
                  background: 'linear-gradient(135deg, rgba(31, 122, 69, 0.08), rgba(95, 175, 69, 0.12))',
                  border: '1px solid rgba(31, 122, 69, 0.25)',
                  borderRadius: 'var(--radius-lg)',
                  padding: 'var(--space-4)',
                  marginBottom: 'var(--space-4)'
                }}>
                  <div style={{ display: 'flex', alignItems: 'flex-start', gap: 'var(--space-3)' }}>
                    <FiInfo size={20} style={{ color: 'var(--brand-primary)', marginTop: '2px', flexShrink: 0 }} />
                    <div>
                      <div style={{ fontSize: '11px', fontWeight: 800, textTransform: 'uppercase', color: 'var(--brand-primary)', marginBottom: '2px' }}>
                        {t('market.compare.decision_summary', { defaultValue: 'Decision Support Summary' })}
                      </div>
                      <p style={{ margin: 0, fontSize: '13px', color: 'var(--color-text-primary)', lineHeight: 1.5 }}>
                        {compareData.decision_summary}
                      </p>
                    </div>
                  </div>
                </div>
              )}

              {/* Mandi Table / Grid */}
              {compareLoading ? (
                <div className="loading-state">{t('common.loading', { defaultValue: 'Comparing regional mandi prices...' })}</div>
              ) : compareData?.markets && compareData.markets.length > 0 ? (
                <div style={{ overflowX: 'auto', marginBottom: 'var(--space-4)' }}>
                  <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '13px' }}>
                    <thead>
                      <tr style={{ background: 'var(--color-background-secondary)', borderBottom: '2px solid var(--color-border)' }}>
                        <th style={{ padding: '10px 14px', textAlign: 'left' }}>{t('market.market', { defaultValue: 'Mandi / Yard' })}</th>
                        <th style={{ padding: '10px 14px', textAlign: 'right' }}>{t('market.price', { defaultValue: 'Prevailing Price' })}</th>
                        <th style={{ padding: '10px 14px', textAlign: 'center' }}>{t('market.trend', { defaultValue: 'Trend' })}</th>
                        <th style={{ padding: '10px 14px', textAlign: 'right' }}>{t('storage.distance', { defaultValue: 'Distance' })}</th>
                      </tr>
                    </thead>
                    <tbody>
                      {compareData.markets.map((m, idx) => (
                        <tr key={idx} style={{ borderBottom: '1px solid var(--color-border)', background: idx === 0 ? 'rgba(31, 122, 69, 0.04)' : 'transparent' }}>
                          <td style={{ padding: '12px 14px', fontWeight: idx === 0 ? 800 : 600, color: idx === 0 ? 'var(--brand-primary)' : 'inherit' }}>
                            {idx === 0 && '🏆 '} {m.market}
                          </td>
                          <td style={{ padding: '12px 14px', textAlign: 'right', fontWeight: 800, color: 'var(--color-text-primary)' }}>
                            ₹{m.price.toLocaleString('en-IN')}/q
                          </td>
                          <td style={{ padding: '12px 14px', textAlign: 'center' }}>
                            <span style={{ 
                              fontSize: '11px', 
                              fontWeight: 700, 
                              padding: '2px 8px', 
                              borderRadius: '10px',
                              background: m.trend === 'UP' ? 'rgba(31, 122, 69, 0.12)' : m.trend === 'DOWN' ? 'rgba(220, 38, 38, 0.12)' : 'rgba(107, 114, 128, 0.12)',
                              color: m.trend === 'UP' ? 'var(--brand-primary)' : m.trend === 'DOWN' ? '#DC2626' : '#4B5563'
                            }}>
                              {m.trend === 'UP' ? '↑ ' + t('trend.up', { defaultValue: 'UP' }) : m.trend === 'DOWN' ? '↓ ' + t('trend.down', { defaultValue: 'DOWN' }) : '→ ' + t('trend.stable', { defaultValue: 'STABLE' })}
                            </span>
                          </td>
                          <td style={{ padding: '12px 14px', textAlign: 'right', color: 'var(--color-text-secondary)' }}>
                            {m.distance} km
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              ) : (
                <div className="empty-state">{t('market.noData', { defaultValue: 'No comparison records available.' })}</div>
              )}

              {/* Disclaimer */}
              <div style={{ fontSize: '11px', color: 'var(--color-text-tertiary)', fontStyle: 'italic', marginBottom: 'var(--space-4)' }}>
                ⚠️ {t('market.compare.disclaimer', { defaultValue: 'Prices are for reference. Actual prices may vary at sale.' })}
              </div>

              {/* AI Advisory Context Box */}
              <div style={{ borderTop: '1px dashed var(--color-border)', paddingTop: 'var(--space-4)' }}>
                <button
                  type="button"
                  className="btn btn-secondary"
                  onClick={handleAskMarketAdvisory}
                  disabled={aiLoading}
                  style={{ width: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px', padding: '10px' }}
                >
                  <FiZap size={16} />
                  <span>{aiLoading ? 'Connecting to AgriDarshak AI...' : t('market.askAiBtn', { defaultValue: 'Ask AgriDarshak about market prices & selling timing' })}</span>
                </button>
                {aiAdvisory && (
                  <div style={{ marginTop: 'var(--space-4)' }}>
                    <AdvisoryMarkdown content={aiAdvisory} language={user?.language || 'en'} source="ai" />
                  </div>
                )}
              </div>

            </div>
          )}

        </div>
      </div>
    </AppLayout>
  )
}
