import { Suspense } from 'react';
import { loadTrendsData } from '@/lib/trends';
import Header from '@/components/Header';
import TrendList from '@/components/TrendList';
import WorldMap from '@/components/WorldMap';
import RightPanel from '@/components/RightPanel';
import BottomCards from '@/components/BottomCards';

// Revalidate every 60 minutes (data updates hourly)
export const revalidate = 3600;

function MapSkeleton() {
  return (
    <div
      style={{
        height: '100%',
        background: 'var(--bg-card)',
        border: '1px solid var(--border-subtle)',
        borderRadius: '16px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
      }}
    >
      <div
        style={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          gap: '12px',
          color: 'var(--text-muted)',
        }}
      >
        <div
          style={{
            fontSize: '40px',
            animation: 'spin-slow 4s linear infinite',
          }}
        >
          🌍
        </div>
        <div style={{ fontSize: '13px' }}>Loading world map…</div>
      </div>
    </div>
  );
}

export default async function HomePage() {
  const data = await loadTrendsData();

  return (
    <div
      style={{
        display: 'flex',
        flexDirection: 'column',
        height: '100vh',
        overflow: 'hidden',
        background: 'var(--bg-base)',
      }}
    >
      {/* Header */}
      <Header
        lastUpdated={data.lastUpdated}
        totalCountries={data.global.totalCountries}
        totalTrends={data.global.totalTrends}
      />

      {/* Main Command Center */}
      <div
        style={{
          flex: 1,
          display: 'grid',
          gridTemplateColumns: '300px 1fr 270px',
          gridTemplateRows: '1fr 148px',
          gap: '10px',
          padding: '10px 12px 12px',
          overflow: 'hidden',
          minHeight: 0,
        }}
      >
        {/* Left Panel — Trend Rankings */}
        <div
          style={{
            gridRow: '1 / 2',
            overflow: 'hidden',
          }}
          className="animate-slide-left"
        >
          <TrendList data={data} />
        </div>

        {/* Center — World Map */}
        <div
          style={{
            gridRow: '1 / 2',
            overflow: 'hidden',
          }}
          className="animate-fade-in"
        >
          <Suspense fallback={<MapSkeleton />}>
            <WorldMap data={data} />
          </Suspense>
        </div>

        {/* Right Panel */}
        <div
          style={{
            gridRow: '1 / 2',
            overflow: 'hidden',
          }}
          className="animate-slide-right"
        >
          <RightPanel data={data} />
        </div>

        {/* Bottom Cards — spans all columns */}
        <div
          style={{
            gridColumn: '1 / -1',
            gridRow: '2 / 3',
            overflow: 'hidden',
          }}
          className="animate-slide-up"
        >
          <BottomCards data={data} />
        </div>
      </div>

      {/* Footer nav */}
      <nav
        style={{
          borderTop: '1px solid var(--border-subtle)',
          padding: '6px 16px',
          display: 'flex',
          gap: '16px',
          alignItems: 'center',
          background: 'var(--bg-surface)',
          flexShrink: 0,
        }}
      >
        {[
          { href: '/blog', label: 'Blog' },
          { href: '/about', label: 'About' },
          { href: '/contact', label: 'Contact' },
          { href: '/privacy-policy', label: 'Privacy' },
          { href: '/terms', label: 'Terms' },
          { href: '/cookie-policy', label: 'Cookies' },
          { href: '/dmca', label: 'DMCA' },
          { href: '/disclaimer', label: 'Disclaimer' },
          { href: '/editorial-policy', label: 'Editorial' },
        ].map((link) => (
          <a
            key={link.href}
            href={link.href}
            className="footer-nav-link"
            style={{
              fontSize: '11px',
              color: 'var(--text-muted)',
              textDecoration: 'none',
            }}
          >
            {link.label}
          </a>
        ))}
        <span
          style={{
            marginLeft: 'auto',
            fontSize: '11px',
            color: 'var(--text-muted)',
            fontFamily: 'Space Mono, monospace',
          }}
        >
          © {new Date().getFullYear()} TrendPulse
        </span>
      </nav>
    </div>
  );
}
