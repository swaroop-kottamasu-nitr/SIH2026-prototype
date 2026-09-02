import { useState, useCallback, useEffect } from 'react'
import { useTranslation } from 'react-i18next'
import { FiVolume2, FiSquare, FiRotateCw } from 'react-icons/fi'
import './TextToSpeech.css'

/** Maps our language codes to priority list of Web Speech API lang codes */
const LANG_SPEECH_TAGS = {
  en: ['en-IN', 'en-US', 'en-GB', 'en'],
  hi: ['hi-IN', 'hi'],
  ta: ['ta-IN', 'ta'],
  te: ['te-IN', 'te'],
  bn: ['bn-IN', 'bn-BD', 'bn'],
  mr: ['mr-IN', 'mr'],
  gu: ['gu-IN', 'gu'],
  or: ['or-IN', 'od-IN', 'or', 'od', 'hi-IN', 'en-IN'],
}

/** Strip markdown for plain-text TTS */
function stripMarkdown(text) {
  if (!text || typeof text !== 'string') return ''
  return text
    .replace(/^##\s+/gm, '')
    .replace(/^#\s+/gm, '')
    .replace(/\*\*(.+?)\*\*/g, '$1')
    .replace(/\*(.+?)\*/g, '$1')
    .replace(/^-\s+/gm, '')
    .replace(/^\d+\.\s+/gm, '')
    .replace(/\[(.+?)\]\(.+?\)/g, '$1')
    .replace(/[`_~]/g, '')
    .replace(/\n+/g, '. ')
    .trim()
}

function TextToSpeech({ text, language = 'en', className = '' }) {
  const { t } = useTranslation()
  const [speaking, setSpeaking] = useState(false)
  const [hasPlayedOnce, setHasPlayedOnce] = useState(false)
  const [odiaFallbackActive, setOdiaFallbackActive] = useState(false)

  // Check voice availability on mount or voice list change
  useEffect(() => {
    if (typeof window === 'undefined' || !window.speechSynthesis) return

    const checkOdiaSupport = () => {
      if (language === 'or' || language === 'od') {
        const voices = window.speechSynthesis.getVoices()
        const hasNativeOdia = voices.some(v => {
          const l = (v.lang || '').toLowerCase()
          return l.includes('or-in') || l.includes('od-in') || l === 'or' || l === 'od'
        })
        setOdiaFallbackActive(!hasNativeOdia)
      } else {
        setOdiaFallbackActive(false)
      }
    }

    checkOdiaSupport()
    if (window.speechSynthesis.onvoiceschanged !== undefined) {
      window.speechSynthesis.onvoiceschanged = checkOdiaSupport
    }

    return () => {
      if (typeof window !== 'undefined' && window.speechSynthesis) {
        window.speechSynthesis.cancel()
      }
    }
  }, [language])

  const speakText = useCallback(() => {
    if (!text || typeof text !== 'string') return
    if (typeof window === 'undefined' || !window.speechSynthesis) {
      console.warn('Speech synthesis not supported')
      return
    }

    const plainText = stripMarkdown(text)
    if (!plainText) return

    window.speechSynthesis.cancel()

    const utterance = new SpeechSynthesisUtterance(plainText)
    const candidateTags = LANG_SPEECH_TAGS[language] || ['en-IN', 'en-US']
    utterance.lang = candidateTags[0]

    // Select the best available browser voice for this language
    const voices = window.speechSynthesis.getVoices()
    if (voices && voices.length > 0) {
      for (const tag of candidateTags) {
        const matchingVoice = voices.find(v => {
          const vLang = (v.lang || '').toLowerCase()
          const target = tag.toLowerCase()
          return vLang === target || vLang.startsWith(target.split('-')[0])
        })
        if (matchingVoice) {
          utterance.voice = matchingVoice
          utterance.lang = matchingVoice.lang
          break
        }
      }
    }

    utterance.rate = 0.9
    utterance.pitch = 1
    utterance.volume = 1

    utterance.onstart = () => {
      setSpeaking(true)
      setHasPlayedOnce(true)
    }
    utterance.onend = () => setSpeaking(false)
    utterance.onerror = () => setSpeaking(false)

    window.speechSynthesis.speak(utterance)
  }, [text, language])

  const handlePlay = useCallback(() => {
    speakText()
  }, [speakText])

  const handleStop = useCallback(() => {
    if (typeof window !== 'undefined' && window.speechSynthesis) {
      window.speechSynthesis.cancel()
    }
    setSpeaking(false)
  }, [])

  const handleReplay = useCallback(() => {
    speakText()
  }, [speakText])

  if (!text || typeof text !== 'string') return null

  return (
    <div className={`tts-voice-control-group ${className}`}>
      {!speaking ? (
        <div className="tts-actions-idle">
          <button
            type="button"
            className="tts-btn tts-btn-play"
            onClick={handlePlay}
            title={t('voiceMode.listen', { defaultValue: 'Listen to Advisory' })}
            aria-label={t('voiceMode.listen', { defaultValue: 'Listen to Advisory' })}
          >
            <FiVolume2 size={16} aria-hidden />
            <span>{t('voiceMode.listen', { defaultValue: 'Listen to Advisory' })}</span>
          </button>

          {hasPlayedOnce && (
            <button
              type="button"
              className="tts-btn tts-btn-replay-subtle"
              onClick={handleReplay}
              title={t('voiceMode.replay', { defaultValue: 'Replay' })}
              aria-label={t('voiceMode.replay', { defaultValue: 'Replay' })}
            >
              <FiRotateCw size={14} aria-hidden />
              <span>{t('voiceMode.replay', { defaultValue: 'Replay' })}</span>
            </button>
          )}
        </div>
      ) : (
        <div className="tts-actions-speaking">
          <div className="tts-speaking-pulse">
            <span className="speaking-indicator-dot"></span>
            <span className="speaking-status-text">{t('voiceMode.speaking', { defaultValue: 'Speaking Advisory...' })}</span>
          </div>

          <div className="tts-active-buttons">
            <button
              type="button"
              className="tts-btn tts-btn-stop"
              onClick={handleStop}
              title={t('voiceMode.stop', { defaultValue: 'Stop' })}
              aria-label={t('voiceMode.stop', { defaultValue: 'Stop' })}
            >
              <FiSquare size={14} aria-hidden />
              <span>{t('voiceMode.stop', { defaultValue: 'Stop' })}</span>
            </button>

            <button
              type="button"
              className="tts-btn tts-btn-replay"
              onClick={handleReplay}
              title={t('voiceMode.replay', { defaultValue: 'Replay' })}
              aria-label={t('voiceMode.replay', { defaultValue: 'Replay' })}
            >
              <FiRotateCw size={14} aria-hidden />
              <span>{t('voiceMode.replay', { defaultValue: 'Replay' })}</span>
            </button>
          </div>
        </div>
      )}

      {/* Graceful Odia Regional Notice */}
      {odiaFallbackActive && (
        <div className="tts-fallback-note" title={t('voiceMode.odiaVoiceNotice')}>
          <span className="note-icon">ℹ️</span>
          <span>{t('voiceMode.odiaVoiceNotice')}</span>
        </div>
      )}
    </div>
  )
}

export default TextToSpeech
