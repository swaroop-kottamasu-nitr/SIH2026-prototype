import { useState, useEffect, useRef } from 'react'
import { Link } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import axios from 'axios'
import { motion, AnimatePresence } from 'framer-motion'
import AppLayout from '../components/AppLayout'
import AdvisoryMarkdown from '../components/AdvisoryMarkdown'
import { 
  FiMessageSquare, FiSend, FiMic, FiMicOff, FiVolume2, 
  FiVolumeX, FiAlertCircle, FiZap, FiRefreshCw, FiUser, FiInfo 
} from 'react-icons/fi'
import './Chatbot.css'

const SPEECH_LANG_MAP = {
  en: 'en-US',
  hi: 'hi-IN',
  or: 'or-IN',
  te: 'te-IN',
  ta: 'ta-IN',
  bn: 'bn-IN',
  gu: 'gu-IN',
  mr: 'mr-IN'
}

export default function Chatbot({ user, onLogout, onUserUpdate }) {
  const { t, i18n } = useTranslation()
  const currentLang = i18n.language || user?.language || 'en'

  const [messages, setMessages] = useState([])
  const [inputText, setInputText] = useState('')
  const [loading, setLoading] = useState(false)
  const [isListening, setIsListening] = useState(false)
  const [speechError, setSpeechError] = useState(null)
  const [speakingId, setSpeakingId] = useState(null)
  const [isSpeechSupported, setIsSpeechSupported] = useState(true)
  const [isTtsSupported, setIsTtsSupported] = useState(true)

  const messagesEndRef = useRef(null)
  const recognitionRef = useRef(null)

  // Initialize Speech Recognition & TTS availability
  useEffect(() => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition
    if (!SpeechRecognition) {
      setIsSpeechSupported(false)
    }
    if (!('speechSynthesis' in window)) {
      setIsTtsSupported(false)
    }

    // Set initial welcome message
    const welcomeMsg = {
      id: 'msg_welcome',
      role: 'assistant',
      content: t('chat.welcome_message', {
        defaultValue: 'Namaste! I am AgriDarshak Assistant. Ask me about your crop, soil, weather, irrigation, markets or government support.'
      }),
      timestamp: new Date(),
      source: 'gemini'
    }
    setMessages(prev => (prev.length <= 1 ? [welcomeMsg] : prev))
  }, [i18n.language, user?.language, t])

  // Auto-scroll on new messages
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, loading])

  // Context-aware suggested questions
  const getSuggestedQuestions = () => {
    if (user?.crop || user?.location) {
      return [
        { key: 'farm_health', text: t('chat.suggested.farm_health', { defaultValue: 'How is my farm health score doing?' }) },
        { key: 'irrigate', text: t('chat.suggested.irrigate', { defaultValue: 'Should I irrigate my crops today?' }) },
        { key: 'today', text: t('chat.suggested.today', { defaultValue: 'What are my top priority actions today?' }) },
        { key: 'sell', text: t('chat.suggested.sell', { defaultValue: 'What are the prevailing mandi prices for my crop?' }) },
        { key: 'schemes', text: t('chat.suggested.schemes', { defaultValue: 'What government subsidies apply to my farm?' }) },
        { key: 'soil', text: t('chat.suggested.soil', { defaultValue: 'How can I improve my soil nutrient balance?' }) }
      ]
    }
    return [
      { key: 'crops', text: t('chat.suggested.crops', { defaultValue: 'What crops grow best in this season?' }) },
      { key: 'soil', text: t('chat.suggested.soil', { defaultValue: 'How do I test my soil health?' }) },
      { key: 'schemes', text: t('chat.suggested.schemes', { defaultValue: 'What government schemes are available for farmers?' }) },
      { key: 'irrigate', text: t('chat.suggested.irrigate', { defaultValue: 'How to optimize irrigation scheduling?' }) }
    ]
  }

  // Handle Send Message
  const handleSendMessage = async (textToSend) => {
    const text = (textToSend || inputText).trim()
    if (!text || loading) return

    setSpeechError(null)

    const userMsg = {
      id: `usr_${Date.now()}`,
      role: 'user',
      content: text,
      timestamp: new Date()
    }

    setMessages(prev => [...prev, userMsg])
    setInputText('')
    setLoading(true)

    try {
      const res = await axios.post('/api/v1/chat', {
        message: text,
        language: currentLang,
        context: {
          crop: user?.crop || 'Chilli',
          location: user?.location || 'Vijayawada, Andhra Pradesh',
          soil_type: user?.soil_type || 'Black Soil'
        }
      }, { timeout: 16000 })

      const assistantMsg = {
        id: `asst_${Date.now()}`,
        role: 'assistant',
        content: res.data?.response || t('chat.error.general', { defaultValue: 'Unable to retrieve guidance right now. Please try again.' }),
        source: res.data?.source || 'fallback',
        timestamp: new Date()
      }

      setMessages(prev => [...prev, assistantMsg])
    } catch (err) {
      console.error('Chat error:', err)
      const errorMsg = {
        id: `err_${Date.now()}`,
        role: 'assistant',
        content: t('chat.error.general', { defaultValue: 'AgriDarshak advisory service encountered a connection issue. Please check your network or try again.' }),
        source: 'fallback',
        timestamp: new Date()
      }
      setMessages(prev => [...prev, errorMsg])
    } finally {
      setLoading(false)
    }
  }

  // Web Speech API Voice Recognition
  const handleToggleVoiceInput = () => {
    setSpeechError(null)
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition

    if (!SpeechRecognition) {
      setSpeechError(t('chat.error.unsupported_browser', { defaultValue: 'Voice input is not supported on this browser.' }))
      return
    }

    if (isListening) {
      recognitionRef.current?.stop()
      setIsListening(false)
      return
    }

    try {
      const recognition = new SpeechRecognition()
      recognitionRef.current = recognition
      recognition.continuous = false
      recognition.interimResults = false

      const targetLocale = SPEECH_LANG_MAP[currentLang] || 'en-US'
      recognition.lang = targetLocale

      recognition.onstart = () => {
        setIsListening(true)
        setSpeechError(null)
      }

      recognition.onresult = (event) => {
        const transcript = event.results[0][0].transcript
        if (transcript) {
          // Populate input field for user review and editing
          setInputText(prev => (prev ? `${prev} ${transcript}` : transcript))
        }
        setIsListening(false)
      }

      recognition.onerror = (event) => {
        setIsListening(false)
        if (event.error === 'not-allowed' || event.error === 'permission-denied') {
          setSpeechError(t('chat.error.permission_denied', { defaultValue: 'Microphone permission denied. Please allow microphone access in browser settings.' }))
        } else if (event.error === 'no-speech') {
          setSpeechError(t('chat.error.no_speech', { defaultValue: 'No speech detected. Please try speaking again.' }))
        } else if (event.error === 'language-not-supported') {
          // Fallback to English locale
          recognition.lang = 'en-IN'
          setSpeechError(t('chat.error.unsupported_language', { defaultValue: 'Voice recognition locale fallback activated. Try speaking in English or Hindi.' }))
        } else {
          setSpeechError(t('chat.error.recognition_error', { defaultValue: 'Voice recognition error. Please type your question.' }))
        }
      }

      recognition.onend = () => {
        setIsListening(false)
      }

      recognition.start()
    } catch (err) {
      console.error('Speech recognition init error:', err)
      setIsListening(false)
      setSpeechError(t('chat.error.recognition_error', { defaultValue: 'Voice recognition error. Please type your question.' }))
    }
  }

  // Web Speech API Text-to-Speech (TTS)
  const handleToggleTts = (msgId, text) => {
    if (!('speechSynthesis' in window)) return

    if (speakingId === msgId) {
      window.speechSynthesis.cancel()
      setSpeakingId(null)
      return
    }

    window.speechSynthesis.cancel()
    
    // Clean markdown headings/stars for natural speech
    const cleanText = text
      .replace(/[#*`_~]/g, '')
      .replace(/\[.*?\]\(.*?\)/g, '')
      .trim()

    const utterance = new SpeechSynthesisUtterance(cleanText)
    const targetLocale = SPEECH_LANG_MAP[currentLang] || 'en-US'
    utterance.lang = targetLocale
    utterance.rate = 0.95

    utterance.onend = () => {
      setSpeakingId(null)
    }

    utterance.onerror = () => {
      setSpeakingId(null)
    }

    setSpeakingId(msgId)
    window.speechSynthesis.speak(utterance)
  }

  // Clear chat session
  const handleClearChat = () => {
    if (window.speechSynthesis) window.speechSynthesis.cancel()
    setSpeakingId(null)
    setMessages([{
      id: 'msg_welcome',
      role: 'assistant',
      content: t('chat.welcome_message', {
        defaultValue: 'Namaste! I am AgriDarshak Assistant. Ask me about your crop, soil, weather, irrigation, markets or government support.'
      }),
      timestamp: new Date(),
      source: 'gemini'
    }])
  }

  return (
    <AppLayout user={user} onLogout={onLogout} onUserUpdate={onUserUpdate}>
      <div className="chat-page">
        <div className="container chat-layout-container">
          
          {/* Header */}
          <div className="chat-header-card">
            <div className="chat-title-box">
              <div className="chat-icon-badge">
                <FiMessageSquare size={24} />
              </div>
              <div>
                <h1 className="chat-title">{t('chat.title', { defaultValue: 'AgriDarshak AI Assistant' })}</h1>
                <p className="chat-subtitle">
                  {t('chat.subtitle', { defaultValue: 'Multilingual conversational decision support & voice advisory for Indian farmers' })}
                </p>
              </div>
            </div>

            <button
              type="button"
              className="btn-chat-reset"
              onClick={handleClearChat}
              title={t('chat.reset', { defaultValue: 'Reset Chat' })}
            >
              <FiRefreshCw size={14} />
              <span>{t('chat.reset', { defaultValue: 'New Chat' })}</span>
            </button>
          </div>

          {/* Voice Error Notice */}
          <AnimatePresence>
            {speechError && (
              <motion.div
                className="speech-error-notice"
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -10 }}
              >
                <FiAlertCircle size={16} />
                <span>{speechError}</span>
              </motion.div>
            )}
          </AnimatePresence>

          {/* Chat Messages Container */}
          <div className="chat-messages-container">
            {messages.map((m) => {
              const isUser = m.role === 'user'
              const isSpeaking = speakingId === m.id
              return (
                <div key={m.id} className={`chat-message-row ${isUser ? 'row-user' : 'row-assistant'}`}>
                  <div className={`chat-bubble ${isUser ? 'bubble-user' : 'bubble-assistant'}`}>
                    <div className="bubble-top-bar">
                      <span className="bubble-author">
                        {isUser ? `👨‍🌾 ${user?.name || 'Farmer'}` : '🌾 AgriDarshak AI'}
                      </span>
                      {!isUser && m.source && (
                        <span className={`source-tag ${m.source === 'gemini' ? 'source-gemini' : 'source-fallback'}`}>
                          {m.source === 'gemini' ? '✨ Gemini AI' : '📋 Rule Guidance'}
                        </span>
                      )}
                    </div>

                    <div className="bubble-content">
                      {isUser ? (
                        <p className="user-text">{m.content}</p>
                      ) : (
                        <AdvisoryMarkdown content={m.content} language={currentLang} source={m.source || 'ai'} />
                      )}
                    </div>

                    <div className="bubble-bottom-bar">
                      <span className="bubble-time">
                        {new Date(m.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                      </span>

                      {!isUser && isTtsSupported && (
                        <button
                          type="button"
                          className={`tts-btn ${isSpeaking ? 'active' : ''}`}
                          onClick={() => handleToggleTts(m.id, m.content)}
                          title={isSpeaking ? t('chat.speaker.stop', { defaultValue: 'Stop speech' }) : t('chat.speaker.listen', { defaultValue: 'Listen aloud' })}
                          aria-label="Text to speech"
                        >
                          {isSpeaking ? <FiVolumeX size={15} /> : <FiVolume2 size={15} />}
                          <span>{isSpeaking ? t('chat.speaker.stop', { defaultValue: 'Stop' }) : t('chat.speaker.listen', { defaultValue: 'Listen' })}</span>
                        </button>
                      )}
                    </div>
                  </div>
                </div>
              )
            })}

            {/* Typing Indicator */}
            {loading && (
              <div className="chat-message-row row-assistant">
                <div className="chat-bubble bubble-assistant typing-bubble">
                  <div className="typing-dots">
                    <span className="dot"></span>
                    <span className="dot"></span>
                    <span className="dot"></span>
                  </div>
                  <span className="typing-text">{t('chat.typing_indicator', { defaultValue: 'AgriDarshak is analyzing...' })}</span>
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>

          {/* Suggested Question Chips */}
          <div className="suggested-chips-bar">
            <span className="suggested-label">
              <FiZap size={14} /> {t('chat.suggested.title', { defaultValue: 'Suggested Questions' })}:
            </span>
            <div className="chips-scroll-row">
              {getSuggestedQuestions().map((q) => (
                <button
                  key={q.key}
                  type="button"
                  className="suggested-chip-btn"
                  onClick={() => handleSendMessage(q.text)}
                  disabled={loading}
                >
                  {q.text}
                </button>
              ))}
            </div>
          </div>

          {/* Chat Input Bar */}
          <form className="chat-input-card" onSubmit={(e) => { e.preventDefault(); handleSendMessage(); }}>
            <button
              type="button"
              className={`mic-btn ${isListening ? 'listening' : ''}`}
              onClick={handleToggleVoiceInput}
              disabled={!isSpeechSupported}
              title={
                !isSpeechSupported
                  ? t('chat.error.unsupported_browser', { defaultValue: 'Voice input not supported on this browser' })
                  : isListening
                  ? t('chat.microphone.listening', { defaultValue: 'Listening... Click to stop' })
                  : t('chat.microphone', { defaultValue: 'Speak your question' })
              }
              aria-label="Microphone"
            >
              {isListening ? <FiMicOff size={20} /> : <FiMic size={20} />}
            </button>

            <input
              type="text"
              className="chat-text-input"
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              placeholder={
                isListening
                  ? t('chat.microphone.listening', { defaultValue: 'Listening to your voice...' })
                  : t('chat.placeholder', { defaultValue: 'Ask a question about your crop, soil, weather, irrigation, markets...' })
              }
              disabled={loading}
            />

            <button
              type="submit"
              className="send-btn"
              disabled={!inputText.trim() || loading}
              aria-label="Send message"
            >
              <FiSend size={18} />
              <span className="send-text-mobile-hide">{t('chat.send', { defaultValue: 'Send' })}</span>
            </button>
          </form>

        </div>
      </div>
    </AppLayout>
  )
}
