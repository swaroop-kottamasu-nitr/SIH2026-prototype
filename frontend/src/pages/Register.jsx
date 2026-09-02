import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import axios from 'axios'
import { motion } from 'framer-motion'
import { SUPPORTED_LANGS } from '../i18n'
import './Auth.css'

function Register() {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    phone: '',
    location: 'Rourkela, Odisha',
    language: 'or'
  })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value })
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError('')
    try {
      await axios.post('/api/auth/register', formData)
      alert(t('auth.regSuccess'))
      navigate('/login')
    } catch (err) {
      const detail = err.response?.data?.detail
      const message = typeof detail === 'string'
        ? detail
        : Array.isArray(detail) && detail[0]?.msg
          ? detail[0].msg
          : t('auth.regFailed')
      setError(message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="auth-page">
      <motion.div
        className="auth-container"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4 }}
      >
        <div className="auth-card">
          <div className="auth-brand-header">
            <img src="/sih logo.jpeg" alt="AgriDarshak" className="auth-logo" />
            <span className="auth-brand-name">{t('brand')}</span>
          </div>
          <h1 className="auth-title">{t('auth.createAccountTitle')}</h1>
          <p className="auth-subtitle">{t('auth.createAccountSubtitle')}</p>

          {error && <div className="alert alert-danger">{error}</div>}

          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <label className="form-label">{t('auth.fullName')}</label>
              <input
                type="text"
                name="name"
                className="form-input"
                value={formData.name}
                onChange={handleChange}
                placeholder={t('auth.namePlaceholder')}
                required
              />
            </div>

            <div className="form-group">
              <label className="form-label">{t('auth.emailAddress')}</label>
              <input
                type="email"
                name="email"
                className="form-input"
                value={formData.email}
                onChange={handleChange}
                placeholder={t('auth.emailPlaceholder')}
                required
              />
            </div>

            <div className="form-group">
              <label className="form-label">{t('auth.phoneNumber')}</label>
              <input
                type="tel"
                name="phone"
                className="form-input"
                value={formData.phone}
                onChange={handleChange}
                placeholder={t('auth.phonePlaceholder')}
                required
              />
            </div>

            <div className="form-group">
              <label className="form-label">{t('auth.locationLabel')}</label>
              <input
                type="text"
                name="location"
                className="form-input"
                value={formData.location}
                onChange={handleChange}
                placeholder={t('auth.locationPlaceholder')}
                list="farmer-locations"
                required
              />
              <datalist id="farmer-locations">
                <option value="Rourkela, Odisha" />
                <option value="Sundargarh, Odisha" />
                <option value="Sambalpur, Odisha" />
                <option value="Bhubaneswar, Odisha" />
                <option value="Cuttack, Odisha" />
                <option value="Balasore, Odisha" />
                <option value="Berhampur, Odisha" />
                <option value="Koraput, Odisha" />
                <option value="Puri, Odisha" />
                <option value="Vijayawada, Andhra Pradesh" />
                <option value="Visakhapatnam, Andhra Pradesh" />
                <option value="Guntur, Andhra Pradesh" />
                <option value="Kurnool, Andhra Pradesh" />
              </datalist>
            </div>

            <div className="form-group">
              <label className="form-label">{t('auth.languageLabel')}</label>
              <select name="language" className="form-select" value={formData.language} onChange={handleChange}>
                {SUPPORTED_LANGS.map((lang) => (
                  <option key={lang.code} value={lang.code}>{lang.label}</option>
                ))}
              </select>
            </div>

            <button type="submit" className="btn btn-primary btn-block" disabled={loading}>
              {loading ? t('auth.creatingAccount') : t('auth.createAccountBtn')}
            </button>
          </form>

          <div className="auth-footer">
            <p>{t('auth.alreadyHaveAccount')} <Link to="/login">{t('auth.signIn')}</Link></p>
          </div>
        </div>
      </motion.div>
    </div>
  )
}

export default Register
