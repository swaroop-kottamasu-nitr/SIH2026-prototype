import { Link, useLocation } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import { FiMenu, FiX, FiLogOut, FiChevronDown } from 'react-icons/fi'
import { useState, useRef, useEffect } from 'react'
import { useTranslation } from 'react-i18next'
import axios from 'axios'
import i18n, { SUPPORTED_LANGS, setStoredLanguage, getStoredLanguage } from '../i18n'
import './AppLayout.css'

function AppLayout({ children, user, onLogout, onUserUpdate }) {
  const { t } = useTranslation()
  const location = useLocation()
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)
  const [toolsOpen, setToolsOpen] = useState(false)
  const dropdownRef = useRef(null)
  
  const currentLang = i18n.language || user?.language || (typeof window !== 'undefined' ? getStoredLanguage() || 'en' : 'en')

  // Close dropdown on outside click
  useEffect(() => {
    const handleOutsideClick = (e) => {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target)) {
        setToolsOpen(false)
      }
    }
    document.addEventListener('mousedown', handleOutsideClick)
    return () => document.removeEventListener('mousedown', handleOutsideClick)
  }, [])

  // Close menus on route change
  useEffect(() => {
    setMobileMenuOpen(false)
    setToolsOpen(false)
  }, [location.pathname])

  const handleLanguageChange = async (lang) => {
    if (user?.id && onUserUpdate) {
      try {
        const { data } = await axios.put(`/api/auth/user/${user.id}?language=${lang}`)
        onUserUpdate(data)
      } catch { /* ignore */ }
    }
    setStoredLanguage(lang)
    i18n.changeLanguage(lang)
  }

  const isActive = (path) => {
    if (path === '/dashboard') return location.pathname === '/dashboard'
    return location.pathname.startsWith(path)
  }

  const isToolsActive = ['/disease-detection', '/soil-analysis', '/crop-recommendation', '/irrigation', '/crop-rotation', '/inputs', '/storage', '/labour', '/schemes'].some(p => location.pathname.startsWith(p))

  return (
    <div className="app-layout">
      <header className="app-nav">
        <div className="nav-container">
          {/* 1. Brand Logo & Title */}
          <Link to="/dashboard" className="nav-brand" aria-label="AgriDarshak Dashboard">
            <img 
              src="/agridarshak-logo.jpeg" 
              alt="AgriDarshak" 
              className="brand-logo" 
            />
            <span className="brand-text">AgriDarshak</span>
          </Link>

          {/* 2. Responsive Desktop Navigation */}
          <nav className="nav-links" aria-label="Primary Navigation">
            <Link 
              to="/dashboard" 
              className={`nav-link ${isActive('/dashboard') ? 'active' : ''}`}
            >
              {t('nav.dashboard', { defaultValue: t('common.dashboard') })}
            </Link>

            <Link 
              to="/weather" 
              className={`nav-link ${isActive('/weather') ? 'active' : ''}`}
            >
              {t('nav.weather', { defaultValue: t('dashboard.liveWeather') })}
            </Link>

            <Link 
              to="/market-prices" 
              className={`nav-link ${isActive('/market-prices') ? 'active' : ''}`}
            >
              {t('nav.market', { defaultValue: t('dashboard.marketPrices') })}
            </Link>

            {/* Clean 'Tools' Dropdown to prevent navbar overflow */}
            <div className="nav-dropdown-wrapper" ref={dropdownRef}>
              <button
                type="button"
                className={`nav-link nav-dropdown-btn ${isToolsActive ? 'active' : ''}`}
                onClick={() => setToolsOpen(!toolsOpen)}
                aria-expanded={toolsOpen}
                aria-haspopup="true"
              >
                <span>{t('nav.tools', { defaultValue: 'Tools' })}</span>
                <FiChevronDown className={`dropdown-caret ${toolsOpen ? 'open' : ''}`} size={14} />
              </button>

              <AnimatePresence>
                {toolsOpen && (
                  <motion.div
                    className="nav-dropdown-menu"
                    initial={{ opacity: 0, y: 8, scale: 0.96 }}
                    animate={{ opacity: 1, y: 0, scale: 1 }}
                    exit={{ opacity: 0, y: 6, scale: 0.96 }}
                    transition={{ duration: 0.15 }}
                  >
                    <Link
                      to="/disease-detection"
                      className={`dropdown-item ${isActive('/disease-detection') ? 'active' : ''}`}
                      onClick={() => setToolsOpen(false)}
                    >
                      <span className="item-icon">🔬</span>
                      <div className="item-text">
                        <span className="item-title">{t('dashboard.diseaseDetection')}</span>
                        <span className="item-sub">{t('nav.disease', { defaultValue: 'Leaf Pathology AI' })}</span>
                      </div>
                    </Link>

                    <Link
                      to="/soil-analysis"
                      className={`dropdown-item ${isActive('/soil-analysis') ? 'active' : ''}`}
                      onClick={() => setToolsOpen(false)}
                    >
                      <span className="item-icon">🌱</span>
                      <div className="item-text">
                        <span className="item-title">{t('dashboard.soilAnalysis')}</span>
                        <span className="item-sub">{t('nav.soil', { defaultValue: 'NPK & pH Fertility' })}</span>
                      </div>
                    </Link>

                    <Link
                      to="/crop-recommendation"
                      className={`dropdown-item ${isActive('/crop-recommendation') ? 'active' : ''}`}
                      onClick={() => setToolsOpen(false)}
                    >
                      <span className="item-icon">🌾</span>
                      <div className="item-text">
                        <span className="item-title">{t('dashboard.cropRecommendation')}</span>
                        <span className="item-sub">{t('nav.crop', { defaultValue: 'Multi-Factor Advisory' })}</span>
                      </div>
                    </Link>

                    <Link
                      to="/irrigation"
                      className={`dropdown-item ${isActive('/irrigation') ? 'active' : ''}`}
                      onClick={() => setToolsOpen(false)}
                    >
                      <span className="item-icon">💧</span>
                      <div className="item-text">
                        <span className="item-title">{t('irrigation.title', { defaultValue: 'Irrigation Scheduler' })}</span>
                        <span className="item-sub">{t('nav.irrigation', { defaultValue: 'Precision Water Windows' })}</span>
                      </div>
                    </Link>

                    <Link
                      to="/crop-rotation"
                      className={`dropdown-item ${isActive('/crop-rotation') ? 'active' : ''}`}
                      onClick={() => setToolsOpen(false)}
                    >
                      <span className="item-icon">🔄</span>
                      <div className="item-text">
                        <span className="item-title">{t('crop_rotation.title', { defaultValue: 'Crop Rotation Planner' })}</span>
                        <span className="item-sub">{t('nav.crop_rotation', { defaultValue: 'Pest Break & Soil Vitality' })}</span>
                      </div>
                    </Link>

                    <Link
                      to="/inputs"
                      className={`dropdown-item ${isActive('/inputs') ? 'active' : ''}`}
                      onClick={() => setToolsOpen(false)}
                    >
                      <span className="item-icon">🛍️</span>
                      <div className="item-text">
                        <span className="item-title">{t('input.title', { defaultValue: 'Input Locator' })}</span>
                        <span className="item-sub">{t('nav.inputs', { defaultValue: 'Certified Seeds & Bio-Inputs' })}</span>
                      </div>
                    </Link>

                    <Link
                      to="/storage"
                      className={`dropdown-item ${isActive('/storage') ? 'active' : ''}`}
                      onClick={() => setToolsOpen(false)}
                    >
                      <span className="item-icon">🏢</span>
                      <div className="item-text">
                        <span className="item-title">{t('storage.title', { defaultValue: 'Storage Locator' })}</span>
                        <span className="item-sub">{t('nav.storage', { defaultValue: 'Cold Chains & Warehouses' })}</span>
                      </div>
                    </Link>

                    <Link
                      to="/labour"
                      className={`dropdown-item ${isActive('/labour') ? 'active' : ''}`}
                      onClick={() => setToolsOpen(false)}
                    >
                      <span className="item-icon">👥</span>
                      <div className="item-text">
                        <span className="item-title">{t('labour.title', { defaultValue: 'Labour Booking' })}</span>
                        <span className="item-sub">{t('nav.labour', { defaultValue: 'Farm Crews & Daily Labor' })}</span>
                      </div>
                    </Link>

                    <Link
                      to="/schemes"
                      className={`dropdown-item ${isActive('/schemes') ? 'active' : ''}`}
                      onClick={() => setToolsOpen(false)}
                    >
                      <span className="item-icon">🏛️</span>
                      <div className="item-text">
                        <span className="item-title">{t('scheme.title', { defaultValue: 'Government Schemes' })}</span>
                        <span className="item-sub">{t('nav.schemes', { defaultValue: 'Subsidies, KCC & PMFBY' })}</span>
                      </div>
                    </Link>
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
          </nav>

          {/* 3. Actions: Language + Farmer User Chip + Accessible Logout */}
          <div className="nav-actions">
            <div className="lang-selector">
              <span className="lang-icon" aria-hidden="true">🌐</span>
              <select
                className="lang-select"
                value={currentLang}
                onChange={(e) => handleLanguageChange(e.target.value)}
                aria-label={t('common.languageLabel')}
                title={t('dashboard.tip')}
              >
                {SUPPORTED_LANGS.map((l) => (
                  <option key={l.code} value={l.code}>{l.label}</option>
                ))}
              </select>
            </div>

            <div className="nav-farmer-chip" title={user?.location || ''}>
              <span className="farmer-chip-avatar">👨‍🌾</span>
              <span className="farmer-chip-name">{user?.name || t('dashboard.farmer')}</span>
            </div>

            <button 
              type="button"
              onClick={onLogout} 
              className="btn-nav-logout" 
              aria-label={t('common.logout')}
              title={t('common.logout')}
            >
              <FiLogOut size={15} />
              <span className="logout-text">{t('common.logout')}</span>
            </button>

            {/* Mobile Hamburger Button */}
            <button
              className="nav-toggle"
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              aria-label="Toggle menu"
              aria-expanded={mobileMenuOpen}
            >
              {mobileMenuOpen ? <FiX size={22} /> : <FiMenu size={22} />}
            </button>
          </div>
        </div>

        {/* 4. Mobile Drawer Menu */}
        <AnimatePresence>
          {mobileMenuOpen && (
            <motion.div
              className="nav-mobile"
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
              transition={{ duration: 0.2 }}
            >
              <Link
                to="/dashboard"
                className={`nav-mobile-link ${isActive('/dashboard') ? 'active' : ''}`}
                onClick={() => setMobileMenuOpen(false)}
              >
                🌾 {t('common.dashboard')}
              </Link>
              <Link
                to="/weather"
                className={`nav-mobile-link ${isActive('/weather') ? 'active' : ''}`}
                onClick={() => setMobileMenuOpen(false)}
              >
                🌧 {t('dashboard.liveWeather')}
              </Link>
              <Link
                to="/market-prices"
                className={`nav-mobile-link ${isActive('/market-prices') ? 'active' : ''}`}
                onClick={() => setMobileMenuOpen(false)}
              >
                📈 {t('dashboard.marketPrices')}
              </Link>
              <Link
                to="/disease-detection"
                className={`nav-mobile-link ${isActive('/disease-detection') ? 'active' : ''}`}
                onClick={() => setMobileMenuOpen(false)}
              >
                🔬 {t('dashboard.diseaseDetection')}
              </Link>
              <Link
                to="/soil-analysis"
                className={`nav-mobile-link ${isActive('/soil-analysis') ? 'active' : ''}`}
                onClick={() => setMobileMenuOpen(false)}
              >
                🌱 {t('dashboard.soilAnalysis')}
              </Link>
              <Link
                to="/crop-recommendation"
                className={`nav-mobile-link ${isActive('/crop-recommendation') ? 'active' : ''}`}
                onClick={() => setMobileMenuOpen(false)}
              >
                🌾 {t('dashboard.cropRecommendation')}
              </Link>
              <Link
                to="/irrigation"
                className={`nav-mobile-link ${isActive('/irrigation') ? 'active' : ''}`}
                onClick={() => setMobileMenuOpen(false)}
              >
                💧 {t('irrigation.title', { defaultValue: 'Irrigation Scheduler' })}
              </Link>
              <Link
                to="/crop-rotation"
                className={`nav-mobile-link ${isActive('/crop-rotation') ? 'active' : ''}`}
                onClick={() => setMobileMenuOpen(false)}
              >
                🔄 {t('crop_rotation.title', { defaultValue: 'Crop Rotation Planner' })}
              </Link>
              <Link
                to="/inputs"
                className={`nav-mobile-link ${isActive('/inputs') ? 'active' : ''}`}
                onClick={() => setMobileMenuOpen(false)}
              >
                🛍️ {t('input.title', { defaultValue: 'Input Locator' })}
              </Link>
              <Link
                to="/storage"
                className={`nav-mobile-link ${isActive('/storage') ? 'active' : ''}`}
                onClick={() => setMobileMenuOpen(false)}
              >
                🏢 {t('storage.title', { defaultValue: 'Storage Locator' })}
              </Link>
              <Link
                to="/labour"
                className={`nav-mobile-link ${isActive('/labour') ? 'active' : ''}`}
                onClick={() => setMobileMenuOpen(false)}
              >
                👥 {t('labour.title', { defaultValue: 'Labour Booking' })}
              </Link>
              <Link
                to="/schemes"
                className={`nav-mobile-link ${isActive('/schemes') ? 'active' : ''}`}
                onClick={() => setMobileMenuOpen(false)}
              >
                🏛️ {t('scheme.title', { defaultValue: 'Government Schemes' })}
              </Link>

              <div className="lang-selector-mobile">
                <span className="lang-label">🌐 {t('common.languageLabel')}</span>
                <select
                  className="lang-select-mobile"
                  value={currentLang}
                  onChange={(e) => handleLanguageChange(e.target.value)}
                >
                  {SUPPORTED_LANGS.map((l) => (
                    <option key={l.code} value={l.code}>{l.label}</option>
                  ))}
                </select>
              </div>

              <button 
                type="button"
                onClick={() => { onLogout(); setMobileMenuOpen(false); }} 
                className="nav-mobile-link nav-mobile-logout"
              >
                <FiLogOut size={16} /> {t('common.logout')}
              </button>
            </motion.div>
          )}
        </AnimatePresence>
      </header>

      <main className="app-main">
        {children}
      </main>
    </div>
  )
}

export default AppLayout
