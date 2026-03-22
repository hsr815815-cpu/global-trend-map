import { Metadata } from 'next';
import { notFound } from 'next/navigation';
import Link from 'next/link';
import {
  loadTrendsData,
  getTemperatureLabel,
  getTemperatureColor,
  getTemperatureGradient,
  getCountryTemperature,
  CATEGORY_ICONS,
  getVelocityIcon,
  getVelocityColor,
  getTrendBadge,
} from '@/lib/trends';

export const revalidate = 3600;

interface Props {
  params: { code: string };
}

export async function generateStaticParams() {
  const data = await loadTrendsData();
  return Object.keys(data.countries).map((code) => ({
    code: code.toLowerCase(),
  }));
}

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const data = await loadTrendsData();
  const code = params.code.toUpperCase();
  const country = data.countries[code];

  if (!country) {
    return { title: 'Country Not Found | TrendPulse' };
  }

  const topKeyword = country.trends[0]?.keyword || 'Trending Topics';
  const avgTemp = getCountryTemperature(data, code);
  const tempLabel = getTemperatureLabel(avgTemp);

  return {
    title: `${country.flag} ${country.name} Trending Now — ${tempLabel} (${avgTemp}°T)`,
    description: `Real-time trending searches in ${country.name}. Top trend: "${topKeyword}". ${country.trends.length} trending topics tracked. Trend temperature: ${avgTemp}°T (${tempLabel}).`,
    openGraph: {
      title: `${country.flag} ${country.name} — Live Trends`,
      description: `See what's trending in ${country.name} right now. Current trend temperature: ${avgTemp}°T.`,
      url: `https://global-trend-map-web.vercel.app/country/${params.code}`,
    },
    alternates: {
      canonical: `https://global-trend-map-web.vercel.app/country/${params.code}`,
    },
  };
}

export default async function CountryPage({ params }: Props) {
  const data = await loadTrendsData();
  const code = params.code.toUpperCase();
  const country = data.countries[code];

  if (!country) {
    notFound();
  }

  const avgTemp = getCountryTemperature(data, code);
  const tempLabel = getTemperatureLabel(avgTemp);
  const tempColor = getTemperatureColor(avgTemp);
  const tempGradient = getTemperatureGradient(avgTemp);

  // Structured data for the country page
  const schema = {
    '@context': 'https://schema.org',
    '@type': 'WebPage',
    name: `${country.name} Trending Searches`,
    description: `Real-time trending searches in ${country.name}`,
    url: `https://global-trend-map-web.vercel.app/country/${params.code}`,
    about: {
      '@type': 'Country',
      name: country.name,
    },
  };

  return (
    <>
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(schema) }}
      />

      <div
        style={{
          minHeight: '100vh',
          background: 'var(--bg-base)',
          display: 'flex',
          flexDirection: 'column',
        }}
      >
        {/* Header */}
        <header
          style={{
            background: 'var(--bg-surface)',
            borderBottom: '1px solid var(--border-subtle)',
            padding: '14px 24px',
            display: 'flex',
            alignItems: 'center',
            gap: '16px',
          }}
        >
          <Link
            href="/"
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
              textDecoration: 'none',
              color: 'var(--text-secondary)',
              fontSize: '13px',
            }}
          >
            ← Back to Map
          </Link>
          <span style={{ color: 'var(--border-normal)' }}>|</span>
          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              fontSize: '15px',
              fontWeight: 700,
              color: 'var(--text-primary)',
            }}
          >
            <span style={{ fontSize: '22px' }}>{country.flag}</span>
            {country.name}
          </div>
          <span
            style={{
              marginLeft: 'auto',
              fontFamily: 'Space Mono, monospace',
              fontSize: '11px',
              color: 'var(--text-muted)',
            }}
          >
            ISO: {code}
          </span>
        </header>

        {/* Content */}
        <main style={{ flex: 1, maxWidth: '900px', margin: '0 auto', padding: '32px 24px', width: '100%' }}>
          {/* Country hero */}
          <div
            style={{
              background: 'var(--bg-card)',
              border: '1px solid var(--border-subtle)',
              borderRadius: '20px',
              padding: '28px',
              marginBottom: '24px',
              position: 'relative',
              overflow: 'hidden',
            }}
          >
            {/* Background gradient */}
            <div
              style={{
                position: 'absolute',
                top: 0,
                right: 0,
                width: '200px',
                height: '200px',
                background: `radial-gradient(circle, ${tempColor}18 0%, transparent 70%)`,
                pointerEvents: 'none',
              }}
            />

            <div style={{ display: 'flex', alignItems: 'center', gap: '20px', position: 'relative' }}>
              <span style={{ fontSize: '64px', lineHeight: 1 }}>{country.flag}</span>

              <div>
                <h1
                  style={{
                    fontSize: '2rem',
                    fontWeight: 800,
                    color: 'var(--text-primary)',
                    marginBottom: '8px',
                    lineHeight: 1.2,
                  }}
                >
                  {country.name}
                </h1>
                <div style={{ display: 'flex', gap: '12px', flexWrap: 'wrap', alignItems: 'center' }}>
                  <div
                    style={{
                      display: 'flex',
                      alignItems: 'baseline',
                      gap: '4px',
                    }}
                  >
                    <span
                      style={{
                        fontFamily: 'Space Mono, monospace',
                        fontSize: '28px',
                        fontWeight: 700,
                        color: tempColor,
                      }}
                    >
                      {avgTemp}°T
                    </span>
                    <span
                      style={{
                        padding: '3px 10px',
                        borderRadius: '100px',
                        background: `${tempColor}22`,
                        border: `1px solid ${tempColor}55`,
                        fontSize: '11px',
                        fontWeight: 700,
                        color: tempColor,
                        letterSpacing: '0.06em',
                      }}
                    >
                      {tempLabel}
                    </span>
                  </div>
                  <span style={{ color: 'var(--text-muted)', fontSize: '13px' }}>
                    {country.trends.length} trends tracked
                  </span>
                </div>
              </div>
            </div>

            {/* Temperature bar */}
            <div
              style={{
                marginTop: '20px',
                height: '6px',
                background: 'var(--border-subtle)',
                borderRadius: '3px',
                overflow: 'hidden',
              }}
            >
              <div
                style={{
                  height: '100%',
                  width: `${avgTemp}%`,
                  background: tempGradient,
                  borderRadius: '3px',
                  transition: 'width 1.5s ease',
                }}
              />
            </div>
          </div>

          {/* Trend list */}
          <h2
            style={{
              fontSize: '16px',
              fontWeight: 700,
              color: 'var(--text-primary)',
              marginBottom: '14px',
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
            }}
          >
            <span>🔥</span>
            Trending Now in {country.name}
          </h2>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', marginBottom: '32px' }}>
            {country.trends.map((trend) => {
              const badge = getTrendBadge(trend, code);
              const tColor = getTemperatureColor(trend.temperature);
              const isTop3 = trend.rank <= 3;

              return (
                <div
                  key={trend.rank}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '14px',
                    padding: '14px 16px',
                    background: 'var(--bg-card)',
                    border: '1px solid var(--border-subtle)',
                    borderRadius: '12px',
                    transition: 'all 0.15s ease',
                  }}
                >
                  {/* Rank */}
                  <div
                    style={{
                      width: '36px',
                      height: '36px',
                      borderRadius: '50%',
                      background: isTop3
                        ? 'linear-gradient(135deg, #6366f1, #a855f7)'
                        : 'var(--bg-elevated)',
                      border: `1px solid ${isTop3 ? 'transparent' : 'var(--border-normal)'}`,
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      fontSize: '14px',
                      fontWeight: 700,
                      color: isTop3 ? 'white' : 'var(--text-muted)',
                      fontFamily: 'Space Mono, monospace',
                      flexShrink: 0,
                    }}
                  >
                    {trend.rank}
                  </div>

                  {/* Keyword info */}
                  <div style={{ flex: 1, minWidth: 0 }}>
                    <div
                      style={{
                        display: 'flex',
                        alignItems: 'center',
                        gap: '8px',
                        marginBottom: '6px',
                        flexWrap: 'wrap',
                      }}
                    >
                      <span
                        style={{
                          fontSize: '15px',
                          fontWeight: 700,
                          color: 'var(--text-primary)',
                        }}
                      >
                        {trend.keyword}
                      </span>
                      {badge && (
                        <span className={`badge badge-${badge.toLowerCase()}`}>
                          {badge}
                        </span>
                      )}
                    </div>

                    <div
                      style={{
                        display: 'flex',
                        alignItems: 'center',
                        gap: '12px',
                        fontSize: '12px',
                        color: 'var(--text-muted)',
                      }}
                    >
                      <span>
                        {CATEGORY_ICONS[trend.category]} {trend.category}
                      </span>
                      <span>📊 {trend.volume} searches</span>
                    </div>

                    {/* Bar */}
                    <div
                      style={{
                        marginTop: '8px',
                        height: '4px',
                        background: 'var(--border-subtle)',
                        borderRadius: '2px',
                        overflow: 'hidden',
                      }}
                    >
                      <div
                        style={{
                          height: '100%',
                          width: `${trend.temperature}%`,
                          background: `linear-gradient(to right, #6366f1, ${tColor})`,
                          borderRadius: '2px',
                        }}
                      />
                    </div>
                  </div>

                  {/* Right side stats */}
                  <div
                    style={{
                      display: 'flex',
                      flexDirection: 'column',
                      alignItems: 'flex-end',
                      gap: '4px',
                      flexShrink: 0,
                    }}
                  >
                    <span
                      style={{
                        fontFamily: 'Space Mono, monospace',
                        fontSize: '16px',
                        fontWeight: 700,
                        color: tColor,
                      }}
                    >
                      {trend.temperature}°
                    </span>
                    <span
                      style={{
                        fontSize: '14px',
                        color: getVelocityColor(trend.velocity),
                      }}
                    >
                      {getVelocityIcon(trend.velocity)}
                    </span>
                  </div>
                </div>
              );
            })}
          </div>

          {/* Related countries CTA */}
          <div
            style={{
              background: 'var(--bg-card)',
              border: '1px solid var(--border-subtle)',
              borderRadius: '16px',
              padding: '20px',
              textAlign: 'center',
            }}
          >
            <p style={{ color: 'var(--text-secondary)', fontSize: '14px', marginBottom: '14px' }}>
              Explore trends from other countries on the global map
            </p>
            <Link
              href="/"
              style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: '6px',
                padding: '10px 24px',
                background: 'var(--accent-indigo)',
                borderRadius: '10px',
                color: 'white',
                fontSize: '14px',
                fontWeight: 600,
                textDecoration: 'none',
              }}
            >
              🌍 Open World Map
            </Link>
          </div>
        </main>

        {/* Footer */}
        <footer
          style={{
            borderTop: '1px solid var(--border-subtle)',
            padding: '16px 24px',
            textAlign: 'center',
            fontSize: '12px',
            color: 'var(--text-muted)',
            background: 'var(--bg-surface)',
          }}
        >
          © {new Date().getFullYear()} TrendPulse ·{' '}
          <Link href="/privacy-policy" style={{ color: 'var(--text-muted)' }}>Privacy</Link> ·{' '}
          <Link href="/terms" style={{ color: 'var(--text-muted)' }}>Terms</Link>
        </footer>
      </div>
    </>
  );
}
