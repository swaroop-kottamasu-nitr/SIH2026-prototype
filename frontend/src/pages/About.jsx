import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import { useTranslation } from 'react-i18next'
import { FiTarget, FiUsers, FiCpu, FiHeart } from 'react-icons/fi'
import i18n, { SUPPORTED_LANGS, setStoredLanguage } from '../i18n'
import './Landing.css'

function About() {
  const { t } = useTranslation()
  const currentLang = typeof window !== 'undefined' ? localStorage.getItem('app_language') || 'en' : 'en'

  return (
    <div className="landing">
      <div className="landing-bg" aria-hidden="true" />

      <header className="landing-header">
        <div className="container">
          <div className="header-inner">
            <Link to="/" className="logo" style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <img src="/agridarshak-logo.jpeg" alt="AgriDarshak" style={{ width: 28, height: 28, borderRadius: 6, objectFit: 'cover' }} />
              <span>{t('brand')}</span>
            </Link>
            <nav className="header-nav">
              <select className="lang-select-inline" value={currentLang} onChange={(e) => { setStoredLanguage(e.target.value); i18n.changeLanguage(e.target.value); }} aria-label={t('common.language')}>
                {SUPPORTED_LANGS.map((l) => <option key={l.code} value={l.code}>{l.label}</option>)}
              </select>
              <Link to="/" className="btn btn-secondary">{t('nav.home')}</Link>
              <Link to="/login" className="btn btn-secondary">{t('nav.login')}</Link>
              <Link to="/register" className="btn btn-primary">{t('nav.getStarted')}</Link>
            </nav>
          </div>
        </div>
      </header>

      <section className="about-content" style={{ padding: 'var(--space-16) 0', maxWidth: 720, margin: '0 auto' }}>
        <div className="container">
          <motion.div
            initial={{ opacity: 0, y: 24 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
          >
            <h1 className="hero-title" style={{ marginBottom: 'var(--space-6)' }}>{t('about.title')}</h1>
            <p className="hero-subtitle" style={{ marginBottom: 'var(--space-8)' }}>
              {t('about.subtitle')}
            </p>

            <div className="about-sections" style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-8)' }}>
              <div className="about-card">
                <FiTarget size={28} style={{ color: 'var(--color-primary)', marginBottom: 'var(--space-3)' }} />
                <h2 style={{ fontSize: 'var(--text-xl)', marginBottom: 'var(--space-2)' }}>{t('about.purposeTitle')}</h2>
                <p style={{ color: 'var(--color-text-secondary)', lineHeight: 1.7 }}>
                  {t('about.purposeDesc')}
                </p>
              </div>

              <div className="about-card">
                <FiUsers size={28} style={{ color: 'var(--color-primary)', marginBottom: 'var(--space-3)' }} />
                <h2 style={{ fontSize: 'var(--text-xl)', marginBottom: 'var(--space-2)' }}>{t('about.howItHelpsTitle')}</h2>
                <ul style={{ color: 'var(--color-text-secondary)', lineHeight: 1.8, paddingLeft: 'var(--space-6)' }}>
                  <li>{t('about.helpPoint1')}</li>
                  <li>{t('about.helpPoint2')}</li>
                  <li>{t('about.helpPoint3')}</li>
                  <li>{t('about.helpPoint4')}</li>
                  <li>{t('about.helpPoint5')}</li>
                  <li>{t('about.helpPoint6')}</li>
                  <li>{t('about.helpPoint7')}</li>
                </ul>
              </div>

              <div className="about-card">
                <FiCpu size={28} style={{ color: 'var(--color-primary)', marginBottom: 'var(--space-3)' }} />
                <h2 style={{ fontSize: 'var(--text-xl)', marginBottom: 'var(--space-2)' }}>{t('about.techTitle')}</h2>
                <p style={{ color: 'var(--color-text-secondary)', lineHeight: 1.7 }}>
                  {t('about.techDesc')}
                </p>
              </div>

              <div className="about-card support-card">
                <FiHeart size={28} style={{ color: 'var(--color-primary)', marginBottom: 'var(--space-3)' }} />
                <h2 style={{ fontSize: 'var(--text-xl)', marginBottom: 'var(--space-2)' }}>{t('about.supportTitle')}</h2>
                <p style={{ color: 'var(--color-text-secondary)', lineHeight: 1.7, fontWeight: 500 }}>
                  {t('about.supportDesc')}
                </p>
              </div>
            </div>

            <div style={{ marginTop: 'var(--space-12)', textAlign: 'center' }}>
              <Link to="/register" className="btn btn-primary btn-lg">{t('landing.createAccount')}</Link>
            </div>
          </motion.div>
        </div>
      </section>

      <footer className="landing-footer">
        <div className="container">
          <p>{t('landing.copyright')}</p>
        </div>
      </footer>
    </div>
  )
}

export default About
