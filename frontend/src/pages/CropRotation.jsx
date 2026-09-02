import { useState, useEffect } from 'react'
import { useTranslation } from 'react-i18next'
import axios from 'axios'
import { motion } from 'framer-motion'
import AppLayout from '../components/AppLayout'
import { getEffectiveLanguage } from '../i18n'
import { 
  FiRefreshCw, FiCheckCircle, FiShield, FiTrendingUp, 
  FiLayers, FiInfo, FiPlus, FiTrash2
} from 'react-icons/fi'
import './CropRotation.css'

const CROPS = ['Rice', 'Paddy', 'Wheat', 'Cotton', 'Chilli', 'Tomato', 'Potato', 'Maize', 'Sugarcane', 'Groundnut', 'Soybean', 'Chickpea']
const SEASONS = [
  { key: 'rabi', label: 'Rabi (Winter - Oct to Mar)' },
  { key: 'summer', label: 'Summer / Zaid (Mar to Jun)' },
  { key: 'kharif', label: 'Kharif (Monsoon - Jun to Oct)' }
]
const SOIL_TYPES = ['Loamy', 'Black Soil', 'Clay', 'Sandy', 'Alluvial', 'Red Soil']

export default function CropRotation({ user, onLogout, onUserUpdate }) {
  const { t, i18n } = useTranslation()

  const defaultCrop = (user?.preferred_crops && user.preferred_crops.length > 0)
    ? user.preferred_crops[0]
    : 'Rice'

  const [previousCrop, setPreviousCrop] = useState(defaultCrop)
  const [season, setSeason] = useState('rabi')
  const [soilType, setSoilType] = useState('Loamy')
  
  // Crop history list
  const [historyList, setHistoryList] = useState(['Rice', 'Maize'])
  const [newHistoryCrop, setNewHistoryCrop] = useState('')

  const [loading, setLoading] = useState(false)
  const [rotationData, setRotationData] = useState(null)

  const fetchRotationPlan = async () => {
    setLoading(true)
    try {
      const res = await axios.post('/api/v1/crop-rotation/recommendation', {
        previous_crop: previousCrop,
        season,
        soil_type: soilType,
        crop_history: historyList,
        user_id: user?.id || 1,
        language: getEffectiveLanguage(user)
      }, { timeout: 12000 })

      if (res.data) {
        setRotationData(res.data)
      }
    } catch (err) {
      console.error('Crop rotation fetch error:', err)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchRotationPlan()
  }, [i18n.language, user?.language])

  const handleAddHistory = () => {
    if (newHistoryCrop.trim() && !historyList.includes(newHistoryCrop.trim())) {
      setHistoryList([...historyList, newHistoryCrop.trim()])
      setNewHistoryCrop('')
    }
  }

  const handleRemoveHistory = (index) => {
    setHistoryList(historyList.filter((_, i) => i !== index))
  }

  return (
    <AppLayout user={user} onLogout={onLogout} onUserUpdate={onUserUpdate}>
      <div className="rotation-page">
        <div className="container">
          
          {/* Header */}
          <motion.div 
            className="rotation-header"
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
          >
            <div className="rotation-title-box">
              <div className="rotation-icon-badge">
                <FiRefreshCw size={26} />
              </div>
              <div>
                <h1 className="rotation-title">{t('crop_rotation.title', { defaultValue: 'Crop Rotation Planner' })}</h1>
                <p className="rotation-subtitle">
                  {t('crop_rotation.subtitle', { defaultValue: 'Scientifically designed rotation cycles to break pest vectors, fix soil nitrogen, and sustain yield vitality' })}
                </p>
              </div>
            </div>
          </motion.div>

          <div className="rotation-grid">
            {/* 1. Rotation Input Parameters */}
            <motion.div 
              className="rotation-card form-card"
              initial={{ opacity: 0, y: 16 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 }}
            >
              <h3 className="card-heading">🌱 {t('crop_rotation.setupTitle', { defaultValue: 'Field & Cropping History' })}</h3>

              <div className="form-group">
                <label className="form-label">{t('crop_rotation.prevCrop', { defaultValue: 'Preceding / Current Standing Crop' })}</label>
                <select 
                  className="form-select"
                  value={previousCrop}
                  onChange={(e) => setPreviousCrop(e.target.value)}
                >
                  {CROPS.map(c => <option key={c} value={c}>{c}</option>)}
                </select>
              </div>

              <div className="form-group">
                <label className="form-label">{t('crop_rotation.targetSeason', { defaultValue: 'Next Sowing Season' })}</label>
                <select 
                  className="form-select"
                  value={season}
                  onChange={(e) => setSeason(e.target.value)}
                >
                  {SEASONS.map(s => <option key={s.key} value={s.key}>{s.label}</option>)}
                </select>
              </div>

              <div className="form-group">
                <label className="form-label">{t('crop_rotation.soilType', { defaultValue: 'Soil Type' })}</label>
                <select 
                  className="form-select"
                  value={soilType}
                  onChange={(e) => setSoilType(e.target.value)}
                >
                  {SOIL_TYPES.map(s => <option key={s} value={s}>{s}</option>)}
                </select>
              </div>

              {/* Crop History Tags */}
              <div className="form-group">
                <label className="form-label">{t('crop_rotation.cropHistoryLabel', { defaultValue: 'Past Crops Grown in Field (Unlocks High Confidence)' })}</label>
                <div className="history-input-row">
                  <input 
                    type="text"
                    className="form-input"
                    value={newHistoryCrop}
                    onChange={(e) => setNewHistoryCrop(e.target.value)}
                    placeholder="e.g. Cotton, Moong"
                    onKeyDown={(e) => { if (e.key === 'Enter') handleAddHistory() }}
                  />
                  <button 
                    type="button" 
                    className="btn btn-secondary add-tag-btn"
                    onClick={handleAddHistory}
                  >
                    <FiPlus size={16} />
                  </button>
                </div>

                <div className="history-tags-list">
                  {historyList.map((item, idx) => (
                    <span key={idx} className="history-tag">
                      {item}
                      <button type="button" onClick={() => handleRemoveHistory(idx)} className="tag-remove-btn">
                        <FiTrash2 size={12} />
                      </button>
                    </span>
                  ))}
                  {historyList.length === 0 && (
                    <span className="no-history-hint">No past history specified (Generalized plan active)</span>
                  )}
                </div>
              </div>

              <button 
                type="button" 
                className="btn btn-primary full-width-btn"
                onClick={fetchRotationPlan}
                disabled={loading}
              >
                {loading ? t('common.loading', { defaultValue: 'Evaluating Agronomic Synergies...' }) : t('crop_rotation.generateBtn', { defaultValue: '🌾 Generate Rotation Plan' })}
              </button>
            </motion.div>

            {/* 2. Recommended Crops List */}
            <motion.div 
              className="rotation-card results-card"
              initial={{ opacity: 0, y: 16 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.15 }}
            >
              <div className="results-header-row">
                <h3 className="card-heading" style={{ border: 'none', margin: 0, padding: 0 }}>
                  🌾 {t('crop_rotation.recommended_crop', { defaultValue: 'Optimal Successor Crops' })}
                </h3>
                {rotationData && (
                  <span className={`source-badge source-${rotationData.data_source}`}>
                    {rotationData.data_source === 'history_based' ? '🏆 History-Based (High Confidence)' : '📖 Agronomic Family Plan'}
                  </span>
                )}
              </div>

              {rotationData && rotationData.recommendations?.length > 0 ? (
                <div className="recommendations-list">
                  {rotationData.recommendations.map((rec, idx) => (
                    <motion.div 
                      key={idx} 
                      className="rotation-item-card"
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: 0.1 + idx * 0.05 }}
                    >
                      <div className="item-card-header">
                        <div className="crop-badge-name">
                          <span className="crop-seed-icon">🌿</span>
                          <span className="crop-name-text">{rec.crop}</span>
                        </div>
                        <div className="suitability-pill-group">
                          <span className={`suitability-tag suit-${rec.season_suitability.toLowerCase()}`}>
                            {rec.season_suitability} {t('crop_rotation.season_suitability', { defaultValue: 'Suitability' })}
                          </span>
                          <span className={`confidence-tag conf-${rec.confidence.toLowerCase()}`}>
                            {rec.confidence} {t('crop_rotation.confidence', { defaultValue: 'Confidence' })}
                          </span>
                        </div>
                      </div>

                      <div className="item-body-grid">
                        <div className="item-body-block">
                          <div className="block-label">💡 {t('crop_rotation.reason', { defaultValue: 'Agronomic Rationale' })}</div>
                          <p className="block-text">{rec.reason}</p>
                        </div>

                        <div className="item-body-block">
                          <div className="block-label">🌱 {t('crop_rotation.soil_benefit', { defaultValue: 'Soil Health & Fertility Impact' })}</div>
                          <p className="block-text">{rec.soil_benefit}</p>
                        </div>

                        {rec.pest_break_benefit && (
                          <div className="item-body-block">
                            <div className="block-label">🛡️ {t('crop_rotation.pest_break', { defaultValue: 'Pest & Pathogen Break' })}</div>
                            <p className="block-text">{rec.pest_break_benefit}</p>
                          </div>
                        )}
                      </div>
                    </motion.div>
                  ))}
                </div>
              ) : (
                <div className="empty-state">
                  <FiRefreshCw size={48} className="empty-icon" />
                  <p>{t('crop_rotation.emptyPrompt', { defaultValue: 'Configure your previous crop and target season to generate rotation recommendations.' })}</p>
                </div>
              )}
            </motion.div>
          </div>

        </div>
      </div>
    </AppLayout>
  )
}
