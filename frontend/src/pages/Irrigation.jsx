import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import axios from 'axios'
import { motion } from 'framer-motion'
import AppLayout from '../components/AppLayout'
import AdvisoryMarkdown from '../components/AdvisoryMarkdown'
import { 
  FiDroplet, FiClock, FiShield, FiTrendingUp, FiCloudRain, 
  FiCheckCircle, FiInfo, FiAlertCircle, FiArrowRight, FiZap
} from 'react-icons/fi'
import './Irrigation.css'

const CROPS = ['Chilli', 'Rice', 'Cotton', 'Tomato', 'Wheat', 'Maize', 'Groundnut', 'Sugarcane', 'Potato', 'Onion', 'Soybean', 'Chickpea']
const STAGES = [
  { key: 'seedling', label: 'Seedling / Nursery' },
  { key: 'vegetative', label: 'Vegetative Growth' },
  { key: 'flowering', label: 'Flowering & Budding (Critical)' },
  { key: 'fruiting', label: 'Fruiting / Grain Filling' },
  { key: 'maturity', label: 'Maturity / Pre-Harvest' }
]
const SOIL_TYPES = ['Loamy', 'Black Soil', 'Clay', 'Sandy', 'Alluvial', 'Red Soil']

export default function Irrigation({ user, onLogout, onUserUpdate }) {
  const { t } = useTranslation()

  const defaultCrop = (user?.preferred_crops && user.preferred_crops.length > 0)
    ? user.preferred_crops[0]
    : 'Chilli'

  const [crop, setCrop] = useState(defaultCrop)
  const [growthStage, setGrowthStage] = useState('flowering')
  const [soilType, setSoilType] = useState('Loamy')
  const [location, setLocation] = useState(user?.location || 'Vijayawada, Andhra Pradesh')
  
  const [loading, setLoading] = useState(false)
  const [recommendation, setRecommendation] = useState(null)
  
  // Minimal AI Integration
  const [aiLoading, setAiLoading] = useState(false)
  const [aiAdvisory, setAiAdvisory] = useState(null)

  const fetchIrrigationSchedule = async () => {
    setLoading(true)
    try {
      const res = await axios.post('/api/v1/irrigation/recommendation', {
        crop,
        growth_stage: growthStage,
        soil_type: soilType,
        location,
        user_id: user?.id || 1
      }, { timeout: 12000 })

      if (res.data?.recommendation) {
        setRecommendation(res.data.recommendation)
      }
    } catch (err) {
      console.error('Irrigation schedule fetch error:', err)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchIrrigationSchedule()
  }, [])

  const handleAskAdvisory = async () => {
    if (aiLoading) return
    setAiLoading(true)
    try {
      const prompt = `Irrigation and water management advice for ${crop} at ${growthStage} stage in ${location}`
      const res = await axios.post('/api/v1/advisory', {
        question: prompt,
        language: user?.language || 'en',
        context: {
          crop,
          location,
          growth_stage: growthStage,
          soil_type: soilType
        }
      }, { timeout: 15000 })
      if (res.data?.advisory) {
        setAiAdvisory(res.data.advisory)
      }
    } catch (err) {
      console.error('Advisory fetch error:', err)
    } finally {
      setAiLoading(false)
    }
  }

  return (
    <AppLayout user={user} onLogout={onLogout} onUserUpdate={onUserUpdate}>
      <div className="irrigation-page">
        <div className="container">
          
          {/* Header */}
          <motion.div 
            className="irrigation-header"
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
          >
            <div className="irrigation-title-box">
              <div className="irrigation-icon-badge">
                <FiDroplet size={26} />
              </div>
              <div>
                <h1 className="irrigation-title">{t('irrigation.title', { defaultValue: 'Smart Irrigation Scheduler' })}</h1>
                <p className="irrigation-subtitle">
                  {t('irrigation.subtitle', { defaultValue: 'Precision water delivery windows aligned with growth stages and live meteorological forecasts' })}
                </p>
              </div>
            </div>
          </motion.div>

          <div className="irrigation-grid">
            {/* 1. Field Parameters Panel */}
            <motion.div 
              className="irrigation-card form-card"
              initial={{ opacity: 0, y: 16 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 }}
            >
              <h3 className="card-heading">🌾 {t('irrigation.fieldParams', { defaultValue: 'Field Parameters' })}</h3>
              
              <div className="form-group">
                <label className="form-label">{t('irrigation.standingCrop', { defaultValue: 'Standing Crop' })}</label>
                <select 
                  className="form-select"
                  value={crop}
                  onChange={(e) => setCrop(e.target.value)}
                >
                  {CROPS.map(c => <option key={c} value={c}>{c}</option>)}
                </select>
              </div>

              <div className="form-group">
                <label className="form-label">{t('irrigation.growthStage', { defaultValue: 'Growth Stage' })}</label>
                <select 
                  className="form-select"
                  value={growthStage}
                  onChange={(e) => setGrowthStage(e.target.value)}
                >
                  {STAGES.map(s => <option key={s.key} value={s.key}>{s.label}</option>)}
                </select>
              </div>

              <div className="form-group">
                <label className="form-label">{t('irrigation.soilType', { defaultValue: 'Soil Type' })}</label>
                <select 
                  className="form-select"
                  value={soilType}
                  onChange={(e) => setSoilType(e.target.value)}
                >
                  {SOIL_TYPES.map(s => <option key={s} value={s}>{s}</option>)}
                </select>
              </div>

              <div className="form-group">
                <label className="form-label">{t('irrigation.farmLocation', { defaultValue: 'Farm Location' })}</label>
                <input 
                  type="text"
                  className="form-input"
                  value={location}
                  onChange={(e) => setLocation(e.target.value)}
                  placeholder="e.g. Vijayawada, Andhra Pradesh"
                />
              </div>

              <button 
                type="button" 
                className="btn btn-primary full-width-btn"
                onClick={fetchIrrigationSchedule}
                disabled={loading}
              >
                {loading ? t('common.loading', { defaultValue: 'Calculating Schedule...' }) : t('irrigation.calculateBtn', { defaultValue: '💧 Calculate Optimal Window' })}
              </button>
            </motion.div>

            {/* 2. Schedule Recommendation Panel */}
            <motion.div 
              className="irrigation-card results-card"
              initial={{ opacity: 0, y: 16 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.15 }}
            >
              {recommendation ? (
                <div>
                  <div className="window-hero-box">
                    <div className="window-header-row">
                      <span className="window-badge-label">
                        <FiClock size={16} /> {t('irrigation.next_window', { defaultValue: 'Recommended Irrigation Window' })}
                      </span>
                      <span className={`priority-tag priority-${recommendation.priority.toLowerCase()}`}>
                        {recommendation.priority} {t('irrigation.priority', { defaultValue: 'PRIORITY' })}
                      </span>
                    </div>
                    <div className="window-time-display">
                      {recommendation.next_window}
                    </div>
                  </div>

                  {/* Recommendation Details */}
                  <div className="rec-detail-row">
                    <div className="detail-icon"><FiInfo size={18} /></div>
                    <div>
                      <div className="detail-title">{t('irrigation.reason', { defaultValue: 'Agronomic Justification' })}</div>
                      <div className="detail-text">{recommendation.reason}</div>
                    </div>
                  </div>

                  <div className="rec-detail-row">
                    <div className="detail-icon"><FiTrendingUp size={18} /></div>
                    <div>
                      <div className="detail-title">{t('irrigation.benefit', { defaultValue: 'Expected Benefit' })}</div>
                      <div className="detail-text">{recommendation.expected_benefit}</div>
                    </div>
                  </div>

                  <div className="rec-detail-row">
                    <div className="detail-icon"><FiCloudRain size={18} /></div>
                    <div>
                      <div className="detail-title">{t('irrigation.weather_factor', { defaultValue: 'Weather & Forecast Condition' })}</div>
                      <div className="detail-text">{recommendation.weather_factor}</div>
                    </div>
                  </div>

                  {/* Data Availability Badges */}
                  <div className="data-avail-box">
                    <span className="avail-label">{t('irrigation.data_available', { defaultValue: 'Telemetry & Forecast Sources Used:' })}</span>
                    <div className="avail-pills">
                      <span className={`pill ${recommendation.data_available.weather_forecast ? 'active' : 'inactive'}`}>
                        🌦️ {recommendation.data_available.weather_forecast ? 'Weather Forecast: Active' : 'Weather: General Baseline'}
                      </span>
                      <span className={`pill ${recommendation.data_available.rainfall_forecast ? 'active' : 'inactive'}`}>
                        🌧️ {recommendation.data_available.rainfall_forecast ? 'Precipitation Monitored' : 'No Rain Data'}
                      </span>
                      <span className="pill info-pill">
                        📡 Soil Moisture: Manual Check (No In-Situ Sensor)
                      </span>
                    </div>
                  </div>

                  {/* Minimal AI Advisory Integration */}
                  <div className="ai-context-box">
                    <button 
                      type="button" 
                      className="btn btn-secondary ai-ask-btn"
                      onClick={handleAskAdvisory}
                      disabled={aiLoading}
                    >
                      <FiZap size={16} />
                      <span>{aiLoading ? 'Connecting to AgriDarshak AI...' : t('irrigation.askAiBtn', { defaultValue: 'Ask AgriDarshak AI about this recommendation' })}</span>
                    </button>
                    {aiAdvisory && (
                      <div className="ai-advisory-panel">
                        <AdvisoryMarkdown content={aiAdvisory} language={user?.language || 'en'} source="ai" />
                      </div>
                    )}
                  </div>

                </div>
              ) : (
                <div className="empty-state">
                  <FiDroplet size={48} className="empty-icon" />
                  <p>{t('irrigation.emptyPrompt', { defaultValue: 'Select crop parameters to generate precision irrigation schedule.' })}</p>
                </div>
              )}
            </motion.div>
          </div>

        </div>
      </div>
    </AppLayout>
  )
}
