'use client';

import { useState, useMemo } from 'react';
import {
  TrendsData,
  TrendCategory,
  TrendItem,
  getTopGlobalTrends,
  getTemperatureColor,
  getVelocityIcon,
  getVelocityColor,
  CATEGORY_ICONS,
  getTrendBadge,
} from '@/lib/trend-utils';

interface TrendListProps {
  data: TrendsData;
}

const CATEGORIES: { key: TrendCategory; label: string; icon: string }[] = [
  { key: 'all', label: 'All', icon: '🌍' },
  { key: 'sports', label: 'Sports', icon: '⚽' },
  { key: 'tech', label: 'Tech', icon: '💻' },
  { key: 'music', label: 'Music', icon: '🎵' },
  { key: 'news', label: 'News', icon: '📰' },
  { key: 'movies', label: 'Movies', icon: '🎬' },
  { key: 'finance', label: 'Finance', icon: '📈' },
];

export default function TrendList({ data }: TrendListProps) {
  const [activeCategory, setActiveCategory] = useState<TrendCategory>('all');
  const [searchQuery, setSearchQuery] = useState('');

  const trends = useMemo(() => {
    let result = getTopGlobalTrends(data, 50, activeCategory);
    if (searchQuery.trim()) {
      const q = searchQuery.toLowerCase();
      result = result.filter(
        (t) =>
          t.keyword.toLowerCase().includes(q) ||
          t.countryName.toLowerCase().includes(q)
      );
    }
    return result;
  }, [data, activeCategory, searchQuery]);

  return (
    <div
      style={{
        height: '100%',
        display: 'flex',
        flexDirection: 'column',
        background: 'var(--bg-card)',
        border: '1px solid var(--border-subtle)',
        borderRadius: '16px',
        overflow: 'hidden',
      }}
    >
      {/* Panel Header */}
      <div
        style={{
          padding: '12px 14px',
          borderBottom: '1px solid var(--border-subtle)',
          background: 'var(--bg-surface)',
          flexShrink: 0,
        }}
      >
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            marginBottom: '10px',
          }}
        >
          <span className="panel-title">Global Rankings</span>
          <span
            style={{
              padding: '2px 8px',
              background: 'rgba(99,102,241,0.15)',
              border: '1px solid rgba(99,102,241,0.3)',
              borderRadius: '100px',
              fontSize: '10px',
              fontWeight: 700,
              color: '#818cf8',
              fontFamily: 'Space Mono, monospace',
            }}
          >
            {trends.length} trends
          </span>
        </div>

        {/* Search */}
        <div style={{ position: 'relative', marginBottom: '10px' }}>
          <span
            style={{
              position: 'absolute',
              left: '10px',
              top: '50%',
              transform: 'translateY(-50%)',
              color: 'var(--text-muted)',
              fontSize: '13px',
              pointerEvents: 'none',
            }}
          >
            🔍
          </span>
          <input
            type="text"
            placeholder="Search trends or countries..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            style={{
              width: '100%',
              background: 'var(--bg-elevated)',
              border: '1px solid var(--border-subtle)',
              borderRadius: '8px',
              padding: '8px 10px 8px 30px',
              color: 'var(--text-primary)',
              fontSize: '12px',
              outline: 'none',
              fontFamily: 'Space Grotesk, sans-serif',
            }}
          />
          {searchQuery && (
            <button
              onClick={() => setSearchQuery('')}
              style={{
                position: 'absolute',
                right: '8px',
                top: '50%',
                transform: 'translateY(-50%)',
                background: 'none',
                border: 'none',
                color: 'var(--text-muted)',
                cursor: 'pointer',
                fontSize: '13px',
              }}
            >
              ✕
            </button>
          )}
        </div>

        {/* Category chips */}
        <div
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(7, 1fr)',
            gap: '4px',
          }}
        >
          {CATEGORIES.map((cat) => (
            <button
              key={cat.key}
              onClick={() => setActiveCategory(cat.key)}
              className={`category-chip${activeCategory === cat.key ? ' active' : ''}`}
            >
              {cat.label}
            </button>
          ))}
        </div>
      </div>

      {/* Spotlight Banner */}
      <div style={{ padding: '10px 14px', flexShrink: 0 }}>
        <div className="spotlight-banner">
          <span style={{ fontSize: '20px' }}>🔥</span>
          <div>
            <div
              style={{
                fontSize: '10px',
                fontFamily: 'Space Mono, monospace',
                color: 'var(--text-muted)',
                textTransform: 'uppercase',
                letterSpacing: '0.1em',
                marginBottom: '2px',
              }}
            >
              Spotlight — #1 Global
            </div>
            <div
              style={{
                fontSize: '13px',
                fontWeight: 700,
                color: 'var(--text-primary)',
              }}
            >
              {data.global.topTrend.keyword}
            </div>
            <div
              style={{
                display: 'flex',
                gap: '6px',
                marginTop: '2px',
                fontSize: '11px',
                color: 'var(--text-secondary)',
              }}
            >
              <span>{data.global.topTrend.volume} searches</span>
              <span>·</span>
              <span>{data.countries[data.global.topTrend.country]?.flag} {data.global.topTrend.country}</span>
            </div>
          </div>
          <span
            className="badge badge-global"
            style={{ marginLeft: 'auto', flexShrink: 0 }}
          >
            GLOBAL
          </span>
        </div>
      </div>

      {/* Trend list */}
      <div
        style={{
          flex: 1,
          overflowY: 'auto',
          padding: '0 10px 10px',
        }}
      >
        {trends.length === 0 ? (
          <div
            style={{
              textAlign: 'center',
              padding: '40px 20px',
              color: 'var(--text-muted)',
              fontSize: '13px',
            }}
          >
            <div style={{ fontSize: '32px', marginBottom: '8px' }}>🔍</div>
            No trends match your search
          </div>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
            {trends.map((trend, index) => {
              const badge = getTrendBadge(trend);
              const isTop3 = index < 3;
              return (
                <TrendRow
                  key={`${trend.countryCode}-${trend.rank}-${index}`}
                  trend={trend}
                  globalRank={index + 1}
                  badge={badge}
                  isTop3={isTop3}
                />
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}

interface TrendRowProps {
  trend: TrendItem & { countryCode: string; countryName: string; flag: string };
  globalRank: number;
  badge: 'GLOBAL' | 'FIRE' | 'NEW' | null;
  isTop3: boolean;
}

function TrendRow({ trend, globalRank, badge, isTop3 }: TrendRowProps) {
  const [hovered, setHovered] = useState(false);

  return (
    <div
      onMouseEnter={() => setHovered(true)}
      onMouseLeave={() => setHovered(false)}
      style={{
        display: 'flex',
        alignItems: 'center',
        gap: '10px',
        padding: '9px 10px',
        borderRadius: '10px',
        background: hovered ? 'var(--bg-elevated)' : 'transparent',
        border: `1px solid ${hovered ? 'var(--border-normal)' : 'transparent'}`,
        cursor: 'pointer',
        transition: 'all 0.15s ease',
      }}
    >
      {/* Rank */}
      <div
        style={{
          width: '26px',
          height: '26px',
          borderRadius: '50%',
          background: isTop3
            ? 'linear-gradient(135deg, #6366f1, #a855f7)'
            : 'var(--bg-elevated)',
          border: `1px solid ${isTop3 ? 'transparent' : 'var(--border-subtle)'}`,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          fontSize: '11px',
          fontWeight: 700,
          color: isTop3 ? 'white' : 'var(--text-muted)',
          fontFamily: 'Space Mono, monospace',
          flexShrink: 0,
        }}
      >
        {globalRank}
      </div>

      {/* Flag + Content */}
      <div style={{ flex: 1, minWidth: 0 }}>
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '6px',
            marginBottom: '3px',
          }}
        >
          <span style={{ fontSize: '13px' }}>{trend.flag}</span>
          <span
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
          </span>
          {badge && (
            <span
              className={`badge badge-${badge.toLowerCase()}`}
              style={{ flexShrink: 0 }}
            >
              {badge}
            </span>
          )}
        </div>

        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '6px',
          }}
        >
          <span
            style={{
              fontSize: '10px',
              color: 'var(--text-muted)',
            }}
          >
            {CATEGORY_ICONS[trend.category]} {trend.volume}
          </span>
          <span style={{ fontSize: '10px', color: 'var(--text-muted)' }}>·</span>
          <span
            style={{
              fontSize: '10px',
              color: 'var(--text-muted)',
            }}
          >
            {trend.countryName}
          </span>
        </div>

        {/* Temperature bar */}
        <div
          style={{
            marginTop: '5px',
            height: '2px',
            background: 'var(--border-subtle)',
            borderRadius: '1px',
            overflow: 'hidden',
          }}
        >
          <div
            style={{
              height: '100%',
              width: `${trend.temperature}%`,
              borderRadius: '1px',
              background: `linear-gradient(to right, var(--accent-indigo), ${getTemperatureColor(trend.temperature)})`,
              transition: 'width 0.6s ease',
            }}
          />
        </div>
      </div>

      {/* Velocity + Temp */}
      <div
        style={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'flex-end',
          gap: '2px',
          flexShrink: 0,
        }}
      >
        <span
          style={{
            fontSize: '13px',
            color: getVelocityColor(trend.velocity),
          }}
        >
          {getVelocityIcon(trend.velocity)}
        </span>
        <span
          style={{
            fontFamily: 'Space Mono, monospace',
            fontSize: '10px',
            color: getTemperatureColor(trend.temperature),
          }}
        >
          {trend.temperature}°
        </span>
      </div>
    </div>
  );
}
