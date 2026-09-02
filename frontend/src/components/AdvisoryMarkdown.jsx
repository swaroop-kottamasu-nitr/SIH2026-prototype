import ReactMarkdown from 'react-markdown'
import { useTranslation } from 'react-i18next'
import TextToSpeech from './TextToSpeech'

/** Renders structured advisory content (markdown) for UI display.
 * Displays source indicator ("AI Advisory" vs "Smart Advisory") and optional TTS.
 */
export default function AdvisoryMarkdown({ content, className = '', language, source = 'ai' }) {
  const { t } = useTranslation()
  if (!content || typeof content !== 'string') return null

  const isAi = source === 'ai' || source === 'gemini'

  return (
    <div className={`advisory-markdown-wrapper ${className} source-${isAi ? 'ai' : 'fallback'}`}>
      <div className="advisory-header-row" style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        flexWrap: 'wrap',
        gap: 'var(--space-2)',
        marginBottom: 'var(--space-4)',
        paddingBottom: 'var(--space-3)',
        borderBottom: '1px solid var(--color-border)'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)' }}>
          <span style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: 6,
            padding: '4px 10px',
            borderRadius: 'var(--radius-full)',
            fontSize: 'var(--text-xs)',
            fontWeight: 700,
            letterSpacing: '0.04em',
            textTransform: 'uppercase',
            backgroundColor: isAi ? 'rgba(31, 122, 69, 0.1)' : 'rgba(95, 175, 69, 0.12)',
            color: isAi ? 'var(--brand-primary)' : 'var(--brand-secondary)',
            border: `1px solid ${isAi ? 'rgba(31, 122, 69, 0.25)' : 'rgba(95, 175, 69, 0.3)'}`
          }}>
            {isAi ? '✨ ' + t('advisory.aiAdvisory') : '🌱 ' + t('advisory.smartAdvisory')}
          </span>
          <span style={{ fontSize: 'var(--text-xs)', color: 'var(--color-text-tertiary)' }}>
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
            h2: ({ children }) => <h3 className="advisory-heading">{children}</h3>,
            h3: ({ children }) => <h4 className="advisory-subheading">{children}</h4>,
            ul: ({ children }) => <ul className="advisory-list">{children}</ul>,
            p: ({ children }) => <p className="advisory-para">{children}</p>,
          }}
        >
          {content}
        </ReactMarkdown>
      </div>
    </div>
  )
}
