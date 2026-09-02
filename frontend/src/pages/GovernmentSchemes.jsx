import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import axios from 'axios'
import { motion, AnimatePresence } from 'framer-motion'
import AppLayout from '../components/AppLayout'
import AdvisoryMarkdown from '../components/AdvisoryMarkdown'
import { getEffectiveLanguage } from '../i18n'
import { 
  FiAward, FiCheckCircle, FiChevronDown, FiChevronUp, FiExternalLink, 
  FiAlertTriangle, FiZap, FiHelpCircle, FiFileText, FiDollarSign, FiShield 
} from 'react-icons/fi'
import './GovernmentSchemes.css'

const CATEGORIES = [
  { key: 'all', labelKey: 'scheme.category_all', defaultLabel: 'All Schemes' },
  { key: 'subsidy', labelKey: 'scheme.category.subsidy', defaultLabel: 'Direct Subsidies' },
  { key: 'insurance', labelKey: 'scheme.category.insurance', defaultLabel: 'Crop Insurance' },
  { key: 'loan', labelKey: 'scheme.category.loan', defaultLabel: 'Credit & Loans (KCC)' },
  { key: 'training', labelKey: 'scheme.category.training', defaultLabel: 'Soil & Organic Training' },
  { key: 'other', labelKey: 'scheme.category.other', defaultLabel: 'Market Linkage' }
]

export default function GovernmentSchemes({ user, onLogout, onUserUpdate }) {
  const { t, i18n } = useTranslation()
  const [category, setCategory] = useState('all')
  const [schemes, setSchemes] = useState([])
  const [loading, setLoading] = useState(false)
  const [expandedScheme, setExpandedScheme] = useState(null)

  // Eligibility Quiz states
  const [quizCrop, setQuizCrop] = useState('Chilli')
  const [quizFarmSize, setQuizFarmSize] = useState(2.5)
  const [quizLocation, setQuizLocation] = useState(user?.location || 'Vijayawada, Andhra Pradesh')
  const [eligibleMatches, setEligibleMatches] = useState(null)
  const [quizLoading, setQuizLoading] = useState(false)

  // Minimal AI Advisory Integration
  const [aiLoading, setAiLoading] = useState(false)
  const [aiAdvisory, setAiAdvisory] = useState(null)

  const fetchSchemes = async (cat) => {
    setLoading(true)
    try {
      const res = await axios.get('/api/v1/schemes', {
        params: { 
          category: cat === 'all' ? undefined : cat,
          language: getEffectiveLanguage(user)
        }
      })
      if (res.data?.schemes) {
        setSchemes(res.data.schemes)
      }
    } catch (err) {
      console.error('Fetch schemes error:', err)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchSchemes('all')
  }, [i18n.language, user?.language])

  const handleRunQuiz = async (e) => {
    e.preventDefault()
    setQuizLoading(true)
    try {
      const res = await axios.get('/api/v1/schemes/eligibility', {
        params: {
          crop: quizCrop,
          location: quizLocation,
          farm_size: parseFloat(quizFarmSize) || 2.5,
          language: getEffectiveLanguage(user)
        }
      })
      if (res.data?.eligible_schemes) {
        setEligibleMatches(res.data.eligible_schemes)
      }
    } catch (err) {
      console.error('Quiz error:', err)
    } finally {
      setQuizLoading(false)
    }
  }

  const toggleExpand = (id) => {
    setExpandedScheme(expandedScheme === id ? null : id)
  }

  const handleAskSchemesAdvisory = async () => {
    if (aiLoading) return
    setAiLoading(true)
    try {
      const prompt = `What central and state government agricultural schemes and subsidy benefits are applicable for ${quizCrop} farmers with ${quizFarmSize} acres in ${quizLocation}?`
      const res = await axios.post('/api/v1/advisory', {
        question: prompt,
        language: getEffectiveLanguage(user),
        context: {
          crop: quizCrop,
          farm_size: quizFarmSize,
          location: quizLocation
        }
      }, { timeout: 15000 })
      if (res.data?.advisory) {
        setAiAdvisory(res.data.advisory)
      }
    } catch (err) {
      console.error('Schemes advisory error:', err)
    } finally {
      setAiLoading(false)
    }
  }

  return (
    <AppLayout user={user} onLogout={onLogout} onUserUpdate={onUserUpdate}>
      <div className="schemes-page">
        <div className="container">
          
          {/* Warning Banner */}
          <div className="demo-disclaimer-banner">
            <FiAlertTriangle size={18} className="banner-icon" />
            <span>{t('scheme.demo_disclaimer', { defaultValue: 'This is demonstration data for SIH 2026. Verify all scheme details with official government sources.' })}</span>
          </div>

          {/* Header */}
          <div className="schemes-header">
            <div className="schemes-title-box">
              <div className="schemes-icon-badge">
                <FiAward size={26} />
              </div>
              <div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', flexWrap: 'wrap' }}>
                  <h1 className="schemes-title">{t('scheme.title', { defaultValue: 'Government Welfare Schemes' })}</h1>
                  <span className="demo-badge">
                    📋 {t('scheme.demo_badge', { defaultValue: 'DEMO DIRECTORY' })}
                  </span>
                </div>
                <p className="schemes-subtitle">
                  {t('scheme.subtitle', { defaultValue: 'Explore financial subsidies, crop insurance coverage, low-interest KCC loans, and organic soil missions' })}
                </p>
              </div>
            </div>
          </div>

          {/* Interactive Eligibility Quiz Card */}
          <div className="quiz-card">
            <h3 className="quiz-card-title">
              🎯 {t('scheme.eligibility_quiz', { defaultValue: 'Instant Farm Scheme Eligibility Estimator' })}
            </h3>
            <form onSubmit={handleRunQuiz} className="quiz-form-grid">
              <div className="form-group" style={{ margin: 0 }}>
                <label className="form-label">{t('crop_rotation.prevCrop', { defaultValue: 'Cultivated Crop' })}</label>
                <input
                  type="text"
                  className="form-input"
                  value={quizCrop}
                  onChange={(e) => setQuizCrop(e.target.value)}
                  placeholder="e.g. Chilli, Rice, Cotton"
                />
              </div>

              <div className="form-group" style={{ margin: 0 }}>
                <label className="form-label">{t('scheme.farmSizeLabel', { defaultValue: 'Total Farm Land (Acres)' })}</label>
                <input
                  type="number"
                  step="0.5"
                  className="form-input"
                  value={quizFarmSize}
                  onChange={(e) => setQuizFarmSize(e.target.value)}
                  placeholder="2.5"
                />
              </div>

              <div className="form-group" style={{ margin: 0 }}>
                <label className="form-label">{t('storage.location', { defaultValue: 'State / District' })}</label>
                <input
                  type="text"
                  className="form-input"
                  value={quizLocation}
                  onChange={(e) => setQuizLocation(e.target.value)}
                />
              </div>

              <div style={{ display: 'flex', alignItems: 'flex-end' }}>
                <button
                  type="submit"
                  className="btn btn-primary quiz-submit-btn"
                  disabled={quizLoading}
                >
                  {quizLoading ? t('common.loading', { defaultValue: 'Estimating...' }) : t('scheme.checkEligibilityBtn', { defaultValue: 'Evaluate Matches' })}
                </button>
              </div>
            </form>

            {/* Quiz Matches Output */}
            {eligibleMatches && (
              <div className="quiz-matches-box">
                <div className="matches-header">
                  <FiCheckCircle size={16} className="match-icon" />
                  <span className="matches-title">{t('scheme.eligible_schemes', { defaultValue: 'Estimated Eligible Programs' })}:</span>
                </div>
                <div className="matches-list">
                  {eligibleMatches.map((m, i) => (
                    <div key={i} className="match-item">
                      <div className="match-top">
                        <span className="match-scheme-id">{m.scheme_id.replace('SCH_', '')}</span>
                        <span className={`match-conf conf-${m.confidence.toLowerCase()}`}>
                          {m.confidence} {t('scheme.confidence', { defaultValue: 'Confidence' })}
                        </span>
                      </div>
                      <p className="match-reason-text">{m.match_reason}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Category Filter Pills */}
          <div className="schemes-filter-row">
            {CATEGORIES.map(c => (
              <button
                key={c.key}
                type="button"
                className={`category-filter-btn ${category === c.key ? 'active' : ''}`}
                onClick={() => { setCategory(c.key); fetchSchemes(c.key); }}
              >
                {t(c.labelKey, { defaultValue: c.defaultLabel })}
              </button>
            ))}
          </div>

          {/* Schemes Directory List */}
          <div className="schemes-list">
            {loading ? (
              <div className="loading-state">{t('common.loading', { defaultValue: 'Loading schemes...' })}</div>
            ) : schemes.length > 0 ? (
              schemes.map((s, idx) => {
                const isExpanded = expandedScheme === s.id
                return (
                  <motion.div
                    key={s.id}
                    className="scheme-card"
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: idx * 0.04 }}
                  >
                    <div className="scheme-card-summary" onClick={() => toggleExpand(s.id)}>
                      <div className="scheme-header-info">
                        <div className="scheme-title-row">
                          <span className="scheme-name">{s.name}</span>
                          <span className={`category-tag cat-${s.category}`}>
                            {t(`scheme.category.${s.category}`, { defaultValue: s.category })}
                          </span>
                        </div>
                        <p className="scheme-desc">{s.description}</p>
                      </div>
                      <button type="button" className="expand-toggle-btn" aria-label="Toggle details">
                        {isExpanded ? <FiChevronUp size={20} /> : <FiChevronDown size={20} />}
                      </button>
                    </div>

                    <AnimatePresence>
                      {isExpanded && (
                        <motion.div
                          className="scheme-expanded-details"
                          initial={{ opacity: 0, height: 0 }}
                          animate={{ opacity: 1, height: 'auto' }}
                          exit={{ opacity: 0, height: 0 }}
                          transition={{ duration: 0.2 }}
                        >
                          <div className="detail-block">
                            <span className="detail-label">📋 {t('scheme.eligibility', { defaultValue: 'Eligibility Criteria' })}</span>
                            <p className="detail-val-text">{s.eligibility}</p>
                          </div>

                          <div className="detail-block">
                            <span className="detail-label">💰 {t('scheme.benefits', { defaultValue: 'Benefits & Assistance' })}</span>
                            <p className="detail-val-text">{s.benefits}</p>
                          </div>

                          <div className="detail-footer-row">
                            {s.deadline && (
                              <div className="deadline-badge">
                                📅 {t('scheme.deadline', { defaultValue: 'Deadline' })}: {s.deadline}
                              </div>
                            )}
                            {s.application_link && (
                              <a
                                href={s.application_link}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="official-portal-link"
                              >
                                <span>{t('scheme.apply_now', { defaultValue: 'Visit Official Portal' })}</span>
                                <FiExternalLink size={13} />
                              </a>
                            )}
                          </div>
                        </motion.div>
                      )}
                    </AnimatePresence>
                  </motion.div>
                )
              })
            ) : (
              <div className="empty-state">
                <FiAward size={48} className="empty-icon" />
                <p>{t('scheme.noSchemes', { defaultValue: 'No schemes found in this category.' })}</p>
              </div>
            )}
          </div>

          {/* AI Advisory Context Consultation */}
          <div className="ai-context-box-card">
            <button
              type="button"
              className="btn btn-secondary ai-ask-btn"
              onClick={handleAskSchemesAdvisory}
              disabled={aiLoading}
            >
              <FiZap size={16} />
              <span>{aiLoading ? 'Connecting to AgriDarshak AI...' : t('scheme.askAiBtn', { defaultValue: 'Ask AgriDarshak about government scheme application procedures' })}</span>
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
