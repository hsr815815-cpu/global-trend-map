'use client';

import { useState, useEffect, useCallback } from 'react';
import Link from 'next/link';
import { formatUpdatedAgo, getNextUpdateTime } from '@/lib/trend-utils';
interface HeaderProps {
  lastUpdated: string;
  totalCountries: number;
  totalTrends: number;
}

export default function Header({
  lastUpdated,
  totalCountries,
  totalTrends,
}: HeaderProps) {
  const [updatedAgo, setUpdatedAgo] = useState('');
  const [nextUpdate, setNextUpdate] = useState('');
  const [showShareModal, setShowShareModal] = useState(false);
  const [showEmbedModal, setShowEmbedModal] = useState(false);
  const [copied, setCopied] = useState(false);
  const [embedCopied, setEmbedCopied] = useState(false);

  const updateTimes = useCallback(() => {
    setUpdatedAgo(formatUpdatedAgo(lastUpdated));
    setNextUpdate(getNextUpdateTime());
  }, [lastUpdated]);

  useEffect(() => {
    updateTimes();
    const interval = setInterval(updateTimes, 30000);
    return () => clearInterval(interval);
  }, [updateTimes]);

  const handleShare = async () => {
    if (navigator.share) {
      try {
        await navigator.share({
          title: 'TrendPulse — Real-Time Global Trend Map',
          text: 'Explore what 36 countries are searching for right now!',
          url: window.location.href,
        });
        return;
      } catch {
        // Fall through to modal
      }
    }
    setShowShareModal(true);
  };

  const copyShareLink = () => {
    navigator.clipboard.writeText(window.location.href).then(() => {
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    });
  };

  const embedCode = `<iframe
  src="${typeof window !== 'undefined' ? window.location.origin : 'https://global-trend-map-web.vercel.app'}/embed"
  width="800"
  height="500"
  frameborder="0"
  style="border-radius:12px;"
  title="TrendPulse Global Trend Map"
></iframe>`;

  const copyEmbedCode = () => {
    navigator.clipboard.writeText(embedCode).then(() => {
      setEmbedCopied(true);
      setTimeout(() => setEmbedCopied(false), 2000);
    });
  };

  return (
    <>
      <header
        style={{
          height: 'var(--header-height)',
          background: 'var(--bg-surface)',
          borderBottom: '1px solid var(--border-subtle)',
          display: 'flex',
          alignItems: 'center',
          padding: '0 16px',
          gap: '16px',
          position: 'sticky',
          top: 0,
          zIndex: 100,
        }}
      >
        {/* Logo */}
        <Link
          href="/"
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            textDecoration: 'none',
            flexShrink: 0,
          }}
        >
          <div
            style={{
              width: '28px',
              height: '28px',
              background: 'linear-gradient(135deg, #6366f1, #a855f7)',
              borderRadius: '8px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontSize: '14px',
            }}
          >
            🌍
          </div>
          <span
            style={{
              fontFamily: 'var(--font-space-grotesk, Space Grotesk), sans-serif',
              fontWeight: 800,
              fontSize: '18px',
              color: 'var(--text-primary)',
              letterSpacing: '-0.02em',
            }}
          >
            Trend<span style={{ color: '#818cf8' }}>Pulse</span>
          </span>
        </Link>

        {/* Stats bar */}
        <div
          style={{
            display: 'flex',
            gap: '8px',
            alignItems: 'center',
            flex: 1,
            overflow: 'hidden',
          }}
        >
          <div className="stats-pill">
            <span>🌐</span>
            <span className="stats-pill-value">{totalCountries}</span>
            <span>countries</span>
          </div>
          <div className="stats-pill" style={{ display: 'flex' }}>
            <span>📊</span>
            <span className="stats-pill-value">
              {totalTrends.toLocaleString()}
            </span>
            <span>trends</span>
          </div>
          <div className="stats-pill header-hide-mobile">
            <span style={{ color: '#10b981' }}>↻</span>
            <span>Next update in</span>
            <span className="stats-pill-value">{nextUpdate}</span>
          </div>
        </div>

        {/* Center: Updated time */}
        <div
          className="header-hide-mobile"
          style={{
            alignItems: 'center',
            gap: '6px',
            flexShrink: 0,
            fontSize: '12px',
            color: 'var(--text-muted)',
            fontFamily: 'Space Mono, monospace',
          }}
        >
          <span
            style={{
              width: '6px',
              height: '6px',
              borderRadius: '50%',
              background: '#10b981',
              display: 'inline-block',
              boxShadow: '0 0 6px #10b981',
              animation: 'pulse-dot 2s ease-in-out infinite',
            }}
          />
          Updated {updatedAgo}
        </div>

        {/* Right: Actions */}
        <div style={{ display: 'flex', gap: '6px', alignItems: 'center', flexShrink: 0 }}>
          {/* Share button */}
          <button
            onClick={handleShare}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '4px',
              padding: '6px 12px',
              background: 'var(--bg-elevated)',
              border: '1px solid var(--border-subtle)',
              borderRadius: '8px',
              color: 'var(--text-secondary)',
              fontSize: '12px',
              fontWeight: 600,
              cursor: 'pointer',
            }}
          >
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M12 3v13M7 8l5-5 5 5"/>
              <path d="M5 16v2a2 2 0 002 2h10a2 2 0 002-2v-2"/>
            </svg>
            <span className="header-btn-text">Share</span>
          </button>

          {/* Embed button */}
          <button
            onClick={() => setShowEmbedModal(true)}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '4px',
              padding: '6px 12px',
              background: 'var(--bg-elevated)',
              border: '1px solid var(--border-subtle)',
              borderRadius: '8px',
              color: 'var(--text-secondary)',
              fontSize: '12px',
              fontWeight: 600,
              cursor: 'pointer',
            }}
          >
            {'</>'} <span className="header-btn-text">Embed</span>
          </button>
        </div>
      </header>

      {/* Share Modal */}
      {showShareModal && (
        <div
          style={{
            position: 'fixed',
            inset: 0,
            background: 'rgba(0,0,0,0.7)',
            zIndex: 500,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
          }}
          onClick={() => setShowShareModal(false)}
        >
          <div
            style={{
              background: 'var(--bg-card)',
              border: '1px solid var(--border-normal)',
              borderRadius: '16px',
              padding: '24px',
              width: '360px',
              maxWidth: '90vw',
            }}
            onClick={(e) => e.stopPropagation()}
          >
            <h3
              style={{
                fontSize: '16px',
                fontWeight: 700,
                color: 'var(--text-primary)',
                marginBottom: '16px',
              }}
            >
              Share TrendPulse
            </h3>
            <div
              style={{
                display: 'flex',
                gap: '8px',
                marginBottom: '16px',
              }}
            >
              <input
                readOnly
                value={typeof window !== 'undefined' ? window.location.href : ''}
                style={{
                  flex: 1,
                  background: 'var(--bg-surface)',
                  border: '1px solid var(--border-normal)',
                  borderRadius: '8px',
                  padding: '10px 12px',
                  color: 'var(--text-secondary)',
                  fontSize: '13px',
                  outline: 'none',
                }}
              />
              <button
                onClick={copyShareLink}
                style={{
                  padding: '10px 14px',
                  background: copied ? '#10b981' : 'var(--accent-indigo)',
                  border: 'none',
                  borderRadius: '8px',
                  color: 'white',
                  fontSize: '13px',
                  fontWeight: 600,
                  cursor: 'pointer',
                  transition: 'background 0.2s',
                  whiteSpace: 'nowrap',
                }}
              >
                {copied ? '✓ Copied' : 'Copy'}
              </button>
            </div>
            <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
              {[
                {
                  name: 'Twitter/X',
                  color: '#000',
                  url: `https://twitter.com/intent/tweet?text=Explore+what+36+countries+are+searching+for+right+now+on+TrendPulse!&url=${encodeURIComponent(typeof window !== 'undefined' ? window.location.href : '')}`,
                },
                {
                  name: 'Facebook',
                  color: '#1877f2',
                  url: `https://www.facebook.com/sharer/sharer.php?u=${encodeURIComponent(typeof window !== 'undefined' ? window.location.href : '')}`,
                },
                {
                  name: 'Reddit',
                  color: '#ff4500',
                  url: `https://reddit.com/submit?url=${encodeURIComponent(typeof window !== 'undefined' ? window.location.href : '')}&title=TrendPulse+Global+Trend+Map`,
                },
              ].map((social) => (
                <a
                  key={social.name}
                  href={social.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  style={{
                    padding: '8px 14px',
                    background: social.color,
                    border: 'none',
                    borderRadius: '8px',
                    color: 'white',
                    fontSize: '12px',
                    fontWeight: 600,
                    cursor: 'pointer',
                    textDecoration: 'none',
                  }}
                >
                  {social.name}
                </a>
              ))}
            </div>
            <button
              onClick={() => setShowShareModal(false)}
              style={{
                marginTop: '16px',
                width: '100%',
                padding: '10px',
                background: 'transparent',
                border: '1px solid var(--border-normal)',
                borderRadius: '8px',
                color: 'var(--text-secondary)',
                fontSize: '13px',
                cursor: 'pointer',
              }}
            >
              Close
            </button>
          </div>
        </div>
      )}

      {/* Embed Modal */}
      {showEmbedModal && (
        <div
          style={{
            position: 'fixed',
            inset: 0,
            background: 'rgba(0,0,0,0.7)',
            zIndex: 500,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
          }}
          onClick={() => setShowEmbedModal(false)}
        >
          <div
            style={{
              background: 'var(--bg-card)',
              border: '1px solid var(--border-normal)',
              borderRadius: '16px',
              padding: '24px',
              width: '500px',
              maxWidth: '90vw',
            }}
            onClick={(e) => e.stopPropagation()}
          >
            <h3
              style={{
                fontSize: '16px',
                fontWeight: 700,
                color: 'var(--text-primary)',
                marginBottom: '8px',
              }}
            >
              Embed TrendPulse
            </h3>
            <p
              style={{
                fontSize: '13px',
                color: 'var(--text-secondary)',
                marginBottom: '16px',
              }}
            >
              Copy and paste this code to embed the trend map on your website.
            </p>
            <pre
              style={{
                background: 'var(--bg-surface)',
                border: '1px solid var(--border-normal)',
                borderRadius: '8px',
                padding: '14px',
                fontSize: '12px',
                color: '#06b6d4',
                overflow: 'auto',
                marginBottom: '12px',
                whiteSpace: 'pre-wrap',
                wordBreak: 'break-all',
              }}
            >
              {embedCode}
            </pre>
            <div style={{ display: 'flex', gap: '8px' }}>
              <button
                onClick={copyEmbedCode}
                style={{
                  flex: 1,
                  padding: '10px',
                  background: embedCopied ? '#10b981' : 'var(--accent-indigo)',
                  border: 'none',
                  borderRadius: '8px',
                  color: 'white',
                  fontSize: '13px',
                  fontWeight: 600,
                  cursor: 'pointer',
                }}
              >
                {embedCopied ? '✓ Copied!' : 'Copy Embed Code'}
              </button>
              <button
                onClick={() => setShowEmbedModal(false)}
                style={{
                  padding: '10px 16px',
                  background: 'transparent',
                  border: '1px solid var(--border-normal)',
                  borderRadius: '8px',
                  color: 'var(--text-secondary)',
                  fontSize: '13px',
                  cursor: 'pointer',
                }}
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
