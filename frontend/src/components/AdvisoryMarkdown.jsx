import ReactMarkdown from 'react-markdown'
import { useTranslation } from 'react-i18next'
import TextToSpeech from './TextToSpeech'
import './AdvisoryMarkdown.css'

/** Renders structured advisory content (markdown) for UI display.
 * Displays source indicator ("AI Advisory" vs "Smart Advisory") and optional TTS.
 */
export default function AdvisoryMarkdown({ content, className = '', language, source = 'ai' }) {
  const { t } = useTranslation()
  if (!content || typeof content !== 'string') return null

  const isAi = source === 'ai' || source === 'gemini'

  return (
    <div className={`advisory-markdown-wrapper ${className} source-${isAi ? 'ai' : 'fallback'}`}>
      <div className="advisory-header-row">
        <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)' }}>
          <span className={`advisory-badge-pill ${isAi ? 'pill-ai' : 'pill-fallback'}`}>
            {isAi ? '✨ ' + t('advisory.aiAdvisory') : '🌱 ' + t('advisory.smartAdvisory')}
          </span>
          <span className="advisory-badge-sub">
            ({isAi ? t('advisory.aiBadge') : t('advisory.fallbackBadge')})
          </span>
        </div>

        {language && (
          <div className="advisory-tts-row">
            <TextToSpeech text={content} language={language} />
          </div>
        )}
      </div>

      <div className="advisory-markdown">
        <ReactMarkdown
          components={{
            h1: ({ children }) => <h3 className="advisory-section-title">{children}</h3>,
            h2: ({ children }) => <h3 className="advisory-heading">{children}</h3>,
            h3: ({ children }) => <h4 className="advisory-subheading">{children}</h4>,
            ul: ({ children }) => <ul className="advisory-list">{children}</ul>,
            ol: ({ children }) => <ol className="advisory-ordered-list">{children}</ol>,
            li: ({ children }) => <li className="advisory-list-item">{children}</li>,
            p: ({ children }) => <p className="advisory-para">{children}</p>,
            strong: ({ children }) => <strong className="advisory-bold">{children}</strong>,
            blockquote: ({ children }) => <blockquote className="advisory-quote">{children}</blockquote>
          }}
        >
          {content}
        </ReactMarkdown>
      </div>
    </div>
  )
}
