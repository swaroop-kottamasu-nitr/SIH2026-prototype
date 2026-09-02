import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import axios from 'axios'
import { motion } from 'framer-motion'
import AppLayout from '../components/AppLayout'
import AdvisoryMarkdown from '../components/AdvisoryMarkdown'
import { getEffectiveLanguage } from '../i18n'
import { 
  FiMapPin, FiPhone, FiCheckCircle, FiAlertCircle, 
  FiSearch, FiZap, FiShoppingBag, FiShield, FiTag 
} from 'react-icons/fi'
import './InputLocator.css'

const CATEGORIES = [
  { key: 'all', labelKey: 'input.category.all', defaultLabel: 'All Categories' },
  { key: 'seeds', labelKey: 'input.category.seeds', defaultLabel: 'Certified Seeds' },
  { key: 'fertilizers', labelKey: 'input.category.fertilizers', defaultLabel: 'Fertilizers & Nutrients' },
  { key: 'pesticides', labelKey: 'input.category.pesticides', defaultLabel: 'Bio-Pesticides & Crop Protection' },
  { key: 'equipment', labelKey: 'input.category.equipment', defaultLabel: 'Machinery & Micro-Irrigation' },
  { key: 'other', labelKey: 'input.category.other', defaultLabel: 'Nursery & Soil Test Units' }
]

export default function InputLocator({ user, onLogout, onUserUpdate }) {
  const { t, i18n } = useTranslation()
  const [category, setCategory] = useState('all')
  const [location, setLocation] = useState(user?.location || 'Vijayawada, Andhra Pradesh')
  const [results, setResults] = useState([])
  const [dataSource, setDataSource] = useState('demo')
  const [loading, setLoading] = useState(false)

  // Minimal AI Advisory Integration
  const [aiLoading, setAiLoading] = useState(false)
  const [aiAdvisory, setAiAdvisory] = useState(null)

  const searchDealers = async (cat, loc) => {
    setLoading(true)
    try {
      const res = await axios.post('/api/v1/inputs/search', {
        category: cat || category,
        location: loc || location,
        language: getEffectiveLanguage(user)
      })
      if (res.data) {
        setResults(res.data.results || [])
        setDataSource(res.data.data_source || 'demo')
      }
    } catch (err) {
      console.error('Input search error:', err)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    searchDealers('all', location)
  }, [location, i18n.language, user?.language])

  const handleAskInputAdvisory = async () => {
    if (aiLoading) return
    setAiLoading(true)
    try {
      const catLabel = CATEGORIES.find(c => c.key === category)?.defaultLabel || 'inputs'
      const prompt = `Where to procure certified quality ${catLabel} in ${location}? What specifications to look for?`
      const res = await axios.post('/api/v1/advisory', {
        question: prompt,
        language: getEffectiveLanguage(user),
        context: {
          category,
          location
        }
      }, { timeout: 15000 })
      if (res.data?.advisory) {
        setAiAdvisory(res.data.advisory)
      }
    } catch (err) {
      console.error('Input advisory error:', err)
    } finally {
      setAiLoading(false)
    }
  }

  return (
    <AppLayout user={user} onLogout={onLogout} onUserUpdate={onUserUpdate}>
      <div className="input-locator-page">
        <div className="container">
          
          {/* Header */}
          <div className="input-header">
            <div className="input-title-box">
              <div className="input-icon-badge">
                <FiShoppingBag size={26} />
              </div>
              <div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', flexWrap: 'wrap' }}>
                  <h1 className="input-title">{t('input.title', { defaultValue: 'Agricultural Input Locator' })}</h1>
                  <span className="demo-badge">
                    📋 {t('input.demo_badge', { defaultValue: 'DEMO DIRECTORY' })}
                  </span>
                </div>
                <p className="input-subtitle">
                  {t('input.subtitle', { defaultValue: 'Locate certified seed hubs, cooperative fertilizer outlets, and micro-irrigation dealers' })}
                </p>
              </div>
            </div>
          </div>

          {/* Search & Filter Bar */}
          <div className="input-search-card">
            <div className="search-grid">
              <div className="form-group" style={{ margin: 0 }}>
                <label className="form-label">{t('input.category', { defaultValue: 'Input Category' })}</label>
                <select
                  className="form-select"
                  value={category}
                  onChange={(e) => { setCategory(e.target.value); searchDealers(e.target.value, location); }}
                >
                  {CATEGORIES.map(c => (
                    <option key={c.key} value={c.key}>{t(c.labelKey, { defaultValue: c.defaultLabel })}</option>
                  ))}
                </select>
              </div>

              <div className="form-group" style={{ margin: 0 }}>
                <label className="form-label">{t('input.location', { defaultValue: 'Location / District' })}</label>
                <input
                  type="text"
                  className="form-input"
                  value={location}
                  onChange={(e) => setLocation(e.target.value)}
                  placeholder="e.g. Vijayawada, Guntur"
                  onKeyDown={(e) => { if (e.key === 'Enter') searchDealers(category, location); }}
                />
              </div>

              <div style={{ display: 'flex', alignItems: 'flex-end' }}>
                <button
                  type="button"
                  className="btn btn-primary search-btn"
                  onClick={() => searchDealers(category, location)}
                  disabled={loading}
                >
                  <FiSearch size={16} />
                  <span>{loading ? t('common.loading', { defaultValue: 'Searching...' }) : t('input.search', { defaultValue: 'Search Suppliers' })}</span>
                </button>
              </div>
            </div>
          </div>

          {/* Results Grid */}
          <div className="results-container">
            <div className="results-header-bar">
              <span className="results-count">
                {results.length} {t('input.dealersFound', { defaultValue: 'verified & registered agricultural supplier listings' })}
              </span>
              <span className="source-tag">
                📍 {location}
              </span>
            </div>

            {loading ? (
              <div className="loading-state">{t('common.loading', { defaultValue: 'Searching suppliers...' })}</div>
            ) : results.length > 0 ? (
              <div className="dealers-grid">
                {results.map((d, idx) => (
                  <motion.div
                    key={idx}
                    className="dealer-card"
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: idx * 0.04 }}
                  >
                    <div className="dealer-header">
                      <div className="dealer-name-box">
                        <span className="dealer-name">{d.name}</span>
                        <div className="category-pill-row">
                          <span className={`cat-pill cat-${d.category}`}>
                            {d.category}
                          </span>
                          {d.data_verified ? (
                            <span className="verified-pill">
                              <FiCheckCircle size={12} /> {t('input.verified_badge', { defaultValue: 'Govt / PACS Verified' })}
                            </span>
                          ) : (
                            <span className="unverified-pill">
                              <FiAlertCircle size={12} /> {t('input.sampleListing', { defaultValue: 'Registered Dealer' })}
                            </span>
                          )}
                        </div>
                      </div>
                      {d.distance && (
                        <div className="distance-badge">
                          {d.distance} km
                        </div>
                      )}
                    </div>

                    <div className="dealer-body">
                      <div className="dealer-info-row">
                        <FiMapPin size={16} className="info-icon" />
                        <span className="info-text">{d.address}</span>
                      </div>
                      {d.contact && (
                        <div className="dealer-info-row">
                          <FiPhone size={16} className="info-icon" />
                          <a href={`tel:${d.contact.replace(/\s+/g, '')}`} className="phone-link">
                            {d.contact}
                          </a>
                        </div>
                      )}
                    </div>
                  </motion.div>
                ))}
              </div>
            ) : (
              <div className="empty-state">
                <FiShoppingBag size={48} className="empty-icon" />
                <p>{t('input.noResults', { defaultValue: 'No supplier records match the selected category in this district.' })}</p>
              </div>
            )}
          </div>

          {/* AI Advisory Context Consultation */}
          <div className="ai-context-box-card">
            <button
              type="button"
              className="btn btn-secondary ai-ask-btn"
              onClick={handleAskInputAdvisory}
              disabled={aiLoading}
            >
              <FiZap size={16} />
              <span>{aiLoading ? 'Connecting to AgriDarshak AI...' : t('input.askAiBtn', { defaultValue: 'Ask AgriDarshak about input quality, dosages & certified brands' })}</span>
            </button>
            {aiAdvisory && (
              <div className="ai-advisory-panel">
                <AdvisoryMarkdown content={aiAdvisory} language={user?.language || 'en'} source="ai" />
              </div>
            )}
          </div>

        </div>
      </div>
    </AppLayout>
  )
}
