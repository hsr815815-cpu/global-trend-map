'use client';

import { useEffect, useRef } from 'react';
import { createPortal } from 'react-dom';
import Link from 'next/link';
import {
  CountryData,
  getTemperatureLabel,
  getTemperatureColor,
  getVelocityIcon,
  getVelocityColor,
  CATEGORY_ICONS,
} from '@/lib/trend-utils';

interface CountryPopupProps {
  countryCode: string;
  countryData: CountryData;
  position: { x: number; y: number };
  onClose: () => void;
}

export default function CountryPopup({
  countryCode,
  countryData,
  position,
  onClose,
}: CountryPopupProps) {
  const popupRef = useRef<HTMLDivElement>(null);

  // X는 클릭 위치 기준, Y는 뷰포트 세로 중앙 고정
  const popupHeight = 430;
  const adjustedPosition = {
    x: Math.min(position.x + 16, (typeof window !== 'undefined' ? window.innerWidth : 1200) - 360),
    y: typeof window !== 'undefined' ? Math.max(20, (window.innerHeight - popupHeight) / 2) : 200,
  };

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose();
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [onClose]);

  // Calculate average temperature
  const avgTemp = Math.round(
    countryData.trends.reduce((sum, t) => sum + t.temperature, 0) /
      Math.max(countryData.trends.length, 1)
  );

  const tempLabel = getTemperatureLabel(avgTemp);
  const tempColor = getTemperatureColor(avgTemp);

  return createPortal(
    <>
      {/* Backdrop (invisible, for click-outside) */}
      <div
        style={{
          position: 'fixed',
          inset: 0,
          zIndex: 999,
        }}
        onClick={onClose}
        aria-hidden="true"
      />

      {/* Popup */}
      <div
        ref={popupRef}
        className="country-popup"
        style={{
          left: adjustedPosition.x,
          top: adjustedPosition.y,
        }}
        role="dialog"
        aria-label={`Trending in ${countryData.name}`}
      >
        {/* Header */}
        <div
          style={{
            display: 'flex',
            alignItems: 'flex-start',
            justifyContent: 'space-between',
            marginBottom: '16px',
          }}
        >
          <div>
            <div
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
                marginBottom: '4px',
              }}
            >
              <span style={{ fontSize: '24px' }}>{countryData.flag}</span>
              <div>
                <h3
                  style={{
                    fontSize: '15px',
                    fontWeight: 700,
                    color: 'var(--text-primary)',
                    lineHeight: 1.2,
                  }}
                >
                  {countryData.name}
                </h3>
                <div
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '6px',
                    marginTop: '2px',
                  }}
                >
                  <span
                    style={{
                      fontFamily: 'Space Mono, monospace',
                      fontSize: '10px',
                      color: 'var(--text-muted)',
                    }}
                  >
                    {countryCode}
                  </span>
                  <span
                    style={{
                      padding: '1px 6px',
                      borderRadius: '100px',
                      fontSize: '9px',
                      fontWeight: 700,
                      letterSpacing: '0.08em',
                      background: `${tempColor}22`,
                      border: `1px solid ${tempColor}66`,
                      color: tempColor,
                    }}
                  >
                    {tempLabel}
                  </span>
                </div>
              </div>
            </div>
          </div>

          {/* Temperature dial */}
          <div style={{ textAlign: 'right' }}>
            <div
              style={{
                fontFamily: 'Space Mono, monospace',
                fontSize: '22px',
                fontWeight: 700,
                color: tempColor,
                lineHeight: 1,
              }}
            >
              {avgTemp}°
            </div>
            <div
              style={{
                fontSize: '10px',
                color: 'var(--text-muted)',
                marginTop: '2px',
              }}
            >
              avg temp
            </div>
          </div>
        </div>

        {/* Divider */}
        <div
          style={{
            height: '1px',
            background: 'var(--border-subtle)',
            marginBottom: '12px',
          }}
        />

        {/* Top Trends */}
        <div
          style={{
            fontSize: '10px',
            fontFamily: 'Space Mono, monospace',
            color: 'var(--text-muted)',
            letterSpacing: '0.1em',
            textTransform: 'uppercase',
            marginBottom: '10px',
          }}
        >
          Top Trends
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
          {countryData.trends.slice(0, 5).map((trend) => (
            <div
              key={trend.rank}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '10px',
                padding: '8px 10px',
                background: 'var(--bg-surface)',
                borderRadius: '8px',
                border: '1px solid var(--border-subtle)',
              }}
            >
              {/* Rank */}
              <div
                style={{
                  width: '20px',
                  height: '20px',
                  borderRadius: '50%',
                  background:
                    trend.rank <= 3
                      ? 'linear-gradient(135deg, #6366f1, #a855f7)'
                      : 'var(--bg-elevated)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  fontSize: '10px',
                  fontWeight: 700,
                  color: trend.rank <= 3 ? 'white' : 'var(--text-muted)',
                  flexShrink: 0,
                }}
              >
                {trend.rank}
              </div>

              {/* Keyword & meta */}
              <div style={{ flex: 1, minWidth: 0 }}>
                <div
                  style={{
                    fontSize: '13px',
                    fontWeight: 600,
                    color: 'var(--text-primary)',
                    overflow: 'hidden',
                    textOverflow: 'ellipsis',
                    whiteSpace: 'nowrap',
                  }}
                >
                  {trend.keyword}
                </div>
                <div
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '6px',
                    marginTop: '2px',
                  }}
                >
                  <span style={{ fontSize: '11px' }}>
                    {CATEGORY_ICONS[trend.category]}
                  </span>
                  <span
                    style={{
                      fontSize: '11px',
                      color: 'var(--text-muted)',
                    }}
                  >
                    {trend.volume}
                  </span>
                </div>
              </div>

              {/* Velocity */}
              <div
                style={{
                  fontFamily: 'Space Mono, monospace',
                  fontSize: '14px',
                  color: getVelocityColor(trend.velocity),
                  flexShrink: 0,
                }}
              >
                {getVelocityIcon(trend.velocity)}
              </div>

              {/* Temperature */}
              <div
                style={{
                  fontFamily: 'Space Mono, monospace',
                  fontSize: '11px',
                  color: getTemperatureColor(trend.temperature),
                  flexShrink: 0,
                }}
              >
                {trend.temperature}°
              </div>
            </div>
          ))}
        </div>

        {/* Footer actions */}
        <div
          style={{
            display: 'flex',
            gap: '8px',
            marginTop: '14px',
          }}
        >
          <Link
            href={`/country/${countryCode.toLowerCase()}`}
            style={{
              flex: 1,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              padding: '9px',
              background: 'var(--accent-indigo)',
              borderRadius: '8px',
              color: 'white',
              fontSize: '12px',
              fontWeight: 600,
              textDecoration: 'none',
            }}
            onClick={onClose}
          >
            View All Trends →
          </Link>
          <button
            onClick={onClose}
            style={{
              padding: '9px 14px',
              background: 'transparent',
              border: '1px solid var(--border-normal)',
              borderRadius: '8px',
              color: 'var(--text-secondary)',
              fontSize: '12px',
              cursor: 'pointer',
            }}
          >
            ✕
          </button>
        </div>
      </div>
    </>,
    document.body
  );
}
