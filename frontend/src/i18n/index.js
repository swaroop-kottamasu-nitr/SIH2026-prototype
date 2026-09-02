import i18n from 'i18next'
import { initReactI18next } from 'react-i18next'
import en from '../locales/en.json'
import hi from '../locales/hi.json'
import te from '../locales/te.json'
import ta from '../locales/ta.json'
import bn from '../locales/bn.json'
import gu from '../locales/gu.json'
import mr from '../locales/mr.json'
import or from '../locales/or.json'

const LANG_KEY = 'app_language'

export const SUPPORTED_LANGS = [
  { code: 'en', label: 'English' },
  { code: 'hi', label: 'हिन्दी' },
  { code: 'te', label: 'తెలుగు' },
  { code: 'ta', label: 'தமிழ்' },
  { code: 'bn', label: 'বাংলা' },
  { code: 'gu', label: 'ગુજરાતી' },
  { code: 'mr', label: 'मराठी' },
  { code: 'or', label: 'ଓଡ଼ିଆ' },
]

export function getStoredLanguage() {
  return localStorage.getItem(LANG_KEY) || 'en'
}

export function setStoredLanguage(lang) {
  localStorage.setItem(LANG_KEY, lang)
}

/** Use for API calls: prefers current UI language (i18n) so generated content matches selected language. */
export function getEffectiveLanguage(user) {
  return i18n.language || user?.language || getStoredLanguage() || 'en'
}

i18n
  .use(initReactI18next)
  .init({
    resources: {
      en: { translation: en },
      hi: { translation: hi },
      te: { translation: te },
      ta: { translation: ta },
      bn: { translation: bn },
      gu: { translation: gu },
      mr: { translation: mr },
      or: { translation: or },
    },
    lng: getStoredLanguage(),
    fallbackLng: 'en',
    returnEmptyString: false,
    returnNull: false,
    interpolation: { escapeValue: false },
  })

export default i18n
