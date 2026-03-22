'use client';

import { useState } from 'react';
import {
  TrendsData,
  TrendCategory,
  getTemperatureLabel,
  getTemperatureColor,
  getTemperatureGradient,
  CATEGORY_ICONS,
  CATEGORY_COLORS,
  getVelocityColor,
} from '@/lib/trend-utils';

interface RightPanelProps {
  data: TrendsData;
}

const CATEGORIES: { key: TrendCategory; label: string }[] = [
  { key: 'sports', label: 'Sports' },
  { key: 'music', label: 'Music' },
  { key: 'tech', label: 'Tech' },
  { key: 'news', label: 'News' },
  { key: 'movies', label: 'Movies' },
  { key: 'finance', label: 'Finance' },
];

export default function RightPanel({ data }: RightPanelProps) {
  const [activeCategory, setActiveCategory] = useState<TrendCategory | null>(null);

  const globalTemp = data.global.temperature;
  const tempLabel = getTemperatureLabel(globalTemp);
  const tempColor = getTemperatureColor(globalTemp);
  const tempGradient = getTemperatureGradient(globalTemp);

  const categoryBreakdown = data.global.categoryBreakdown;
  const risingFast = data.global.risingFast || [];

  const getTempStatusColor = () => {
    if (globalTemp >= 90) return '#ea580c';
    if (globalTemp >= 75) return '#dc2626';
    if (globalTemp >= 60) return '#7c3aed';
    if (globalTemp >= 40) return '#1d4ed8';
    return '#1e3a5f';
  };

  return (
    <div
      style={{
        height: '100%',
        display: 'flex',
        flexDirection: 'column',
        gap: '10px',
        overflowY: 'auto',
      }}
    >
      {/* Thermometer Panel */}
      <div
        style={{
          background: 'var(--bg-card)',
          border: '1px solid var(--border-subtle)',
          borderRadius: '16px',
          overflow: 'hidden',
          flexShrink: 0,
        }}
      >
        <div className="panel-header">
          <span className="panel-title">Global Thermometer</span>
          <span
            style={{
              fontFamily: 'Space Mono, monospace',
              fontSize: '10px',
              color: 'var(--text-muted)',
            }}
          >
            °T SCALE
          </span>
        </div>

        <div style={{ padding: '16px' }}>
          <div
            style={{
              display: 'flex',
              gap: '20px',
              alignItems: 'flex-end',
            }}
          >
            {/* Thermometer tube */}
            <div style={{ position: 'relative', flexShrink: 0 }}>
              {/* Scale labels */}
              <div
                style={{
                  position: 'absolute',
                  right: '100%',
                  paddingRight: '6px',
                  height: '120px',
                  display: 'flex',
                  flexDirection: 'column',
                  justifyContent: 'space-between',
                  alignItems: 'flex-end',
                }}
              >
                {[100, 75, 50, 25, 0].map((v) => (
                  <span
                    key={v}
                    style={{
                      fontFamily: 'Space Mono, monospace',
                      fontSize: '8px',
                      color: 'var(--text-muted)',
                      lineHeight: 1,
                    }}
                  >
                    {v}
                  </span>
                ))}
              </div>

              {/* Tube */}
              <div
                style={{
                  width: '20px',
                  height: '120px',
                  background: 'var(--bg-surface)',
                  border: '2px solid var(--border-normal)',
                  borderRadius: '10px',
                  overflow: 'hidden',
                  position: 'relative',
                }}
              >
                <div
                  style={{
                    position: 'absolute',
                    bottom: 0,
                    left: 0,
                    right: 0,
                    height: `${globalTemp}%`,
                    background: tempGradient,
                    borderRadius: '8px',
                    transition: 'height 1.5s cubic-bezier(0.34, 1.56, 0.64, 1)',
                  }}
                />
              </div>

              {/* Bulb */}
              <div
                style={{
                  width: '28px',
                  height: '28px',
                  borderRadius: '50%',
                  background: tempColor,
                  border: `3px solid var(--border-normal)`,
                  marginLeft: '-4px',
                  marginTop: '4px',
                  boxShadow: `0 0 12px ${tempColor}66`,
                }}
              />
            </div>

            {/* Temperature info */}
            <div style={{ flex: 1 }}>
              <div
                style={{
                  fontFamily: 'Space Mono, monospace',
                  fontSize: '48px',
                  fontWeight: 700,
                  color: tempColor,
                  lineHeight: 1,
                  marginBottom: '4px',
                }}
              >
                {globalTemp}
                <span style={{ fontSize: '24px' }}>°T</span>
              </div>

              <div
                style={{
                  padding: '4px 10px',
                  background: `${tempColor}22`,
                  border: `1px solid ${tempColor}55`,
                  borderRadius: '100px',
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: '4px',
                  marginBottom: '8px',
                }}
              >
                <span style={{ fontSize: '11px' }}>
                  {globalTemp >= 90 ? '🔥' : globalTemp >= 75 ? '🌡️' : '📊'}
                </span>
                <span
                  style={{
                    fontSize: '11px',
                    fontWeight: 700,
                    color: tempColor,
                    fontFamily: 'Space Mono, monospace',
                    letterSpacing: '0.08em',
                  }}
                >
                  {tempLabel}
                </span>
              </div>

              <div
                style={{
                  fontSize: '11px',
                  color: 'var(--text-muted)',
                  lineHeight: 1.5,
                }}
              >
                Global trend intensity across {data.global.totalCountries} countries
              </div>
            </div>
          </div>

          {/* Temp scale reference */}
          <div
            style={{
              marginTop: '14px',
              padding: '10px',
              background: 'var(--bg-surface)',
              borderRadius: '8px',
              display: 'grid',
              gridTemplateColumns: '1fr 1fr',
              gap: '4px',
            }}
          >
            {[
              { label: 'SUPER HOT', range: '90-100°', color: '#ea580c' },
              { label: 'HOT', range: '75-89°', color: '#dc2626' },
              { label: 'WARM', range: '60-74°', color: '#7c3aed' },
              { label: 'RISING', range: '40-59°', color: '#1d4ed8' },
            ].map((item) => (
              <div
                key={item.label}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '6px',
                }}
              >
                <div
                  style={{
                    width: '8px',
                    height: '8px',
                    borderRadius: '50%',
                    background: item.color,
                    flexShrink: 0,
                  }}
                />
                <span style={{ fontSize: '10px', color: 'var(--text-muted)' }}>
                  {item.label}
                </span>
                <span
                  style={{
                    fontFamily: 'Space Mono, monospace',
                    fontSize: '9px',
                    color: item.label === tempLabel ? item.color : 'var(--text-muted)',
                    marginLeft: 'auto',
                    fontWeight: item.label === tempLabel ? 700 : 400,
                  }}
                >
                  {item.range}
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Category Grid */}
      <div
        style={{
          background: 'var(--bg-card)',
          border: '1px solid var(--border-subtle)',
          borderRadius: '16px',
          overflow: 'hidden',
          flexShrink: 0,
        }}
      >
        <div className="panel-header">
          <span className="panel-title">Categories</span>
          {activeCategory && (
            <button
              onClick={() => setActiveCategory(null)}
              style={{
                background: 'none',
                border: 'none',
                color: 'var(--text-muted)',
                cursor: 'pointer',
                fontSize: '11px',
              }}
            >
              Clear ✕
            </button>
          )}
        </div>

        <div
          style={{
            padding: '12px',
            display: 'grid',
            gridTemplateColumns: '1fr 1fr',
            gap: '8px',
          }}
        >
          {CATEGORIES.map((cat) => {
            const count = categoryBreakdown[cat.key] || 0;
            const total = Object.values(categoryBreakdown).reduce((a, b) => a + b, 0);
            const pct = total > 0 ? Math.round((count / total) * 100) : 0;
            const color = CATEGORY_COLORS[cat.key] || '#6366f1';
            const isActive = activeCategory === cat.key;

            return (
              <button
                key={cat.key}
                onClick={() => setActiveCategory(isActive ? null : cat.key)}
                style={{
                  display: 'flex',
                  flexDirection: 'column',
                  gap: '6px',
                  padding: '10px',
                  background: isActive ? `${color}18` : 'var(--bg-surface)',
                  border: `1px solid ${isActive ? color + '44' : 'var(--border-subtle)'}`,
                  borderRadius: '10px',
                  cursor: 'pointer',
                  textAlign: 'left',
                  transition: 'all 0.15s ease',
                }}
              >
                <div
                  style={{
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                  }}
                >
                  <span style={{ fontSize: '16px' }}>{CATEGORY_ICONS[cat.key]}</span>
                  <span
                    style={{
                      fontFamily: 'Space Mono, monospace',
                      fontSize: '10px',
                      color: isActive ? color : 'var(--text-muted)',
                      fontWeight: 700,
                    }}
                  >
                    {pct}%
                  </span>
                </div>
                <div>
                  <div
                    style={{
                      fontSize: '11px',
                      fontWeight: 600,
                      color: isActive ? color : 'var(--text-secondary)',
                      marginBottom: '4px',
                    }}
                  >
                    {cat.label}
                  </div>
                  <div
                    style={{
                      height: '3px',
                      background: 'var(--border-subtle)',
                      borderRadius: '2px',
                      overflow: 'hidden',
                    }}
                  >
                    <div
                      style={{
                        height: '100%',
                        width: `${pct}%`,
                        background: color,
                        borderRadius: '2px',
                        transition: 'width 0.6s ease',
                      }}
                    />
                  </div>
                </div>
              </button>
            );
          })}
        </div>
      </div>

      {/* Rising Fast / Velocity Panel */}
      <div
        style={{
          background: 'var(--bg-card)',
          border: '1px solid var(--border-subtle)',
          borderRadius: '16px',
          overflow: 'hidden',
          flexShrink: 0,
        }}
      >
        <div className="panel-header">
          <span className="panel-title">Rising Fast</span>
          <span style={{ fontSize: '14px' }}>⚡</span>
        </div>

        <div style={{ padding: '12px', display: 'flex', flexDirection: 'column', gap: '8px' }}>
          {risingFast.length === 0 ? (
            <div
              style={{
                textAlign: 'center',
                padding: '20px',
                color: 'var(--text-muted)',
                fontSize: '12px',
              }}
            >
              No velocity data yet
            </div>
          ) : (
            risingFast.map((item, i) => (
              <div
                key={i}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '10px',
                  padding: '9px 10px',
                  background: 'var(--bg-surface)',
                  borderRadius: '8px',
                  border: '1px solid var(--border-subtle)',
                }}
              >
                <div
                  style={{
                    width: '22px',
                    height: '22px',
                    borderRadius: '50%',
                    background: 'rgba(249,115,22,0.2)',
                    border: '1px solid rgba(249,115,22,0.4)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    fontSize: '10px',
                    flexShrink: 0,
                  }}
                >
                  ↑
                </div>
                <div style={{ flex: 1, minWidth: 0 }}>
                  <div
                    style={{
                      fontSize: '12px',
                      fontWeight: 600,
                      color: 'var(--text-primary)',
                      overflow: 'hidden',
                      textOverflow: 'ellipsis',
                      whiteSpace: 'nowrap',
                    }}
                  >
                    {item.keyword}
                  </div>
                  <div style={{ fontSize: '10px', color: 'var(--text-muted)' }}>
                    {data.countries[item.country]?.flag} {item.country}
                  </div>
                </div>
                <span
                  style={{
                    fontFamily: 'Space Mono, monospace',
                    fontSize: '11px',
                    fontWeight: 700,
                    color: '#10b981',
                    flexShrink: 0,
                  }}
                >
                  {item.change}
                </span>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}
