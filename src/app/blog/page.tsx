import { Metadata } from 'next';
import Link from 'next/link';
import { promises as fs } from 'fs';
import path from 'path';

export const revalidate = 3600;

export const metadata: Metadata = {
  title: 'Trend Insights Blog — TrendPulse',
  description:
    'In-depth analysis of global search trends, viral topics, and what the world is searching for. Written by the Global Trends Editorial Team.',
  openGraph: {
    title: 'Trend Insights Blog — TrendPulse',
    description: 'Deep dives into global search trends and viral topics from 36 countries.',
    url: 'https://global-trend-map-web.vercel.app/blog',
  },
  alternates: { canonical: 'https://global-trend-map-web.vercel.app/blog' },
};

interface PostMeta {
  slug: string;
  title: string;
  date: string;
  lastUpdated?: string;
  excerpt: string;
  category?: string;
  language?: string;
  readingTime?: number;
  featured?: boolean;
  tags?: string[];
}

const CATEGORY_COLORS: Record<string, string> = {
  sports: '#10b981', tech: '#06b6d4', music: '#a855f7',
  news: '#f59e0b', movies: '#f43f5e', finance: '#22c55e',
};

const CATEGORY_ICONS: Record<string, string> = {
  sports: '⚽', tech: '💻', music: '🎵',
  news: '📰', movies: '🎬', finance: '📈',
};

async function loadPostsIndex(): Promise<PostMeta[]> {
  try {
    const filePath = path.join(process.cwd(), 'public', 'data', 'posts-index.json');
    const raw = await fs.readFile(filePath, 'utf-8');
    const data = JSON.parse(raw);
    const posts: PostMeta[] = Array.isArray(data) ? data : (data.posts ?? []);
    return posts;
  } catch { return []; }
}

function formatDate(dateStr: string): string {
  return new Date(dateStr).toLocaleDateString('en-US', {
    year: 'numeric', month: 'long', day: 'numeric',
  });
}

const LANG_LABELS: { code: string; flag: string; label: string }[] = [
  { code: 'en', flag: '🇺🇸', label: 'EN' },
  { code: 'zh', flag: '🇨🇳', label: 'ZH' },
  { code: 'es', flag: '🇪🇸', label: 'ES' },
  { code: 'pt', flag: '🇧🇷', label: 'PT' },
  { code: 'fr', flag: '🇫🇷', label: 'FR' },
  { code: 'de', flag: '🇩🇪', label: 'DE' },
  { code: 'kr', flag: '🇰🇷', label: 'KR' },
  { code: 'jp', flag: '🇯🇵', label: 'JP' },
];

const VALID_LANGS = LANG_LABELS.map((l) => l.code);

export default async function BlogPage({ searchParams }: { searchParams: { lang?: string } }) {
  const lang = searchParams.lang && VALID_LANGS.includes(searchParams.lang) ? searchParams.lang : 'en';
  const allPosts = await loadPostsIndex();
  const posts = allPosts.filter((p) => {
    const postLang = p.language || 'en';
    return postLang === lang;
  });
  const featured = posts.filter((p) => p.featured);
  const rest = posts.filter((p) => !p.featured);

  return (
    <div style={{ minHeight: '100vh', background: 'var(--bg-base)' }}>
      <style>{`
        .blog-card { transition: background 0.15s ease, border-color 0.15s ease, transform 0.15s ease; }
        .blog-card:hover { background: var(--bg-elevated) !important; border-color: var(--border-normal) !important; }
        .featured-card:hover { transform: translateY(-2px); }
        .lang-tab { display: inline-flex; align-items: center; gap: 5px; padding: 6px 16px; border-radius: 100px; font-size: 13px; font-weight: 700; text-decoration: none; border: 1px solid var(--border-normal); color: var(--text-secondary); background: var(--bg-surface); transition: all 0.15s ease; }
        .lang-tab.active { background: rgba(99,102,241,0.2); border-color: rgba(99,102,241,0.5); color: #818cf8; }
        .lang-tab:hover:not(.active) { border-color: var(--border-normal); background: var(--bg-elevated); }
      `}</style>

      <header style={{ background: 'var(--bg-surface)', borderBottom: '1px solid var(--border-subtle)', padding: '14px 24px' }}>
        <Link href="/" style={{ display: 'flex', alignItems: 'center', gap: '8px', textDecoration: 'none', width: 'fit-content' }}>
          <div style={{ width: '26px', height: '26px', background: 'linear-gradient(135deg, #6366f1, #a855f7)', borderRadius: '7px', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '13px' }}>🌍</div>
          <span style={{ fontWeight: 800, fontSize: '17px', color: 'var(--text-primary)' }}>Trend<span style={{ color: '#818cf8' }}>Pulse</span></span>
        </Link>
      </header>

      <main style={{ maxWidth: '900px', margin: '0 auto', padding: '40px 24px' }}>
        <div style={{ marginBottom: '32px', textAlign: 'center' }}>
          <div style={{ display: 'inline-flex', alignItems: 'center', gap: '6px', padding: '4px 14px', background: 'rgba(99,102,241,0.15)', border: '1px solid rgba(99,102,241,0.3)', borderRadius: '100px', fontSize: '11px', fontWeight: 700, color: '#818cf8', letterSpacing: '0.1em', marginBottom: '16px' }}>
            📊 TREND INSIGHTS
          </div>
          <h1 style={{ fontSize: '2.25rem', fontWeight: 800, color: 'var(--text-primary)', marginBottom: '12px', lineHeight: 1.2 }}>
            Global Trend Analysis
          </h1>
          <p style={{ fontSize: '16px', color: 'var(--text-secondary)', maxWidth: '600px', margin: '0 auto 20px' }}>
            Deep dives into what 36 countries are searching for — written by the Global Trends Editorial Team.
          </p>
          {/* Language tabs — 4×2 grid */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, auto)', gap: '8px', justifyContent: 'center' }}>
            {LANG_LABELS.map(({ code, flag, label }) => (
              <Link key={code} href={`?lang=${code}`} className={`lang-tab${lang === code ? ' active' : ''}`}>
                {flag} {label}
              </Link>
            ))}
          </div>
        </div>

        {featured.length > 0 && (
          <section style={{ marginBottom: '40px' }}>
            <h2 style={{ fontSize: '13px', fontFamily: 'Space Mono, monospace', fontWeight: 700, letterSpacing: '0.1em', textTransform: 'uppercase', color: 'var(--text-muted)', marginBottom: '16px' }}>
              Featured Articles
            </h2>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
              {featured.map((post) => {
                const color = post.category ? (CATEGORY_COLORS[post.category] || '#6366f1') : '#6366f1';
                const icon = post.category ? (CATEGORY_ICONS[post.category] || '📊') : '📊';
                return (
                  <Link key={post.slug} href={`/blog/${post.slug}`} style={{ textDecoration: 'none' }}>
                    <article className="blog-card featured-card" style={{ background: 'var(--bg-card)', border: '1px solid var(--border-subtle)', borderRadius: '16px', padding: '24px', position: 'relative', overflow: 'hidden' }}>
                      <div style={{ position: 'absolute', top: 0, left: 0, right: 0, height: '3px', background: color }} />
                      <div style={{ display: 'flex', gap: '10px', alignItems: 'center', marginBottom: '12px' }}>
                        {post.category && (
                          <span style={{ padding: '3px 10px', background: `${color}18`, border: `1px solid ${color}44`, borderRadius: '100px', fontSize: '11px', fontWeight: 700, color }}>
                            {icon} {post.category.toUpperCase()}
                          </span>
                        )}
                        <span style={{ padding: '3px 10px', background: 'rgba(99,102,241,0.15)', border: '1px solid rgba(99,102,241,0.3)', borderRadius: '100px', fontSize: '10px', fontWeight: 700, color: '#818cf8' }}>
                          ★ FEATURED
                        </span>
                        {post.readingTime && <span style={{ fontSize: '11px', color: 'var(--text-muted)', marginLeft: 'auto' }}>{post.readingTime} min read</span>}
                      </div>
                      <h2 style={{ fontSize: '1.25rem', fontWeight: 700, color: 'var(--text-primary)', marginBottom: '10px', lineHeight: 1.3 }}>{post.title}</h2>
                      <p style={{ fontSize: '14px', color: 'var(--text-secondary)', lineHeight: 1.7, marginBottom: '16px' }}>{post.excerpt}</p>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '12px', fontSize: '12px', color: 'var(--text-muted)', flexWrap: 'wrap' }}>
                        <span>Global Trends Editorial Team</span>
                        <span>·</span>
                        <span>{formatDate(post.date)}</span>
                        {post.tags && post.tags.length > 0 && (
                          <>
                            <span>·</span>
                            <div style={{ display: 'flex', gap: '4px' }}>
                              {post.tags.slice(0, 3).map((tag) => (
                                <span key={tag} style={{ padding: '1px 6px', background: 'var(--bg-elevated)', borderRadius: '4px', fontSize: '10px', color: 'var(--text-muted)' }}>#{tag}</span>
                              ))}
                            </div>
                          </>
                        )}
                        <span style={{ marginLeft: 'auto', color: '#818cf8', fontSize: '13px', fontWeight: 600 }}>Read →</span>
                      </div>
                    </article>
                  </Link>
                );
              })}
            </div>
          </section>
        )}

        {rest.length > 0 && (
          <section>
            <h2 style={{ fontSize: '13px', fontFamily: 'Space Mono, monospace', fontWeight: 700, letterSpacing: '0.1em', textTransform: 'uppercase', color: 'var(--text-muted)', marginBottom: '16px' }}>
              Recent Articles
            </h2>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
              {rest.map((post) => {
                const color = post.category ? (CATEGORY_COLORS[post.category] || '#6366f1') : '#6366f1';
                const icon = post.category ? (CATEGORY_ICONS[post.category] || '📊') : '📊';
                return (
                  <Link key={post.slug} href={`/blog/${post.slug}`} style={{ textDecoration: 'none' }}>
                    <article className="blog-card" style={{ background: 'var(--bg-card)', border: '1px solid var(--border-subtle)', borderRadius: '12px', padding: '16px 20px', display: 'flex', gap: '16px', alignItems: 'flex-start' }}>
                      <div style={{ width: '40px', height: '40px', borderRadius: '10px', background: `${color}18`, border: `1px solid ${color}33`, display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '18px', flexShrink: 0 }}>
                        {icon}
                      </div>
                      <div style={{ flex: 1, minWidth: 0 }}>
                        <h3 style={{ fontSize: '14px', fontWeight: 700, color: 'var(--text-primary)', marginBottom: '5px', lineHeight: 1.3 }}>{post.title}</h3>
                        <p style={{ fontSize: '12px', color: 'var(--text-secondary)', lineHeight: 1.6, marginBottom: '8px', overflow: 'hidden', display: '-webkit-box', WebkitLineClamp: 2, WebkitBoxOrient: 'vertical' }}>{post.excerpt}</p>
                        <div style={{ fontSize: '11px', color: 'var(--text-muted)', display: 'flex', gap: '8px' }}>
                          <span>{formatDate(post.date)}</span>
                          {post.readingTime && <><span>·</span><span>{post.readingTime} min read</span></>}
                        </div>
                      </div>
                      <span style={{ fontSize: '16px', color: 'var(--text-muted)', flexShrink: 0, marginTop: '8px' }}>→</span>
                    </article>
                  </Link>
                );
              })}
            </div>
          </section>
        )}

        {posts.length === 0 && (
          <div style={{ textAlign: 'center', padding: '60px 20px', color: 'var(--text-muted)' }}>
            <div style={{ fontSize: '48px', marginBottom: '16px' }}>✍️</div>
            <p>Articles are being prepared. Check back soon!</p>
          </div>
        )}
      </main>

      <footer style={{ borderTop: '1px solid var(--border-subtle)', padding: '20px 24px', textAlign: 'center', fontSize: '12px', color: 'var(--text-muted)', background: 'var(--bg-surface)' }}>
        © {new Date().getFullYear()} TrendPulse · <Link href="/" style={{ color: 'var(--text-muted)' }}>Home</Link> · <Link href="/about" style={{ color: 'var(--text-muted)' }}>About</Link> · <Link href="/privacy-policy" style={{ color: 'var(--text-muted)' }}>Privacy</Link>
      </footer>
    </div>
  );
}
