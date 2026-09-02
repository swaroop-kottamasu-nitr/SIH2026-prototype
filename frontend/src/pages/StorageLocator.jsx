import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import axios from 'axios'
import { motion } from 'framer-motion'
import AppLayout from '../components/AppLayout'
import AdvisoryMarkdown from '../components/AdvisoryMarkdown'
import { 
  FiArchive, FiMapPin, FiPhone, FiInfo, FiZap, 
  FiSearch, FiAlertTriangle, FiCheckCircle, FiShield 
} from 'react-icons/fi'
import './StorageLocator.css'

const CROPS = ['Chilli', 'Rice', 'Wheat', 'Cotton', 'Tomato', 'Potato', 'Onion', 'Groundnut', 'Maize', 'Turmeric']

export default function StorageLocator({ user, onLogout, onUserUpdate }) {
  const { t } = useTranslation()
  const [crop, setCrop] = useState('Chilli')
  const [quantity, setQuantity] = useState(50)
  const [location, setLocation] = useState(user?.location || 'Vijayawada, Andhra Pradesh')
  const [facilities, setFacilities] = useState([])
  const [dataSource, setDataSource] = useState('demo')
  const [loading, setLoading] = useState(false)

  // Minimal AI Advisory Integration
  const [aiLoading, setAiLoading] = useState(false)
  const [aiAdvisory, setAiAdvisory] = useState(null)

  const searchStorage = async () => {
    setLoading(true)
    try {
      const res = await axios.post('/api/v1/storage/search', {
        crop,
        quantity: parseFloat(quantity) || 10,
        location,
        language: getEffectiveLanguage(user)
      })
      if (res.data) {
        setFacilities(res.data.facilities || [])
        setDataSource(res.data.data_source || 'demo')
      }
    } catch (err) {
      console.error('Storage search error:', err)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    searchStorage()
  }, [location, i18n.language, user?.language])

  const handleAskStorageAdvisory = async () => {
    if (aiLoading) return
    setAiLoading(true)
    try {
      const prompt = `Post-harvest storage parameters and preservation guidelines for ${quantity} quintals of ${crop} in ${location}. What cold storage conditions or godown precautions are recommended?`
      const res = await axios.post('/api/v1/advisory', {
        question: prompt,
        language: getEffectiveLanguage(user),
        context: {
          crop,
          quantity,
          location
        }
      }, { timeout: 15000 })
      if (res.data?.advisory) {
        setAiAdvisory(res.data.advisory)
      }
    } catch (err) {
      console.error('Storage advisory error:', err)
    } finally {
      setAiLoading(false)
    }
  }

  return (
    <AppLayout user={user} onLogout={onLogout} onUserUpdate={onUserUpdate}>
      <div className="storage-locator-page">
        <div className="container">
          
          {/* Header */}
          <div className="storage-header">
            <div className="storage-title-box">
              <div className="storage-icon-badge">
                <FiArchive size={26} />
              </div>
              <div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', flexWrap: 'wrap' }}>
                  <h1 className="storage-title">{t('storage.title', { defaultValue: 'Post-Harvest Storage Locator' })}</h1>
                  <span className="demo-badge">
                    📋 {t('storage.demo_badge', { defaultValue: 'DEMO DIRECTORY' })}
                  </span>
                </div>
                <p className="storage-subtitle">
                  {t('storage.subtitle', { defaultValue: 'Locate nearby State Warehousing godowns, multi-chamber cold chains, and APMC silos' })}
                </p>
              </div>
            </div>
          </div>

          {/* Search Card */}
          <div className="storage-search-card">
            <div className="storage-search-grid">
              <div className="form-group" style={{ margin: 0 }}>
                <label className="form-label">{t('storage.crop', { defaultValue: 'Commodity / Crop' })}</label>
                <select
                  className="form-select"
                  value={crop}
                  onChange={(e) => setCrop(e.target.value)}
                >
                  {CROPS.map(c => <option key={c} value={c}>{c}</option>)}
                </select>
              </div>

              <div className="form-group" style={{ margin: 0 }}>
                <label className="form-label">{t('storage.quantity', { defaultValue: 'Estimated Quantity (Quintals)' })}</label>
                <input
                  type="number"
                  className="form-input"
                  value={quantity}
                  onChange={(e) => setQuantity(e.target.value)}
                  min="1"
                  placeholder="e.g. 50"
                />
              </div>

              <div className="form-group" style={{ margin: 0 }}>
                <label className="form-label">{t('storage.location', { defaultValue: 'District / Hub Location' })}</label>
                <input
                  type="text"
                  className="form-input"
                  value={location}
                  onChange={(e) => setLocation(e.target.value)}
                  placeholder="e.g. Vijayawada, Andhra Pradesh"
                />
              </div>

              <div style={{ display: 'flex', alignItems: 'flex-end' }}>
                <button
                  type="button"
                  className="btn btn-primary storage-search-btn"
                  onClick={searchStorage}
                  disabled={loading}
                >
                  <FiSearch size={16} />
                  <span>{loading ? t('common.loading', { defaultValue: 'Locating...' }) : t('storage.searchBtn', { defaultValue: 'Find Facilities' })}</span>
                </button>
              </div>
            </div>
          </div>

          {/* Facility Cards */}
          <div className="facilities-container">
            <div className="facilities-header-bar">
              <span className="facilities-count">
                {facilities.length} {t('storage.facilitiesFound', { defaultValue: 'warehousing & cold storage listings' })}
              </span>
              <span className="location-context-tag">
                📍 {location}
              </span>
            </div>

            {loading ? (
              <div className="loading-state">{t('common.loading', { defaultValue: 'Locating storage facilities...' })}</div>
            ) : facilities.length > 0 ? (
              <div className="facilities-grid">
                {facilities.map((fac, idx) => (
                  <motion.div
                    key={idx}
                    className="facility-card"
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: idx * 0.04 }}
                  >
                    <div className="facility-card-header">
                      <div>
                        <span className="facility-name">{fac.name}</span>
                        <div className="facility-type-row">
                          <span className={`type-tag type-${fac.type.toLowerCase().replace(/\s+/g, '-')}`}>
                            {fac.type}
                          </span>
                          <span className="unconfirmed-status-tag">
                            <FiAlertTriangle size={12} /> {t('storage.availability_needs_confirmation', { defaultValue: 'Availability needs confirmation' })}
                          </span>
                        </div>
                      </div>
                      {fac.distance && (
                        <div className="facility-distance">
                          {fac.distance} km
                        </div>
                      )}
                    </div>

                    <div className="facility-card-body">
                      <div className="facility-detail-line">
                        <span className="detail-prop">{t('storage.capacity', { defaultValue: 'Capacity' })}:</span>
                        <span className="detail-val">
                          {fac.capacity_known ? fac.capacity : t('storage.capacity_unknown', { defaultValue: 'Capacity: Not specified' })}
                        </span>
                      </div>

                      <div className="facility-info-row">
                        <FiMapPin size={15} className="info-icon" />
                        <span>{fac.location}</span>
                      </div>

                      {fac.contact && (
                        <div className="facility-info-row">
                          <FiPhone size={15} className="info-icon" />
                          <a href={`tel:${fac.contact.replace(/\s+/g, '')}`} className="phone-link">
                            {fac.contact}
                          </a>
                        </div>
                      )}
                    </div>
                  </motion.div>
                ))}
              </div>
            ) : (
              <div className="empty-state">
                <FiArchive size={48} className="empty-icon" />
                <p>{t('storage.noResults', { defaultValue: 'No warehousing facilities found in this area.' })}</p>
              </div>
            )}
          </div>

          {/* AI Advisory Context Consultation */}
          <div className="ai-context-box-card">
            <button
              type="button"
              className="btn btn-secondary ai-ask-btn"
              onClick={handleAskStorageAdvisory}
              disabled={aiLoading}
            >
              <FiZap size={16} />
              <span>{aiLoading ? 'Connecting to AgriDarshak AI...' : t('storage.askAiBtn', { defaultValue: 'Ask AgriDarshak about storage temperature, moisture control & warehousing loans' })}</span>
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
