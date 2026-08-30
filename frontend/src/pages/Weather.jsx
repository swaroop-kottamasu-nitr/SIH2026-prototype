import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import axios from 'axios'
import { motion } from 'framer-motion'
import AppLayout from '../components/AppLayout'
import { FiArrowLeft } from 'react-icons/fi'
import './FeaturePage.css'

function Weather({ user, onLogout, onUserUpdate }) {
  const { t } = useTranslation()
  const [weather, setWeather] = useState(null)
  const [alerts, setAlerts] = useState([])
  const [loading, setLoading] = useState(true)

  const [states, setStates] = useState(['Andhra Pradesh'])
  const [cities, setCities] = useState([])
  const [selectedState, setSelectedState] = useState('Andhra Pradesh')
  const [selectedCity, setSelectedCity] = useState('')
  const [citiesLoading, setCitiesLoading] = useState(false)

  const location = selectedCity || (cities.length > 0 ? cities[0] : selectedState)

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
    setCitiesLoading(true)
    setSelectedCity('')
    axios.get(`/api/market/cities/${encodeURIComponent(selectedState)}`)
      .then(res => setCities(res.data?.cities || []))
      .catch(() => setCities([]))
      .finally(() => setCitiesLoading(false))
  }, [selectedState])

  useEffect(() => {
    if (!location) return
    const load = async () => {
      setLoading(true)
      try {
        const [wRes, syncRes] = await Promise.all([
          axios.post('/api/weather/current', { location }),
          axios.post('/api/weather/sync-alerts', { user_id: user.id, location }).catch(() => ({ data: { alerts: [] } }))
        ])
        setWeather(wRes.data)
        setAlerts(syncRes.data?.alerts || [])
      } catch {
        setAlerts([])
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [location, user.id])

  if (loading && !weather) {
    return (
      <AppLayout user={user} onLogout={onLogout} onUserUpdate={onUserUpdate}>
        <div className="loading-state"><div className="spinner" /></div>
      </AppLayout>
    )
  }

  return (
    <AppLayout user={user} onLogout={onLogout} onUserUpdate={onUserUpdate}>
      <div className="feature-page">
        <div className="container">
          <Link to="/dashboard" className="back-link"><FiArrowLeft size={16} /> {t('common.backToDashboard')}</Link>
          <div className="page-header">
            <h1 className="page-title">{t('weather.title')}</h1>
            <p className="page-subtitle">
              {t('weather.liveFor', { district: location })}
              <span className="live-badge" title="Real-time data from Open-Meteo"> {t('weather.liveBadge')}</span>
            </p>
            <div className="weather-location-select" style={{ display: 'flex', flexWrap: 'wrap', gap: 'var(--space-3)', marginTop: 'var(--space-2)', alignItems: 'center' }}>
              <div>
                <label className="param-label" style={{ display: 'block', marginBottom: 'var(--space-1)' }}>{t('market.selectState')}</label>
                <select
                  className="form-select"
                  style={{ minWidth: 200 }}
                  value={selectedState}
                  onChange={e => setSelectedState(e.target.value)}
                >
                  {states.map(s => <option key={s} value={s}>{s}</option>)}
                </select>
              </div>
              <div>
                <label className="param-label" style={{ display: 'block', marginBottom: 'var(--space-1)' }}>{t('market.selectCity')}</label>
                <select
                  className="form-select"
                  style={{ minWidth: 200 }}
                  value={selectedCity}
                  onChange={e => setSelectedCity(e.target.value)}
                  disabled={!selectedState || citiesLoading}
                >
                  <option value="">{citiesLoading ? (t('soilType.loading') || 'Loading...') : t('weather.selectCity')}</option>
                  {cities.map(c => <option key={c} value={c}>{c}</option>)}
                </select>
              </div>
            </div>
          </div>

          <div className="feature-content">
            {weather?.main && (
              <motion.div
                className="weather-card"
                initial={{ opacity: 0, y: 16 }}
                animate={{ opacity: 1, y: 0 }}
              >
                <div className="weather-main">
                  <div className="temp-display">{Math.round(weather.main.temp)}°C</div>
                  <div className="weather-desc">{weather.weather?.[0]?.description || 'Clear'}</div>
                </div>
                <div className="weather-details">
                  <div className="detail-item"><span className="param-label">{t('weather.humidity')}</span><span className="param-value">{weather.main.humidity}%</span></div>
                  <div className="detail-item"><span className="param-label">{t('weather.wind')}</span><span className="param-value">{(weather.wind?.speed * 3.6 || 0).toFixed(1)} km/h</span></div>
                  <div className="detail-item"><span className="param-label">{t('weather.feelsLike')}</span><span className="param-value">{Math.round(weather.main.feels_like)}°C</span></div>
                </div>
              </motion.div>
            )}

            {alerts.length > 0 ? (
              <div>
                <h2 className="section-heading" style={{ marginBottom: 'var(--space-4)' }}>{t('weather.activeAlerts')}</h2>
                <div className="alerts-grid">
                  {alerts.map((alert, i) => (
                    <div key={i} className={`alert-card severity-${alert.severity}`}>
                      <span className="alert-badge">{alert.severity}</span>
                      <h3>{alert.title}</h3>
                      <p>{alert.description}</p>
                    </div>
                  ))}
                </div>
              </div>
            ) : (
              <div className="card" style={{ textAlign: 'center', padding: 'var(--space-12)' }}>
                <p style={{ color: 'var(--color-text-secondary)' }}>{t('weather.noAlerts')}</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </AppLayout>
  )
}

export default Weather
