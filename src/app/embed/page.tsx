import { Suspense } from 'react';
import { loadTrendsData } from '@/lib/trends';
import WorldMap from '@/components/WorldMap';
import type { Metadata } from 'next';

export const revalidate = 3600;

export const metadata: Metadata = {
  title: 'TrendPulse — Embed',
  robots: { index: false, follow: false },
};

function MapSkeleton() {
  return (
    <div
      style={{
        flex: 1,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        color: 'var(--text-muted)',
        flexDirection: 'column',
        gap: '12px',
      }}
    >
      <div style={{ fontSize: '40px' }}>🌍</div>
      <div style={{ fontSize: '13px' }}>Loading world map…</div>
    </div>
  );
}

export default async function EmbedPage() {
  const data = await loadTrendsData();
  const { totalCountries, totalTrends, temperature, topTrend } = data.global;

  return (
    <div
      style={{
        display: 'flex',
        flexDirection: 'column',
        height: '100vh',
        overflow: 'hidden',
        background: 'var(--bg-base)',
        fontFamily: 'Space Grotesk, sans-serif',
      }}
    >
      {/* Compact top bar */}
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          padding: '8px 14px',
          background: 'var(--bg-surface)',
          borderBottom: '1px solid var(--border-subtle)',
          flexShrink: 0,
          gap: '10px',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <div
            style={{
              width: '22px',
              height: '22px',
              background: 'linear-gradient(135deg, #6366f1, #a855f7)',
              borderRadius: '6px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontSize: '11px',
              flexShrink: 0,
            }}
          >
            🌍
          </div>
          <span
            style={{
              fontWeight: 800,
              fontSize: '14px',
              color: 'var(--text-primary)',
              letterSpacing: '-0.02em',
            }}
          >
            Trend<span style={{ color: '#818cf8' }}>Pulse</span>
          </span>
        </div>

        <div
          style={{
            display: 'flex',
            gap: '8px',
            alignItems: 'center',
            fontSize: '11px',
            color: 'var(--text-muted)',
          }}
        >
          <span>{totalCountries} countries</span>
          <span>·</span>
          <span>{totalTrends.toLocaleString()} trends</span>
          <span>·</span>
          <span style={{ color: '#6366f1', fontWeight: 700 }}>{temperature}°T global</span>
        </div>

        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '6px',
            padding: '4px 10px',
            background: 'rgba(239,68,68,0.12)',
            border: '1px solid rgba(239,68,68,0.3)',
            borderRadius: '100px',
            fontSize: '11px',
            color: '#ef4444',
            fontWeight: 700,
            flexShrink: 0,
            maxWidth: '200px',
          }}
        >
          <span>🔥</span>
          <span
            style={{
              overflow: 'hidden',
              textOverflow: 'ellipsis',
              whiteSpace: 'nowrap',
            }}
          >
            {topTrend.keyword}
          </span>
        </div>

        <a
          href="https://global-trend-map-web.vercel.app"
          target="_blank"
          rel="noopener noreferrer"
          style={{
            fontSize: '10px',
            color: 'var(--text-muted)',
            textDecoration: 'none',
            flexShrink: 0,
            padding: '4px 8px',
            border: '1px solid var(--border-subtle)',
            borderRadius: '6px',
          }}
        >
          Open ↗
        </a>
      </div>

      {/* Map */}
      <div style={{ flex: 1, overflow: 'hidden' }}>
        <Suspense fallback={<MapSkeleton />}>
          <WorldMap data={data} />
        </Suspense>
      </div>
    </div>
  );
}
