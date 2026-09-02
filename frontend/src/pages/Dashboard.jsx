import { Link } from 'react-router-dom'
import { useState, useEffect } from 'react'
import { useTranslation } from 'react-i18next'
import axios from 'axios'
import { motion } from 'framer-motion'
import AppLayout from '../components/AppLayout'
import AdvisoryMarkdown from '../components/AdvisoryMarkdown'
import TextToSpeech from '../components/TextToSpeech'
import { 
  FiDroplet, FiCloudRain, FiActivity, FiMapPin, FiTrendingUp, 
  FiShield, FiCheckCircle, FiChevronRight, FiUser, FiSend, FiZap, FiInfo, FiArrowRight
} from 'react-icons/fi'
import i18n, { getStoredLanguage } from '../i18n'
import './Dashboard.css'

function Dashboard({ user, onLogout, onUserUpdate }) {
  const { t } = useTranslation()

  const [alerts, setAlerts] = useState([])
  const [farmHealth, setFarmHealth] = useState(null)
  const [weatherSnapshot, setWeatherSnapshot] = useState(null)
  const [marketSnapshot, setMarketSnapshot] = useState(null)
  const [loading, setLoading] = useState(true)
  const [expandedBreakdown, setExpandedBreakdown] = useState(false)
  const [selectedChainIndex, setSelectedChainIndex] = useState(0)

  // Section 10: Interactive AI Advisory State
  const [advisoryContent, setAdvisoryContent] = useState(null)
  const [advisorySource, setAdvisorySource] = useState('ai')
  const [advisoryLoading, setAdvisoryLoading] = useState(false)
  const [advisoryQuery, setAdvisoryQuery] = useState('')

  const PILLAR_CONFIG = [
    { id: 'weather', icon: '🌧', key: 'weather', titleKey: 'distressIndex.pillars.weather', max: 25, fallbackName: 'Weather Risk' },
    { id: 'disease', icon: '🦠', key: 'disease', titleKey: 'distressIndex.pillars.disease', max: 20, fallbackName: 'Disease Risk' },
    { id: 'market', icon: '📉', key: 'market', titleKey: 'distressIndex.pillars.market', max: 20, fallbackName: 'Market Risk' },
    { id: 'crop', icon: '🌾', key: 'crop', titleKey: 'distressIndex.pillars.crop', max: 20, fallbackName: 'Crop/Yield Risk' },
    { id: 'soil', icon: '🌱', key: 'soil', titleKey: 'distressIndex.pillars.soil', max: 10, fallbackName: 'Soil Health Risk' },
    { id: 'context', icon: '🔔', key: 'context', titleKey: 'distressIndex.pillars.context', max: 5, fallbackName: 'Context Alerts Risk' }
  ]

  const activeCropName = (user?.preferred_crops && user.preferred_crops.length > 0)
    ? user.preferred_crops[0]
    : 'Chilli'

  const effectiveLang = i18n.language || user?.language || (typeof window !== 'undefined' ? getStoredLanguage() || 'en' : 'en')

  useEffect(() => {
    const loadDashboardData = async () => {
      const loc = user?.location || 'Vijayawada, Andhra Pradesh'
      const encodedLoc = encodeURIComponent(loc)

      try {
        const userId = user?.id || 1
        const [healthRes, alertsRes, weatherRes, marketRes] = await Promise.allSettled([
          axios.get(`/api/farm-health/risk?user_id=${userId}&location=${encodedLoc}`, {
            headers: { 'X-User-ID': String(userId) }
          }),
          axios.get(`/api/weather/alerts/user/${userId}?unread_only=true&limit=3`),
          axios.post('/api/weather/current', { location: loc }),
          axios.post('/api/market/season-prices', { location: loc })
        ])

        if (healthRes.status === 'fulfilled') {
          setFarmHealth(healthRes.value.data)
        } else {
          // Graceful fallback
          setFarmHealth({
            score: 34,
            risk_level: 'MODERATE',
            factors: [
              { name: 'Weather Risk', score: 3, max_score: 25, level: 'LOW', reason: 'Favorable weather conditions with normal temperature and rainfall' },
              { name: 'Disease Risk', score: 2, max_score: 20, level: 'LOW', reason: 'No active plant disease detected on standing crops' },
              { name: 'Market Risk', score: 17, max_score: 20, level: 'CRITICAL', reason: 'Softening mandi prices for Chilli and Cotton in local APMC yard' },
              { name: 'Crop/Yield Risk', score: 9, max_score: 20, level: 'MODERATE', reason: 'Standing crop is in pre-harvest phase - prepare field collection' },
              { name: 'Soil Risk', score: 2, max_score: 10, level: 'LOW', reason: 'Well-balanced soil nutrients with optimal pH' },
              { name: 'Context Risk', score: 1, max_score: 5, level: 'LOW', reason: 'Alert notifications resolved; farm profile up to date' }
            ],
            recommendations: [
              'Consider staggered harvest selling or explore nearby district APMC mandis for higher rates.',
              'Maintain regular crop scouting and scheduled irrigation.',
              'Track local weather alerts and daily mandi prices on the dashboard.'
            ]
          })
        }

        if (alertsRes.status === 'fulfilled') {
          const data = alertsRes.value.data
          setAlerts(Array.isArray(data) ? data : (data?.alerts || []))
        }

        if (weatherRes.status === 'fulfilled') {
          setWeatherSnapshot(weatherRes.value.data)
        }

        if (marketRes.status === 'fulfilled') {
          setMarketSnapshot(marketRes.value.data)
        }

      } catch {
        // Graceful error state handling
      } finally {
        setLoading(false)
      }
    }

    loadDashboardData()
  }, [user?.id, user?.location])

  const handleAskAdvisory = async (queryText) => {
    if (advisoryLoading) return

    const defaultPrompt = 'Organic pest control measures for current season'
    const textToAsk = (typeof queryText === 'string' && queryText.trim())
      ? queryText.trim()
      : (advisoryQuery && advisoryQuery.trim())
        ? advisoryQuery.trim()
        : (t('dashboardAdvisory.promptPest') || defaultPrompt)

    if (!advisoryQuery && textToAsk) {
      setAdvisoryQuery(textToAsk)
    }

    setAdvisoryLoading(true)
    try {
      const loc = user?.location || 'Vijayawada, Andhra Pradesh'
      const lang = effectiveLang || 'en'
      const crop = activeCropName || 'Chilli'
      const currentScore = farmHealth?.score ?? 35
      const tempVal = weatherSnapshot?.main?.temp ? Math.round(weatherSnapshot.main.temp) : 28
      
      const payload = {
        question: textToAsk,
        query: textToAsk,
        language: lang,
        context: {
          crop: crop,
          location: loc,
          season: 'Kharif',
          temperature: tempVal,
          weather_data: weatherSnapshot ? {
            temp: weatherSnapshot?.main?.temp,
            humidity: weatherSnapshot?.main?.humidity,
            wind_speed: weatherSnapshot?.wind?.speed,
            description: weatherSnapshot?.weather?.[0]?.description
          } : null,
          distress_score: currentScore
        },
        location: loc,
        crop_name: crop,
        season: 'Kharif',
        temperature: tempVal,
        distress_score: currentScore,
        user_id: user?.id || 1
      }

      // 1. Primary API v1 Advisory endpoint with strict 15s timeout
      const res = await axios.post('/api/v1/advisory', payload, { timeout: 15000 })

      const advisoryText = res.data?.advisory || res.data?.explanation
      if (advisoryText) {
        setAdvisoryContent(advisoryText)
        const src = res.data?.source || res.data?.advisory_source || 'gemini'
        setAdvisorySource(src === 'gemini' || src === 'ai' ? 'ai' : 'fallback')
      }
    } catch (err) {
      // 2. Cascade fallback to farm-health advisory / crop rule engine
      try {
        const loc = user?.location || 'Vijayawada, Andhra Pradesh'
        const lang = effectiveLang || 'en'
        const crop = activeCropName || 'Chilli'
        const currentScore = farmHealth?.score ?? 35
        const tempVal = weatherSnapshot?.main?.temp ? Math.round(weatherSnapshot.main.temp) : 28

        const fallbackRes = await axios.post('/api/farm-health/advisory', {
          query: textToAsk,
          location: loc,
          crop_name: crop,
          season: 'Kharif',
          temperature: tempVal,
          distress_score: currentScore,
          user_id: user?.id || 1,
          language: lang
        }, { timeout: 8000 })

        const advisoryText = fallbackRes.data?.advisory || fallbackRes.data?.explanation
        if (advisoryText) {
          setAdvisoryContent(advisoryText)
          const src = fallbackRes.data?.source || fallbackRes.data?.advisory_source || 'fallback'
          setAdvisorySource(src === 'gemini' || src === 'ai' ? 'ai' : 'fallback')
        }
      } catch {
        // Handled gracefully - state remains valid
      }
    } finally {
      // Guaranteed loading indicator clearance
      setAdvisoryLoading(false)
    }
  }

  return (
    <AppLayout user={user} onLogout={onLogout} onUserUpdate={onUserUpdate}>
      <div className="dashboard">
        <div className="container">

          {/* ============================================================
              1. FARMER CONTEXT (Profile / Quick Stats Header)
              ============================================================ */}
          <motion.div
            className="farmer-profile-card"
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3 }}
          >
            <div className="farmer-profile-main">
              <div className="farmer-avatar-box">
                <FiUser size={28} />
              </div>
              <div className="farmer-info-col">
                <div className="farmer-title-row">
                  <div className="dashboard-brand-pill">
                    <img src="/agridarshak-logo.jpeg" alt="AgriDarshak" className="dashboard-brand-logo" />
                    <span>AgriDarshak</span>
                  </div>
                  <h1 className="farmer-name">{user?.name || t('dashboard.farmer')}</h1>
                  <span className="badge badge-verified">{t('dashboard.registeredFarmer')}</span>
                </div>
                <p className="farmer-location-meta">
                  <FiMapPin size={14} /> {user?.location || 'Vijayawada, Andhra Pradesh'} • {user?.farming_experience ? t('dashboard.yearsExp', { count: user.farming_experience }) : t('dashboard.experiencedFarmer')}
                </p>
              </div>
            </div>

            <div className="farm-specs-row">
              <div className="farm-spec-cell">
                <span className="spec-title">{t('dashboard.landArea')}</span>
                <span className="spec-value">{user?.farm_size ? t('dashboard.acres', { count: user.farm_size }) : t('dashboard.acres', { count: 4.5 })}</span>
              </div>
              <div className="farm-spec-cell">
                <span className="spec-title">{t('dashboard.soilStatus')}</span>
                <span className="spec-value status-good">{t('dashboard.balancedGood')}</span>
              </div>
              <div className="farm-spec-cell active-crop-cell">
                <span className="spec-title">{t('dashboard.activeStandingCrop')}</span>
                <span className="spec-value text-primary font-bold">🌱 {t(`crops.${activeCropName.toLowerCase().replace(/[^a-z]/g, '')}`, { defaultValue: activeCropName })}</span>
              </div>
            </div>
          </motion.div>

          {/* ACTIVE EMERGENCY WEATHER ALERTS (If any) */}
          {alerts.length > 0 && (
            <motion.section
              className="alerts-section"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.1 }}
            >
              <h2 className="section-heading">{t('dashboard.activeAlerts')}</h2>
              <div className="alerts-grid">
                {alerts.map((alert) => (
                  <Link
                    key={alert.id}
                    to={`/alert/${alert.id}`}
                    className={`alert-card severity-${alert.severity}`}
                  >
                    <span className="alert-badge">{alert.severity}</span>
                    <h3>{alert.title}</h3>
                    <p>{alert.description}</p>
                  </Link>
                ))}
              </div>
            </motion.section>
          )}

          {/* ============================================================
              2. FARMER DISTRESS INDEX (Flagship Hero Card & 6 Pillars)
              ============================================================ */}
          {farmHealth && (
            <motion.section
              className="farm-health-section"
              initial={{ opacity: 0, y: 14 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 }}
            >
              <div className={`farm-health-card flagship-distress-card risk-${farmHealth.risk_level.toLowerCase()}`}>
                
                {/* 2.1 HERO HEADER */}
                <div className="farm-health-header">
                  <div className="farm-health-title-group">
                    <div className="distress-badge-icon">
                      <span>🌾</span>
                    </div>
                    <div>
                      <div className="distress-title-row">
                        <h2 className="farm-health-title">{t('distressIndex.title')}</h2>
                        <span className="distress-platform-tag">AgriDarshak</span>
                      </div>
                      <p className="farm-health-desc">{t('distressIndex.subtitle')}</p>
                    </div>
                  </div>

                  <div className="farm-health-score-badge-group">
                    <div className="farm-health-score-val">
                      <span className="score-num">{farmHealth.score}</span>
                      <span className="score-max">{t('distressIndex.outOf100', { defaultValue: '/ 100' })}</span>
                    </div>
                    <div className="risk-badge-col">
                      <span className={`farm-risk-badge risk-${farmHealth.risk_level.toLowerCase()}`}>
                        {t(`farmHealth.levels.${farmHealth.risk_level.toLowerCase()}`, { defaultValue: farmHealth.risk_level })} {t('farmHealth.riskSuffix')}
                      </span>
                      <span className="risk-trend-indicator">
                        {farmHealth.score >= 50 ? t('farmHealth.riskIncreasing') : farmHealth.score >= 25 ? t('farmHealth.riskStable') : t('farmHealth.riskLowStable')}
                      </span>
                    </div>
                  </div>
                </div>

                {/* Visual Progress Meter */}
                <div className="farm-health-meter">
                  <div
                    className={`farm-health-fill risk-${farmHealth.risk_level.toLowerCase()}`}
                    style={{ width: `${Math.max(6, farmHealth.score)}%` }}
                  />
                </div>

                {/* 2.2 SIX AGRONOMIC RISK PILLARS */}
                <div className="distress-pillars-section">
                  <h3 className="pillars-section-title">{t('distressIndex.pillarsTitle')}</h3>
                  <div className="distress-pillars-grid">
                    {farmHealth.factors.map((factor, idx) => {
                      let pillarMeta = PILLAR_CONFIG.find(p => factor.name.toLowerCase().includes(p.key)) || PILLAR_CONFIG[idx] || {
                        icon: '⚡',
                        key: 'context',
                        titleKey: 'distressIndex.pillars.context',
                        max: factor.max_score || 20
                      }
                      const factorScore = factor.score ?? 0
                      const factorMax = factor.max_score || pillarMeta.max || 20
                      const percent = Math.min(100, Math.round((factorScore / factorMax) * 100))
                      const factorLevel = (factor.level || (percent >= 70 ? 'CRITICAL' : percent >= 45 ? 'HIGH' : percent >= 25 ? 'MODERATE' : 'LOW')).toLowerCase()

                      return (
                        <div key={idx} className={`pillar-card pillar-risk-${factorLevel}`}>
                          <div className="pillar-top">
                            <span className="pillar-icon">{pillarMeta.icon}</span>
                            <span className={`pillar-level-tag risk-${factorLevel}`}>
                              {t(`farmHealth.levels.${factorLevel}`, { defaultValue: factorLevel.toUpperCase() })}
                            </span>
                          </div>
                          <div className="pillar-name">{t(pillarMeta.titleKey, { defaultValue: factor.name })}</div>
                          <div className="pillar-score-row">
                            <span className="pillar-score">{factorScore}</span>
                            <span className="pillar-max">/ {factorMax}</span>
                          </div>
                          <div className="pillar-bar">
                            <div className={`pillar-fill risk-${factorLevel}`} style={{ width: `${Math.max(8, percent)}%` }} />
                          </div>
                        </div>
                      )
                    })}
                  </div>
                </div>

                {/* ============================================================
                    3. EARLY WARNING INTELLIGENCE LAYER
                    ============================================================ */}
                {(() => {
                  const sortedRiskFactors = [...(farmHealth.factors || [])].sort((a, b) => {
                    const ratioA = (a.score ?? 0) / (a.max_score || 20)
                    const ratioB = (b.score ?? 0) / (b.max_score || 20)
                    return ratioB - ratioA
                  })

                  const attentionFactorsCount = (farmHealth.factors || []).filter(f => {
                    const ratio = (f.score ?? 0) / (f.max_score || 20)
                    return ratio >= 0.25 || f.level === 'HIGH' || f.level === 'CRITICAL' || f.level === 'MODERATE'
                  }).length

                  const hasHistoricalData = Boolean(farmHealth.previous_score != null || farmHealth.history)
                  const previousScore = farmHealth.previous_score
                  const scoreChange = hasHistoricalData ? (farmHealth.score - previousScore) : null
                  const topRiskDrivers = sortedRiskFactors.slice(0, 3)

                  return (
                    <div className="early-warning-section">
                      <div className="early-warning-header">
                        <div className="early-warning-title-box">
                          <span className="early-warning-icon">⚠️</span>
                          <div>
                            <h3 className="early-warning-title">{t('earlyWarning.title')}</h3>
                            <p className="early-warning-desc">{t('earlyWarning.subtitle')}</p>
                          </div>
                        </div>

                        <div className="early-warning-status-pill">
                          {hasHistoricalData ? (
                            <span className={`ew-trend-tag ${scoreChange > 0 ? 'trend-up' : scoreChange < 0 ? 'trend-down' : 'trend-stable'}`}>
                              {t('earlyWarning.riskChange', { prev: previousScore, curr: farmHealth.score })} (
                              {scoreChange > 0 ? `+${scoreChange}` : scoreChange} {t('earlyWarning.trendPoints', { delta: '' }).trim()})
                            </span>
                          ) : (
                            <span className="ew-attention-counter">
                              <span className="counter-dot">●</span>
                              {t('earlyWarning.factorsNeedAttention', { count: attentionFactorsCount })}
                            </span>
                          )}
                        </div>
                      </div>

                      {/* Top 3 Risk Drivers Grid */}
                      <div className="early-warning-drivers-grid">
                        {topRiskDrivers.map((factor, idx) => {
                          let pillarMeta = PILLAR_CONFIG.find(p => factor.name.toLowerCase().includes(p.key)) || PILLAR_CONFIG[idx] || {
                            icon: '⚡',
                            key: 'context',
                            titleKey: 'distressIndex.pillars.context',
                            max: factor.max_score || 20
                          }
                          const factorScore = factor.score ?? 0
                          const factorMax = factor.max_score || pillarMeta.max || 20
                          const percent = Math.min(100, Math.round((factorScore / factorMax) * 100))
                          const factorLevel = (factor.level || (percent >= 70 ? 'CRITICAL' : percent >= 45 ? 'HIGH' : percent >= 25 ? 'MODERATE' : 'LOW')).toLowerCase()

                          const reasonText = factor.key
                            ? t(factor.key, factor.params || {}, { defaultValue: factor.reason })
                            : factor.reason

                          // Match corresponding recommendation or fallback
                          const matchingRec = (farmHealth.recommendation_objects || []).find(r => {
                            const k = (r.key || '').toLowerCase()
                            return k.includes(pillarMeta.key)
                          })
                          const recText = matchingRec
                            ? t(matchingRec.key, matchingRec.params || {}, { defaultValue: matchingRec.text || matchingRec.key })
                            : (farmHealth.recommendations && farmHealth.recommendations[idx])
                            ? (typeof farmHealth.recommendations[idx] === 'object' ? farmHealth.recommendations[idx].text : farmHealth.recommendations[idx])
                            : t(`distressIndex.whyMattersExplanations.${pillarMeta.key}`, { defaultValue: reasonText })

                          return (
                            <div key={idx} className={`ew-driver-card ew-risk-${factorLevel}`}>
                              <div className="ew-driver-top">
                                <div className="ew-driver-identity">
                                  <span className="ew-driver-icon">{pillarMeta.icon}</span>
                                  <div>
                                    <span className="ew-driver-rank">{t('earlyWarning.driverRank', { rank: idx + 1 })}</span>
                                    <h4 className="ew-driver-name">{t(pillarMeta.titleKey, { defaultValue: factor.name })}</h4>
                                  </div>
                                </div>
                                <div className="ew-driver-score-col">
                                  <span className={`ew-driver-badge risk-${factorLevel}`}>
                                    {t(`farmHealth.levels.${factorLevel}`, { defaultValue: factorLevel.toUpperCase() })}
                                  </span>
                                  <span className="ew-driver-ratio">{factorScore}/{factorMax}</span>
                                </div>
                              </div>

                              <div className="ew-driver-body">
                                <div className="ew-signal-box">
                                  <span className="ew-box-label">📡 {t('earlyWarning.driverExplanationLabel')}</span>
                                  <p className="ew-signal-text">{reasonText}</p>
                                </div>

                                <div className="ew-action-box">
                                  <span className="ew-box-label">🛡️ {t('earlyWarning.mitigationActionLabel')}</span>
                                  <p className="ew-action-text">{recText}</p>
                                </div>
                              </div>
                            </div>
                          )
                        })}
                      </div>
                    </div>
                  )
                })()}

                {/* ============================================================
                    4. PRIORITY ACTION PLAN (Enriched with URGENT/TODAY/THIS WEEK & WHY/BENEFIT)
                    ============================================================ */}
                <div className="distress-action-panel">
                  <div className="action-panel-header">
                    <div className="action-panel-icon">📋</div>
                    <div>
                      <h3 className="action-panel-title">{t('priorityActions.title')}</h3>
                      <p className="action-panel-desc">{t('priorityActions.subtitle')}</p>
                    </div>
                  </div>

                  <div className="action-cards-grid">
                    {(farmHealth.recommendation_objects || farmHealth.recommendations).slice(0, 3).map((rec, idx) => {
                      const recText = typeof rec === 'object' && rec?.key
                        ? t(rec.key, rec.params || {}, { defaultValue: rec.text || rec.key })
                        : typeof rec === 'string'
                        ? t(rec, { defaultValue: rec })
                        : String(rec)

                      const recKey = typeof rec === 'object' ? (rec.key || '').toLowerCase() : String(rec).toLowerCase()

                      // Find matching factor from backend data
                      const matchingFactor = (farmHealth.factors || []).find(f => {
                        const fName = f.name.toLowerCase()
                        if (recKey.includes('market') || recKey.includes('price') || recKey.includes('mandi') || recKey.includes('selling')) return fName.includes('market')
                        if (recKey.includes('disease') || recKey.includes('pest') || recKey.includes('leaf') || recKey.includes('scout')) return fName.includes('disease')
                        if (recKey.includes('weather') || recKey.includes('rain') || recKey.includes('alert')) return fName.includes('weather')
                        if (recKey.includes('crop') || recKey.includes('harvest') || recKey.includes('yield')) return fName.includes('crop')
                        if (recKey.includes('soil') || recKey.includes('fertilizer') || recKey.includes('nutrient') || recKey.includes('ph')) return fName.includes('soil')
                        return false
                      }) || farmHealth.factors[idx] || { level: 'LOW', reason: 'Maintain standard seasonal monitoring schedule' }

                      const factorLevel = (matchingFactor.level || 'LOW').toUpperCase()

                      // Determine Priority Label based on risk severity:
                      // CRITICAL or HIGH -> URGENT
                      // MODERATE -> TODAY
                      // LOW -> THIS WEEK
                      const isUrgent = factorLevel === 'CRITICAL' || factorLevel === 'HIGH'
                      const isToday = factorLevel === 'MODERATE'
                      const priorityTag = isUrgent 
                        ? { label: t('priorityActions.urgent'), cls: 'priority-urgent' }
                        : isToday 
                        ? { label: t('priorityActions.today'), cls: 'priority-today' }
                        : { label: t('priorityActions.thisWeek'), cls: 'priority-this-week' }

                      const factorReason = matchingFactor.key
                        ? t(matchingFactor.key, matchingFactor.params || {}, { defaultValue: matchingFactor.reason })
                        : matchingFactor.reason

                      // Domain-consistent expected benefit
                      let benefitKey = 'priorityActions.benefits.general'
                      if (recKey.includes('market') || matchingFactor.name?.toLowerCase().includes('market')) benefitKey = 'priorityActions.benefits.market'
                      else if (recKey.includes('disease') || matchingFactor.name?.toLowerCase().includes('disease')) benefitKey = 'priorityActions.benefits.disease'
                      else if (recKey.includes('weather') || matchingFactor.name?.toLowerCase().includes('weather')) benefitKey = 'priorityActions.benefits.weather'
                      else if (recKey.includes('crop') || matchingFactor.name?.toLowerCase().includes('crop')) benefitKey = 'priorityActions.benefits.crop'
                      else if (recKey.includes('soil') || matchingFactor.name?.toLowerCase().includes('soil')) benefitKey = 'priorityActions.benefits.soil'

                      const benefitText = t(benefitKey)

                      return (
                        <div key={idx} className={`priority-action-card ${priorityTag.cls}`}>
                          <div className="action-card-top">
                            <span className={`priority-badge ${priorityTag.cls}`}>
                              {priorityTag.label}
                            </span>
                            <span className="action-rank-tag">{t('distressIndex.priorityRank', { rank: idx + 1 })}</span>
                          </div>

                          <div className="priority-card-body">
                            <div className="action-detail-group">
                              <span className="action-section-label">⚡ {t('priorityActions.actionLabel')}</span>
                              <p className="priority-action-text">{recText}</p>
                            </div>

                            <div className="action-detail-group why-group">
                              <span className="action-section-label">❓ {t('priorityActions.whyLabel')}</span>
                              <p className="priority-why-text">{factorReason}</p>
                            </div>

                            <div className="action-detail-group benefit-group">
                              <span className="action-section-label">🎯 {t('priorityActions.benefitLabel')}</span>
                              <p className="priority-benefit-text">{benefitText}</p>
                            </div>
                          </div>
                        </div>
                      )
                    })}
                  </div>
                </div>

                {/* ============================================================
                    EXPLAINABLE DECISION CHAIN (SIGNAL -> RISK -> RECOMMENDATION)
                    ============================================================ */}
                {(() => {
                  const activeFactors = (farmHealth.factors || []).slice(0, 3)
                  const currentFactor = activeFactors[selectedChainIndex] || activeFactors[0]

                  if (!currentFactor) return null

                  let pillarMeta = PILLAR_CONFIG.find(p => currentFactor.name.toLowerCase().includes(p.key)) || {
                    icon: '⚡',
                    key: 'context',
                    titleKey: 'distressIndex.pillars.context',
                    max: 20
                  }

                  const factorLevel = (currentFactor.level || 'LOW').toLowerCase()
                  const factorReason = currentFactor.key
                    ? t(currentFactor.key, currentFactor.params || {}, { defaultValue: currentFactor.reason })
                    : currentFactor.reason

                  // Corresponding recommendation
                  const matchingRec = (farmHealth.recommendation_objects || []).find(r => {
                    const k = (r.key || '').toLowerCase()
                    return k.includes(pillarMeta.key)
                  })
                  const recText = matchingRec
                    ? t(matchingRec.key, matchingRec.params || {}, { defaultValue: matchingRec.text || matchingRec.key })
                    : (farmHealth.recommendations && farmHealth.recommendations[selectedChainIndex])
                    ? (typeof farmHealth.recommendations[selectedChainIndex] === 'object' ? farmHealth.recommendations[selectedChainIndex].text : farmHealth.recommendations[selectedChainIndex])
                    : t(`distressIndex.whyMattersExplanations.${pillarMeta.key}`, { defaultValue: factorReason })

                  // Dynamic live signal summary based on domain
                  let signalSummary = factorReason
                  if (pillarMeta.key === 'weather') {
                    signalSummary = weatherSnapshot?.main?.temp 
                      ? `${weatherSnapshot.main.temp}°C, ${weatherSnapshot.main.humidity}% Humidity, ${weatherSnapshot.weather?.[0]?.description || 'Clear'}`
                      : factorReason
                  } else if (pillarMeta.key === 'market') {
                    signalSummary = marketSnapshot?.crops 
                      ? `${marketSnapshot.crops.map(c => `${c.crop_name}: ₹${c.latest_price}/q`).join(' • ')}`
                      : factorReason
                  } else if (pillarMeta.key === 'disease') {
                    signalSummary = `Leaf humidity ${weatherSnapshot?.main?.humidity || '71'}% • Crop leaf monitoring status active`
                  }

                  return (
                    <div className="decision-chain-container">
                      <div className="decision-chain-header">
                        <div className="decision-chain-title-box">
                          <span className="chain-icon">🔗</span>
                          <div>
                            <h3 className="decision-chain-title">{t('decisionChain.title')}</h3>
                            <p className="decision-chain-desc">{t('decisionChain.subtitle')}</p>
                          </div>
                        </div>
                        <span className="chain-evidence-badge">✓ {t('decisionChain.evidenceBased')}</span>
                      </div>

                      {/* Chain Factor Selector Tabs */}
                      <div className="decision-chain-tabs">
                        {activeFactors.map((f, i) => {
                          const pMeta = PILLAR_CONFIG.find(p => f.name.toLowerCase().includes(p.key)) || { icon: '⚡', titleKey: 'distressIndex.pillars.context' }
                          return (
                            <button
                              key={i}
                              type="button"
                              className={`chain-tab-btn ${selectedChainIndex === i ? 'active' : ''}`}
                              onClick={() => setSelectedChainIndex(i)}
                            >
                              <span>{pMeta.icon}</span>
                              <span>{t(pMeta.titleKey, { defaultValue: f.name })}</span>
                            </button>
                          )
                        })}
                      </div>

                      {/* 3-Step Evidence Pipeline Visual Flow */}
                      <div className="decision-chain-flow">
                        {/* Step 1: SIGNAL */}
                        <div className="chain-step-node node-signal">
                          <div className="node-badge-header">
                            <span className="node-step-tag">STEP 1</span>
                            <span className="node-type-title">📡 {t('decisionChain.signal')}</span>
                          </div>
                          <span className="node-sublabel">{t('decisionChain.signalDesc')}</span>
                          <p className="node-content-text">{signalSummary}</p>
                        </div>

                        <div className="chain-connector-arrow" aria-hidden="true">
                          <FiArrowRight size={22} />
                        </div>

                        {/* Step 2: RISK */}
                        <div className={`chain-step-node node-risk risk-${factorLevel}`}>
                          <div className="node-badge-header">
                            <span className="node-step-tag">STEP 2</span>
                            <span className="node-type-title">⚠️ {t('decisionChain.risk')}</span>
                          </div>
                          <span className="node-sublabel">{t('decisionChain.riskDesc')}</span>
                          <div className="node-risk-highlight">
                            <strong>{t(pillarMeta.titleKey, { defaultValue: currentFactor.name })}</strong>: {currentFactor.score}/{currentFactor.max_score}
                            <span className={`mini-risk-pill risk-${factorLevel}`}>
                              {t(`farmHealth.levels.${factorLevel}`, { defaultValue: factorLevel.toUpperCase() })}
                            </span>
                          </div>
                          <p className="node-content-text">{factorReason}</p>
                        </div>

                        <div className="chain-connector-arrow" aria-hidden="true">
                          <FiArrowRight size={22} />
                        </div>

                        {/* Step 3: RECOMMENDATION */}
                        <div className="chain-step-node node-recommendation">
                          <div className="node-badge-header">
                            <span className="node-step-tag">STEP 3</span>
                            <span className="node-type-title">🛡️ {t('decisionChain.recommendation')}</span>
                          </div>
                          <span className="node-sublabel">{t('decisionChain.actionDesc')}</span>
                          <p className="node-content-text">{recText}</p>
                        </div>
                      </div>
                    </div>
                  )
                })()}

                {/* Expandable "Why this Score?" Accordion */}
                <div className="why-score-accordion">
                  <button
                    type="button"
                    className="why-score-toggle-btn"
                    onClick={() => setExpandedBreakdown(!expandedBreakdown)}
                    aria-expanded={expandedBreakdown}
                  >
                    <div className="why-score-toggle-left">
                      <span className="why-score-icon">🔍</span>
                      <div className="why-score-text-group">
                        <span className="why-score-headline">{t('distressIndex.whyScoreTitle')}</span>
                        <span className="why-score-subheadline">{t('distressIndex.whyScoreSubtitle')}</span>
                      </div>
                    </div>
                    <span className={`accordion-chevron ${expandedBreakdown ? 'open' : ''}`}>▼</span>
                  </button>

                  {expandedBreakdown && (
                    <motion.div
                      className="why-score-content"
                      initial={{ opacity: 0, height: 0 }}
                      animate={{ opacity: 1, height: 'auto' }}
                      transition={{ duration: 0.25 }}
                    >
                      <div className="breakdown-factors-list">
                        {farmHealth.factors.map((factor, idx) => {
                          let pillarMeta = PILLAR_CONFIG.find(p => factor.name.toLowerCase().includes(p.key)) || PILLAR_CONFIG[idx] || {
                            icon: '⚡',
                            key: 'context',
                            titleKey: 'distressIndex.pillars.context',
                            max: factor.max_score || 20
                          }
                          const factorLevel = (factor.level || 'LOW').toLowerCase()
                          const reasonText = factor.key
                            ? t(factor.key, factor.params || {}, { defaultValue: factor.reason })
                            : factor.reason

                          const explanationText = t(`distressIndex.whyMattersExplanations.${pillarMeta.key}`, {
                            defaultValue: 'Environmental and management signals directly impact crop vigor and farmer profitability.'
                          })

                          return (
                            <div key={idx} className={`breakdown-factor-card factor-risk-${factorLevel}`}>
                              <div className="breakdown-factor-header">
                                <div className="breakdown-factor-title">
                                  <span className="breakdown-emoji">{pillarMeta.icon}</span>
                                  <span className="breakdown-name">{t(pillarMeta.titleKey, { defaultValue: factor.name })}</span>
                                  <span className={`breakdown-badge risk-${factorLevel}`}>
                                    {t(`farmHealth.levels.${factorLevel}`, { defaultValue: factorLevel.toUpperCase() })}
                                  </span>
                                </div>
                                <div className="breakdown-score-badge">
                                  {factor.score} / {factor.max_score}
                                </div>
                              </div>

                              <div className="breakdown-grid">
                                <div className="breakdown-cell happening-cell">
                                  <div className="breakdown-cell-label">📌 {t('distressIndex.whatHappening')}</div>
                                  <p className="breakdown-cell-text">{reasonText}</p>
                                </div>
                                <div className="breakdown-cell matters-cell">
                                  <div className="breakdown-cell-label">⚠️ {t('distressIndex.whyMatters')}</div>
                                  <p className="breakdown-cell-text">{explanationText}</p>
                                </div>
                              </div>
                            </div>
                          )
                        })}
                      </div>
                    </motion.div>
                  )}
                </div>

              </div>
            </motion.section>
          )}

          {/* ============================================================
              5 - 9. FIVE CORE DIAGNOSTIC DOMAINS: WEATHER, SOIL, DISEASE, CROP, MARKET
              ============================================================ */}
          <section className="domains-grid-section">
            <h2 className="section-heading">🌾 {t('dashboard.tools')}</h2>
            <div className="domains-grid">

              {/* 5. WEATHER CARD */}
              <div className="domain-card weather-domain-card">
                <div className="domain-card-header">
                  <div className="domain-icon-box weather-domain-icon">
                    <FiCloudRain size={22} />
                  </div>
                  <div>
                    <h3 className="domain-card-title">{t('dashboard.liveWeather')}</h3>
                    <p className="domain-card-subtitle">{user?.location || t('dashboard.localStation')}</p>
                  </div>
                  <Link to="/weather" className="domain-card-link">
                    {t('dashboard.forecast')} <FiChevronRight size={14} />
                  </Link>
                </div>
                <div className="domain-metrics-row">
                  <div className="metric-badge">
                    <span className="metric-number">{weatherSnapshot?.main?.temp ? `${Math.round(weatherSnapshot.main.temp)}°C` : '28°C'}</span>
                    <span className="metric-label">{t('dashboard.temp')}</span>
                  </div>
                  <div className="metric-badge">
                    <span className="metric-number">{weatherSnapshot?.main?.humidity ? `${weatherSnapshot.main.humidity}%` : '65%'}</span>
                    <span className="metric-label">{t('dashboard.humidity')}</span>
                  </div>
                  <div className="metric-badge">
                    <span className="metric-number">{weatherSnapshot?.wind?.speed ? `${Math.round(weatherSnapshot.wind.speed * 3.6)} km/h` : '12 km/h'}</span>
                    <span className="metric-label">{t('dashboard.wind')}</span>
                  </div>
                </div>
                <p className="domain-summary-text">
                  {weatherSnapshot?.weather?.[0]?.description 
                    ? weatherSnapshot.weather[0].description.toUpperCase()
                    : t('dashboard.favorableConditions')}
                </p>
                <Link to="/weather" className="btn btn-domain-action">
                  🌧 {t('dashboard.weatherAlerts')} →
                </Link>
              </div>

              {/* 6. SOIL CARD */}
              <div className="domain-card soil-domain-card">
                <div className="domain-card-header">
                  <div className="domain-icon-box soil-domain-icon">
                    <FiDroplet size={22} />
                  </div>
                  <div>
                    <h3 className="domain-card-title">{t('dashboard.soilAnalysis')}</h3>
                    <p className="domain-card-subtitle">{t('dashboard.soilStatus')}</p>
                  </div>
                  <Link to="/soil-analysis" className="domain-card-link">
                    {t('common.details')} <FiChevronRight size={14} />
                  </Link>
                </div>
                <div className="soil-quick-status-row">
                  <div className="soil-chip"><span>pH:</span> <strong>6.8 (Optimal)</strong></div>
                  <div className="soil-chip"><span>NPK:</span> <strong>Balanced</strong></div>
                  <div className="soil-chip"><span>Organic:</span> <strong>0.75%</strong></div>
                </div>
                <p className="domain-summary-text">
                  {t('dashboard.soilAnalysisDesc')}
                </p>
                <div className="domain-btn-dual">
                  <Link to="/soil-analysis" className="btn btn-domain-action">
                    🌱 {t('dashboard.soilAnalysis')}
                  </Link>
                  <Link to="/soil-detection" className="btn btn-domain-action-subtle">
                    {t('dashboard.soilType')}
                  </Link>
                </div>
              </div>

              {/* 7. DISEASE CARD */}
              <div className="domain-card disease-domain-card">
                <div className="domain-card-header">
                  <div className="domain-icon-box disease-domain-icon">
                    <FiActivity size={22} />
                  </div>
                  <div>
                    <h3 className="domain-card-title">{t('dashboard.plantPathology')}</h3>
                    <p className="domain-card-subtitle">{t('dashboard.modelBadge')}</p>
                  </div>
                  <Link to="/disease-detection" className="domain-card-link">
                    {t('dashboard.scan')} <FiChevronRight size={14} />
                  </Link>
                </div>
                <div className="disease-status-wrapper">
                  <div className="disease-status-badge-row">
                    <span className="status-indicator-dot healthy"></span>
                    <span className="status-indicator-text">{t('dashboard.cropsMonitored')}</span>
                  </div>
                  <p className="domain-summary-text">
                    {t('dashboard.conditionsSupported')}
                  </p>
                </div>
                <Link to="/disease-detection" className="btn btn-domain-action">
                  {t('dashboard.scanLeafBtn')}
                </Link>
              </div>

              {/* 8. CROP CARD */}
              <div className="domain-card crop-domain-card">
                <div className="domain-card-header">
                  <div className="domain-icon-box crop-domain-icon">
                    <FiShield size={22} />
                  </div>
                  <div>
                    <h3 className="domain-card-title">{t('dashboard.cropRecommendation')}</h3>
                    <p className="domain-card-subtitle">{t('dashboard.activeStandingCrop')}: {activeCropName}</p>
                  </div>
                  <Link to="/crop-recommendation" className="domain-card-link">
                    {t('common.explore')} <FiChevronRight size={14} />
                  </Link>
                </div>
                <div className="crop-status-chips-row">
                  <span className="crop-stage-badge">🌱 Vegetative Growth Phase</span>
                  <span className="crop-yield-badge">92% Health Index</span>
                </div>
                <p className="domain-summary-text">
                  {t('dashboard.cropRecommendationDesc')}
                </p>
                <Link to="/crop-recommendation" className="btn btn-domain-action">
                  🌾 {t('dashboard.cropRecommendation')} →
                </Link>
              </div>

              {/* 9. MARKET CARD */}
              <div className="domain-card market-domain-card">
                <div className="domain-card-header">
                  <div className="domain-icon-box market-domain-icon">
                    <FiTrendingUp size={22} />
                  </div>
                  <div>
                    <h3 className="domain-card-title">{t('dashboard.localMandi')}</h3>
                    <p className="domain-card-subtitle">{marketSnapshot?.state || 'Andhra Pradesh'}</p>
                  </div>
                  <Link to="/market-prices" className="domain-card-link">
                    {t('dashboard.prices')} <FiChevronRight size={14} />
                  </Link>
                </div>
                <div className="mandi-rows-container">
                  {(marketSnapshot?.crops || [
                    { crop_name: 'Chilli', latest_price: 18500, trend: 'down', change_percent: 11.7 },
                    { crop_name: 'Cotton', latest_price: 6800, trend: 'up', change_percent: 4.2 },
                    { crop_name: 'Rice', latest_price: 2400, trend: 'stable', change_percent: 0.5 }
                  ]).slice(0, 3).map((crop, i) => (
                    <div key={i} className="mandi-price-row">
                      <span className="mandi-crop-name">{t(`crops.${crop.crop_name.toLowerCase().replace(/[^a-z]/g, '')}`, { defaultValue: crop.crop_name })}</span>
                      <div className="mandi-price-trend">
                        <span className="mandi-price-val">₹{crop.latest_price}/q</span>
                        <span className={`mandi-trend-tag ${crop.trend}`}>
                          {crop.trend === 'up' ? '↑' : crop.trend === 'down' ? '↓' : '→'} {Math.abs(crop.change_percent)}%
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
                <Link to="/market-prices" className="btn btn-domain-action">
                  📈 {t('dashboard.marketPrices')} →
                </Link>
              </div>

            </div>
          </section>

          {/* ============================================================
              10. INTERACTIVE AI ADVISORY SECTION (Gemini AI + Rule Fallback + Farmer Voice Mode)
              ============================================================ */}
          <motion.section
            className="dashboard-advisory-section"
            initial={{ opacity: 0, y: 14 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.15 }}
          >
            <div className="dashboard-advisory-card">
              <div className="advisory-card-header">
                <div className="advisory-title-box">
                  <div className="advisory-icon-sparkle">
                    <FiZap size={24} />
                  </div>
                  <div>
                    <div className="advisory-heading-row">
                      <h3 className="advisory-main-title">{t('dashboardAdvisory.title')}</h3>
                      <span className="advisory-platform-badge">AgriDarshak AI</span>
                    </div>
                    <p className="advisory-main-desc">{t('dashboardAdvisory.subtitle')}</p>
                  </div>
                </div>

                <div className="advisory-source-indicator-box">
                  <span className={`advisory-source-tag source-${advisorySource}`}>
                    {advisorySource === 'ai' ? '✨ ' + t('advisory.aiAdvisory') : '🌱 ' + t('advisory.smartAdvisory')}
                  </span>
                </div>
              </div>

              {/* Interactive Query Input */}
              <div className="advisory-query-box">
                <div className="advisory-input-group">
                  <input
                    type="text"
                    className="advisory-input"
                    value={advisoryQuery}
                    onChange={(e) => setAdvisoryQuery(e.target.value)}
                    placeholder={t('dashboardAdvisory.placeholder')}
                    onKeyDown={(e) => { if (e.key === 'Enter') handleAskAdvisory() }}
                  />
                  <button
                    type="button"
                    className="btn btn-advisory-ask"
                    onClick={() => handleAskAdvisory()}
                    disabled={advisoryLoading}
                  >
                    {advisoryLoading ? (
                      <span>{t('dashboardAdvisory.generating')}</span>
                    ) : (
                      <>
                        <FiSend size={16} />
                        <span>{t('dashboardAdvisory.askBtn')}</span>
                      </>
                    )}
                  </button>
                </div>

                {/* Quick Prompts */}
                <div className="advisory-quick-prompts">
                  <span className="quick-prompts-label">{t('dashboardAdvisory.quickPrompts')}</span>
                  <button
                    type="button"
                    className="quick-prompt-btn"
                    onClick={() => { setAdvisoryQuery(t('dashboardAdvisory.promptWeather')); handleAskAdvisory(t('dashboardAdvisory.promptWeather')); }}
                  >
                    🌦️ {t('dashboardAdvisory.promptWeather')}
                  </button>
                  <button
                    type="button"
                    className="quick-prompt-btn"
                    onClick={() => { setAdvisoryQuery(t('dashboardAdvisory.promptPest')); handleAskAdvisory(t('dashboardAdvisory.promptPest')); }}
                  >
                    🐛 {t('dashboardAdvisory.promptPest')}
                  </button>
                  <button
                    type="button"
                    className="quick-prompt-btn"
                    onClick={() => { setAdvisoryQuery(t('dashboardAdvisory.promptMarket')); handleAskAdvisory(t('dashboardAdvisory.promptMarket')); }}
                  >
                    📈 {t('dashboardAdvisory.promptMarket')}
                  </button>
                </div>
              </div>

              {/* Advisory Response Display */}
              {advisoryContent && (
                <div className="advisory-result-display">
                  <AdvisoryMarkdown
                    content={advisoryContent}
                    language={effectiveLang}
                    source={advisorySource}
                  />
                </div>
              )}
            </div>
          </motion.section>

        </div>
      </div>
    </AppLayout>
  )
}

export default Dashboard
