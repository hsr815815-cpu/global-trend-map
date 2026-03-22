'use client';

import { useState, useEffect } from 'react';

const COOKIE_KEY = 'trendpulse_cookie_consent';

export default function CookieBanner() {
  const [visible, setVisible] = useState(false);
  const [showDetails, setShowDetails] = useState(false);

  useEffect(() => {
    try {
      const consent = localStorage.getItem(COOKIE_KEY);
      if (!consent) {
        // Small delay so it doesn't flash immediately on load
        const timer = setTimeout(() => setVisible(true), 1500);
        return () => clearTimeout(timer);
      }
    } catch {
      // localStorage not available (SSR guard)
    }
  }, []);

  const acceptAll = () => {
    try {
      localStorage.setItem(COOKIE_KEY, 'all');
    } catch {
      /* ignore */
    }
    setVisible(false);
    // Enable GA4 tracking
    if (typeof window !== 'undefined') {
      const gtag = (window as Window & { gtag?: (...args: unknown[]) => void }).gtag;
      if (gtag) gtag('consent', 'update', { analytics_storage: 'granted', ad_storage: 'granted' });
    }
  };

  const acceptEssential = () => {
    try {
      localStorage.setItem(COOKIE_KEY, 'essential');
    } catch {
      /* ignore */
    }
    setVisible(false);
    // Deny analytics
    if (typeof window !== 'undefined') {
      const gtag = (window as Window & { gtag?: (...args: unknown[]) => void }).gtag;
      if (gtag) gtag('consent', 'update', { analytics_storage: 'denied', ad_storage: 'denied' });
    }
  };

  const rejectAll = () => {
    try {
      localStorage.setItem(COOKIE_KEY, 'rejected');
    } catch {
      /* ignore */
    }
    setVisible(false);
  };

  if (!visible) return null;

  return (
    <div
      className="cookie-banner"
      role="dialog"
      aria-modal="true"
      aria-label="Cookie consent"
    >
      <div style={{ maxWidth: '1200px', margin: '0 auto' }}>
        <div
          style={{
            display: 'flex',
            alignItems: 'flex-start',
            gap: '20px',
            flexWrap: 'wrap',
          }}
        >
          {/* Icon */}
          <div
            style={{
              fontSize: '32px',
              flexShrink: 0,
              marginTop: '2px',
            }}
            aria-hidden="true"
          >
            🍪
          </div>

          {/* Content */}
          <div style={{ flex: 1, minWidth: '280px' }}>
            <h3
              style={{
                fontSize: '15px',
                fontWeight: 700,
                color: 'var(--text-primary)',
                marginBottom: '6px',
              }}
            >
              We use cookies to improve your experience
            </h3>
            <p
              style={{
                fontSize: '13px',
                color: 'var(--text-secondary)',
                lineHeight: 1.6,
                marginBottom: showDetails ? '12px' : '0',
              }}
            >
              TrendPulse uses cookies for analytics (Google Analytics 4),
              performance monitoring, and to remember your preferences. We never
              sell your data. You can choose which cookies to accept.{' '}
              <button
                onClick={() => setShowDetails(!showDetails)}
                style={{
                  background: 'none',
                  border: 'none',
                  color: 'var(--accent-indigo-bright)',
                  cursor: 'pointer',
                  fontSize: '13px',
                  padding: 0,
                  textDecoration: 'underline',
                }}
              >
                {showDetails ? 'Show less' : 'Learn more'}
              </button>
            </p>

            {showDetails && (
              <div
                style={{
                  background: 'var(--bg-surface)',
                  border: '1px solid var(--border-subtle)',
                  borderRadius: '8px',
                  padding: '14px',
                  marginBottom: '12px',
                  fontSize: '12px',
                  color: 'var(--text-secondary)',
                  lineHeight: 1.6,
                }}
              >
                <p style={{ marginBottom: '8px', fontWeight: 600, color: 'var(--text-primary)' }}>
                  Cookie Types We Use:
                </p>
                <ul style={{ paddingLeft: '16px', margin: 0 }}>
                  <li style={{ marginBottom: '6px' }}>
                    <strong style={{ color: 'var(--text-primary)' }}>Essential cookies</strong> — Required for the
                    site to function (cookie preference storage, security). Cannot be disabled.
                  </li>
                  <li style={{ marginBottom: '6px' }}>
                    <strong style={{ color: 'var(--text-primary)' }}>Analytics cookies</strong> — Google Analytics
                    4 helps us understand how visitors use the site (pages viewed, session duration, country). IP
                    addresses are anonymized.
                  </li>
                  <li>
                    <strong style={{ color: 'var(--text-primary)' }}>Advertising cookies</strong> — Google AdSense
                    may serve personalized or contextual ads based on your interests and browsing behavior.
                  </li>
                </ul>
                <p style={{ marginTop: '10px' }}>
                  For more details, see our{' '}
                  <a
                    href="/cookie-policy"
                    style={{ color: 'var(--accent-indigo-bright)' }}
                  >
                    Cookie Policy
                  </a>{' '}
                  and{' '}
                  <a
                    href="/privacy-policy"
                    style={{ color: 'var(--accent-indigo-bright)' }}
                  >
                    Privacy Policy
                  </a>
                  .
                </p>
              </div>
            )}
          </div>

          {/* Buttons */}
          <div
            style={{
              display: 'flex',
              gap: '8px',
              flexShrink: 0,
              flexWrap: 'wrap',
              alignItems: 'center',
            }}
          >
            <button
              onClick={rejectAll}
              style={{
                padding: '8px 14px',
                background: 'transparent',
                border: '1px solid var(--border-normal)',
                borderRadius: '8px',
                color: 'var(--text-muted)',
                fontSize: '12px',
                fontWeight: 600,
                cursor: 'pointer',
                transition: 'all 0.15s ease',
                whiteSpace: 'nowrap',
              }}
              onMouseEnter={(e) => {
                (e.target as HTMLButtonElement).style.color = 'var(--text-secondary)';
              }}
              onMouseLeave={(e) => {
                (e.target as HTMLButtonElement).style.color = 'var(--text-muted)';
              }}
            >
              Reject All
            </button>

            <button
              onClick={acceptEssential}
              style={{
                padding: '8px 14px',
                background: 'var(--bg-elevated)',
                border: '1px solid var(--border-normal)',
                borderRadius: '8px',
                color: 'var(--text-secondary)',
                fontSize: '12px',
                fontWeight: 600,
                cursor: 'pointer',
                transition: 'all 0.15s ease',
                whiteSpace: 'nowrap',
              }}
            >
              Essential Only
            </button>

            <button
              onClick={acceptAll}
              style={{
                padding: '8px 20px',
                background: 'var(--accent-indigo)',
                border: 'none',
                borderRadius: '8px',
                color: 'white',
                fontSize: '12px',
                fontWeight: 700,
                cursor: 'pointer',
                transition: 'all 0.15s ease',
                whiteSpace: 'nowrap',
              }}
              onMouseEnter={(e) => {
                (e.target as HTMLButtonElement).style.background = 'var(--accent-violet)';
              }}
              onMouseLeave={(e) => {
                (e.target as HTMLButtonElement).style.background = 'var(--accent-indigo)';
              }}
            >
              Accept All
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
