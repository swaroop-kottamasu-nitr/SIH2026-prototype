import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import axios from 'axios'
import { motion, AnimatePresence } from 'framer-motion'
import AppLayout from '../components/AppLayout'
import AdvisoryMarkdown from '../components/AdvisoryMarkdown'
import { 
  FiUsers, FiMapPin, FiCalendar, FiDollarSign, FiStar, 
  FiCheckCircle, FiAlertTriangle, FiZap, FiX, FiCheck, FiInfo, FiClock 
} from 'react-icons/fi'
import './LabourBooking.css'

const SKILLS = [
  { key: 'all', labelKey: 'labour.filter_all', defaultLabel: 'All Skills' },
  { key: 'harvesting', labelKey: 'labour.skill.harvesting', defaultLabel: 'Harvesting' },
  { key: 'irrigation', labelKey: 'labour.skill.irrigation', defaultLabel: 'Irrigation' },
  { key: 'pesticide', labelKey: 'labour.skill.pesticide', defaultLabel: 'Pesticide Spraying' },
  { key: 'planting', labelKey: 'labour.skill.planting', defaultLabel: 'Planting & Sowing' },
  { key: 'weeding', labelKey: 'labour.skill.weeding', defaultLabel: 'Weeding' },
  { key: 'fertilizer', labelKey: 'labour.skill.fertilizer', defaultLabel: 'Fertilizer Application' }
]

export default function LabourBooking({ user, onLogout, onUserUpdate }) {
  const { t } = useTranslation()
  const [skillFilter, setSkillFilter] = useState('all')
  const [workers, setWorkers] = useState([])
  const [loading, setLoading] = useState(false)

  // Booking modal states
  const [selectedWorker, setSelectedWorker] = useState(null)
  const [bookingDate, setBookingDate] = useState(new Date().toISOString().split('T')[0])
  const [durationDays, setDurationDays] = useState(1)
  const [taskDescription, setTaskDescription] = useState('')
  const [contactPhone, setContactPhone] = useState(user?.phone || '')
  const [bookingLoading, setBookingLoading] = useState(false)
  const [bookingResult, setBookingResult] = useState(null)

  // Minimal AI Advisory Integration
  const [aiLoading, setAiLoading] = useState(false)
  const [aiAdvisory, setAiAdvisory] = useState(null)

  const fetchWorkers = async (skill) => {
    setLoading(true)
    try {
      const res = await axios.get('/api/v1/labour/available', {
        params: { 
          skill: skill === 'all' ? undefined : skill,
          language: getEffectiveLanguage(user)
        }
      })
      if (res.data?.workers) {
        setWorkers(res.data.workers)
      }
    } catch (err) {
      console.error('Fetch workers error:', err)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchWorkers('all')
  }, [i18n.language, user?.language])

  const handleOpenBooking = (worker) => {
    setSelectedWorker(worker)
    setBookingResult(null)
    setTaskDescription(`Farm assistance for ${worker.skills.slice(0, 2).join(', ')}`)
  }

  const handleSubmitBooking = async (e) => {
    e.preventDefault()
    if (!selectedWorker) return
    setBookingLoading(true)
    try {
      const res = await axios.post('/api/v1/labour/request', {
        worker_id: selectedWorker.id,
        date: bookingDate,
        duration_days: parseInt(durationDays) || 1,
        task_description: taskDescription,
        location: user?.location || 'Vijayawada, Andhra Pradesh',
        contact_phone: contactPhone,
        language: getEffectiveLanguage(user)
      })
      if (res.data) {
        setBookingResult(res.data)
      }
    } catch (err) {
      console.error('Booking request error:', err)
    } finally {
      setBookingLoading(false)
    }
  }

  const handleAskLabourAdvisory = async () => {
    if (aiLoading) return
    setAiLoading(true)
    try {
      const prompt = `Agricultural labour management and prevailing daily wage rates in ${user?.location || 'Andhra Pradesh'}. What are standard farm operation labor requirements for current season?`
      const res = await axios.post('/api/v1/advisory', {
        question: prompt,
        language: getEffectiveLanguage(user),
        context: {
          location: user?.location
        }
      }, { timeout: 15000 })
      if (res.data?.advisory) {
        setAiAdvisory(res.data.advisory)
      }
    } catch (err) {
      console.error('Labour advisory error:', err)
    } finally {
      setAiLoading(false)
    }
  }

  return (
    <AppLayout user={user} onLogout={onLogout} onUserUpdate={onUserUpdate}>
      <div className="labour-page">
        <div className="container">
          
          {/* Warning Banner */}
          <div className="demo-disclaimer-banner">
            <FiAlertTriangle size={18} className="banner-icon" />
            <span>{t('labour.demo_disclaimer', { defaultValue: 'This is demonstration data. Actual labour availability may vary.' })}</span>
          </div>

          {/* Header */}
          <div className="labour-header">
            <div className="labour-title-box">
              <div className="labour-icon-badge">
                <FiUsers size={26} />
              </div>
              <div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', flexWrap: 'wrap' }}>
                  <h1 className="labour-title">{t('labour.title', { defaultValue: 'Farm Labour Booking' })}</h1>
                  <span className="demo-badge">
                    📋 {t('labour.demo_badge', { defaultValue: 'DEMO DATA' })}
                  </span>
                </div>
                <p className="labour-subtitle">
                  {t('labour.subtitle', { defaultValue: 'Connect with available local farm workers and specialized harvest teams' })}
                </p>
              </div>
            </div>
          </div>

          {/* Skill Filter Pills */}
          <div className="filter-card">
            <label className="filter-label">{t('labour.filter_by_skill', { defaultValue: 'Filter by Required Skill:' })}</label>
            <div className="skill-pills-row">
              {SKILLS.map(s => (
                <button
                  key={s.key}
                  type="button"
                  className={`skill-pill-btn ${skillFilter === s.key ? 'active' : ''}`}
                  onClick={() => { setSkillFilter(s.key); fetchWorkers(s.key); }}
                >
                  {t(s.labelKey, { defaultValue: s.defaultLabel })}
                </button>
              ))}
            </div>
          </div>

          {/* Workers Grid */}
          <div className="workers-section">
            <div className="section-header-bar">
              <span className="section-count">
                {workers.length} {t('labour.available_workers', { defaultValue: 'available workers & crews listed' })}
              </span>
            </div>

            {loading ? (
              <div className="loading-state">{t('common.loading', { defaultValue: 'Loading available workers...' })}</div>
            ) : workers.length > 0 ? (
              <div className="workers-grid">
                {workers.map((w, idx) => (
                  <motion.div
                    key={w.id}
                    className="worker-card"
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: idx * 0.04 }}
                  >
                    <div className="worker-card-header">
                      <div>
                        <span className="worker-name">{w.name}</span>
                        <div className="worker-rating-row">
                          <FiStar size={13} className="star-icon" />
                          <span className="rating-val">{w.rating || 4.8}</span>
                          <span className={`avail-tag avail-${w.availability}`}>
                            {w.availability === 'available' ? '● ' + t('labour.available', { defaultValue: 'Available' }) : '◐ ' + t('labour.limited', { defaultValue: 'Limited' })}
                          </span>
                        </div>
                      </div>
                      <div className="wage-badge">
                        ₹{w.daily_wage}<span>/day</span>
                      </div>
                    </div>

                    <div className="worker-card-body">
                      <div className="worker-info-row">
                        <FiMapPin size={15} className="info-icon" />
                        <span>{w.location}</span>
                      </div>

                      <div className="skills-tag-group">
                        {w.skills.map((sk, i) => (
                          <span key={i} className="skill-tag">
                            {t(`labour.skill.${sk}`, { defaultValue: sk })}
                          </span>
                        ))}
                      </div>

                      <button
                        type="button"
                        className="btn btn-primary book-btn"
                        onClick={() => handleOpenBooking(w)}
                      >
                        {t('labour.book_now', { defaultValue: 'Book Worker' })}
                      </button>
                    </div>
                  </motion.div>
                ))}
              </div>
            ) : (
              <div className="empty-state">
                <FiUsers size={48} className="empty-icon" />
                <p>{t('labour.noWorkers', { defaultValue: 'No worker listings match the selected skill category.' })}</p>
              </div>
            )}
          </div>

          {/* Booking Modal */}
          <AnimatePresence>
            {selectedWorker && (
              <div className="modal-backdrop" onClick={() => setSelectedWorker(null)}>
                <motion.div
                  className="booking-modal-card"
                  onClick={(e) => e.stopPropagation()}
                  initial={{ opacity: 0, scale: 0.95, y: 15 }}
                  animate={{ opacity: 1, scale: 1, y: 0 }}
                  exit={{ opacity: 0, scale: 0.95, y: 15 }}
                >
                  <div className="modal-header">
                    <div className="modal-title-box">
                      <h3 className="modal-title">🌾 {t('labour.booking_request', { defaultValue: 'Labour Booking Request' })}</h3>
                      <p className="modal-subtitle">Candidate: <strong>{selectedWorker.name}</strong> (₹{selectedWorker.daily_wage}/day)</p>
                    </div>
                    <button type="button" className="close-btn" onClick={() => setSelectedWorker(null)}>
                      <FiX size={20} />
                    </button>
                  </div>

                  {bookingResult ? (
                    <div className="modal-success-body">
                      <div className="success-icon-box">
                        <FiCheck size={32} />
                      </div>
                      <h4 className="success-title">{t('labour.request_confirmed', { defaultValue: 'Demo Booking Registered' })}</h4>
                      <p className="success-text">{bookingResult.message}</p>
                      <div className="demo-notice-box">
                        <FiInfo size={16} />
                        <span>{bookingResult.demo_notice}</span>
                      </div>
                      <button
                        type="button"
                        className="btn btn-primary"
                        style={{ marginTop: 'var(--space-4)', width: '100%' }}
                        onClick={() => setSelectedWorker(null)}
                      >
                        {t('common.done', { defaultValue: 'Close' })}
                      </button>
                    </div>
                  ) : (
                    <form onSubmit={handleSubmitBooking} className="modal-form">
                      <div className="form-group">
                        <label className="form-label">{t('labour.date', { defaultValue: 'Work Date' })}</label>
                        <input
                          type="date"
                          className="form-input"
                          value={bookingDate}
                          onChange={(e) => setBookingDate(e.target.value)}
                          required
                        />
                      </div>

                      <div className="form-group">
                        <label className="form-label">{t('labour.duration_days', { defaultValue: 'Duration (Days)' })}</label>
                        <input
                          type="number"
                          className="form-input"
                          value={durationDays}
                          onChange={(e) => setDurationDays(e.target.value)}
                          min="1"
                          max="30"
                          required
                        />
                      </div>

                      <div className="form-group">
                        <label className="form-label">{t('labour.task_description', { defaultValue: 'Task Description' })}</label>
                        <textarea
                          className="form-input"
                          rows="3"
                          value={taskDescription}
                          onChange={(e) => setTaskDescription(e.target.value)}
                          placeholder="e.g. 2-day chilli harvesting and field cleaning"
                          required
                        />
                      </div>

                      <div className="form-group">
                        <label className="form-label">{t('labour.contact_phone', { defaultValue: 'Your Contact Phone' })}</label>
                        <input
                          type="text"
                          className="form-input"
                          value={contactPhone}
                          onChange={(e) => setContactPhone(e.target.value)}
                          placeholder="+91 98765 43210"
                        />
                      </div>

                      <div className="modal-actions">
                        <button
                          type="button"
                          className="btn btn-secondary"
                          onClick={() => setSelectedWorker(null)}
                        >
                          {t('common.cancel', { defaultValue: 'Cancel' })}
                        </button>
                        <button
                          type="submit"
                          className="btn btn-primary"
                          disabled={bookingLoading}
                        >
                          {bookingLoading ? t('common.submitting', { defaultValue: 'Submitting...' }) : t('labour.submit_request', { defaultValue: 'Submit Demo Booking' })}
                        </button>
                      </div>
                    </form>
                  )}
                </motion.div>
              </div>
            )}
          </AnimatePresence>

          {/* AI Advisory Context Consultation */}
          <div className="ai-context-box-card">
            <button
              type="button"
              className="btn btn-secondary ai-ask-btn"
              onClick={handleAskLabourAdvisory}
              disabled={aiLoading}
            >
              <FiZap size={16} />
              <span>{aiLoading ? 'Connecting to AgriDarshak AI...' : t('labour.askAiBtn', { defaultValue: 'Ask AgriDarshak about seasonal labour requirements & wages' })}</span>
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
