'use client';

import { useMemo } from 'react';
import Link from 'next/link';
import type { TrendsData, TrendItem, ChartItem } from '@/lib/trend-utils';
import {
  getTemperatureColor,
  CATEGORY_ICONS,
  CATEGORY_COLORS,
} from '@/lib/trend-utils';

interface BottomCardsProps {
  data: TrendsData;
}

const CARD_CATEGORIES = ['sports', 'tech', 'music', 'news', 'movies', 'finance'];

export default function BottomCards({ data }: BottomCardsProps) {
  const topByCategory = useMemo(() => {
    const result: Record<string, (TrendItem & { countryCode: string; flag: string; countryName: string }) | null> = {};

    const SOURCE_FLAGS: Record<string, string> = {
      'Apple Music': '🎵', 'iTunes Movies': '🎬',
      'Hacker News': '💻', 'MarketWatch': '📈',
      'ESPN': '⚽', 'BBC Sport': '🏅',
    };

    for (const category of CARD_CATEGORIES) {
      let topTrend: (TrendItem & { countryCode: string; flag: string; countryName: string }) | null = null;

      // Check category charts first
      const chartItems = data.categoryCharts?.[category] || [];
      chartItems.forEach((item) => {
        if (!topTrend || item.temperature > topTrend.temperature) {
          topTrend = {
            ...item,
            countryCode: 'CHART',
            flag: SOURCE_FLAGS[item.source] || '📊',
            countryName: item.source,
          };
        }
      });

      // Check Google Trends countries
      Object.entries(data.countries).forEach(([code, country]) => {
        country.trends.forEach((trend) => {
          if (trend.category === category) {
            if (!topTrend || trend.temperature > topTrend.temperature) {
              topTrend = { ...trend, countryCode: code, flag: country.flag, countryName: country.name };
            }
          }
        });
      });

      result[category] = topTrend;
    }

    return result;
  }, [data]);

  return (
    <div
      className="bottom-cards-container"
      style={{
        display: 'flex',
        gap: '10px',
        height: '100%',
        overflowX: 'auto',
        paddingBottom: '2px',
      }}
    >
      {CARD_CATEGORIES.map((category) => {
        const trend = topByCategory[category];
        const color = CATEGORY_COLORS[category] || '#6366f1';
        const icon = CATEGORY_ICONS[category] || '📊';

        return (
          <CategoryCard
            key={category}
            category={category}
            trend={trend}
            color={color}
            icon={icon}
          />
        );
      })}

      {/* Global average card */}
      <GlobalCard data={data} />
    </div>
  );
}

interface CategoryCardProps {
  category: string;
  trend: (TrendItem & { countryCode: string; flag: string; countryName: string }) | null;
  color: string;
  icon: string;
}

function CategoryCard({ category, trend, color, icon }: CategoryCardProps) {
  const tempColor = trend ? getTemperatureColor(trend.temperature) : '#475569';

  return (
    <div
      style={{
        minWidth: '200px',
        maxWidth: '200px',
        background: 'var(--bg-card)',
        border: '1px solid var(--border-subtle)',
        borderRadius: '12px',
        padding: '12px 14px',
        display: 'flex',
        flexDirection: 'column',
        gap: '8px',
        flexShrink: 0,
        transition: 'all 0.15s ease',
        cursor: trend ? 'pointer' : 'default',
        position: 'relative',
        overflow: 'hidden',
      }}
      onClick={() => {
        if (trend) {
          window.open(
            `https://www.google.com/search?q=${encodeURIComponent(trend.keyword)}&tbm=nws`,
            '_blank'
          );
        }
      }}
      onMouseEnter={(e) => {
        (e.currentTarget as HTMLDivElement).style.borderColor = `${color}66`;
        (e.currentTarget as HTMLDivElement).style.background = 'var(--bg-elevated)';
      }}
      onMouseLeave={(e) => {
        (e.currentTarget as HTMLDivElement).style.borderColor = 'var(--border-subtle)';
        (e.currentTarget as HTMLDivElement).style.background = 'var(--bg-card)';
      }}
    >
      {/* Gradient accent */}
      <div
        style={{
          position: 'absolute',
          top: 0,
          left: 0,
          right: 0,
          height: '2px',
          background: color,
        }}
      />

      {/* Category header */}
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
          <span style={{ fontSize: '14px' }}>{icon}</span>
          <span
            style={{
              fontFamily: 'Space Mono, monospace',
              fontSize: '10px',
              fontWeight: 700,
              letterSpacing: '0.08em',
              textTransform: 'uppercase',
              color: color,
            }}
          >
            {category}
          </span>
        </div>
        {trend && (
          <span
            style={{
              fontFamily: 'Space Mono, monospace',
              fontSize: '11px',
              fontWeight: 700,
              color: tempColor,
            }}
          >
            {trend.temperature}°
          </span>
        )}
      </div>

      {/* Trend content */}
      {trend ? (
        <>
          <div
            style={{
              fontSize: '13px',
              fontWeight: 700,
              color: 'var(--text-primary)',
              lineHeight: 1.3,
              overflow: 'hidden',
              display: '-webkit-box',
              WebkitLineClamp: 2,
              WebkitBoxOrient: 'vertical',
            }}
          >
            {trend.keywordEn || trend.keyword}
          </div>

          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
              marginTop: 'auto',
            }}
          >
            <span style={{ fontSize: '14px' }}>{trend.flag}</span>
            <div>
              <div
                style={{
                  fontSize: '10px',
                  color: 'var(--text-secondary)',
                  fontWeight: 600,
                }}
              >
                {trend.volume} searches
              </div>
              <div style={{ fontSize: '10px', color: 'var(--text-muted)' }}>
                {trend.countryName}
              </div>
            </div>
          </div>

          {/* Volume bar */}
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
                width: `${trend.temperature}%`,
                background: color,
                borderRadius: '2px',
              }}
            />
          </div>
        </>
      ) : (
        <div
          style={{
            flex: 1,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: 'var(--text-muted)',
            fontSize: '12px',
          }}
        >
          No data
        </div>
      )}
    </div>
  );
}

function GlobalCard({ data }: { data: TrendsData }) {
  const globalTemp = data.global.temperature;
  const tempColor = getTemperatureColor(globalTemp);

  return (
    <div
      style={{
        minWidth: '200px',
        maxWidth: '200px',
        background: 'linear-gradient(135deg, rgba(99,102,241,0.12), rgba(168,85,247,0.12))',
        border: '1px solid rgba(99,102,241,0.3)',
        borderRadius: '12px',
        padding: '12px 14px',
        display: 'flex',
        flexDirection: 'column',
        gap: '8px',
        flexShrink: 0,
        position: 'relative',
        overflow: 'hidden',
      }}
    >
      <div
        style={{
          position: 'absolute',
          top: 0,
          left: 0,
          right: 0,
          height: '2px',
          background: 'linear-gradient(to right, #6366f1, #a855f7)',
        }}
      />

      <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
        <span style={{ fontSize: '14px' }}>🌍</span>
        <span
          style={{
            fontFamily: 'Space Mono, monospace',
            fontSize: '10px',
            fontWeight: 700,
            letterSpacing: '0.08em',
            color: '#818cf8',
          }}
        >
          GLOBAL
        </span>
      </div>

      <div>
        <div
          style={{
            fontFamily: 'Space Mono, monospace',
            fontSize: '28px',
            fontWeight: 700,
            color: tempColor,
            lineHeight: 1,
          }}
        >
          {globalTemp}°
        </div>
        <div
          style={{
            fontSize: '11px',
            color: 'var(--text-secondary)',
            marginTop: '2px',
          }}
        >
          World Temperature
        </div>
      </div>

      <div style={{ marginTop: 'auto' }}>
        <div
          style={{
            fontSize: '10px',
            color: 'var(--text-muted)',
            marginBottom: '4px',
          }}
        >
          {data.global.totalCountries} countries · {data.global.totalTrends.toLocaleString()} trends
        </div>
        <div style={{ display: 'flex', gap: '4px' }}>
          <Link
            href="/blog"
            style={{
              flex: 1,
              padding: '5px',
              background: 'rgba(99,102,241,0.2)',
              border: '1px solid rgba(99,102,241,0.3)',
              borderRadius: '6px',
              color: '#818cf8',
              fontSize: '10px',
              fontWeight: 600,
              textDecoration: 'none',
              textAlign: 'center',
            }}
          >
            Blog
          </Link>
          <Link
            href="/about"
            style={{
              flex: 1,
              padding: '5px',
              background: 'transparent',
              border: '1px solid var(--border-subtle)',
              borderRadius: '6px',
              color: 'var(--text-muted)',
              fontSize: '10px',
              fontWeight: 600,
              textDecoration: 'none',
              textAlign: 'center',
            }}
          >
            About
          </Link>
        </div>
      </div>
    </div>
  );
}
