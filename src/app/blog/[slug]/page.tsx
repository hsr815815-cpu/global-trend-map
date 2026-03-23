import { Metadata } from 'next';
import { notFound } from 'next/navigation';
import Link from 'next/link';
import { promises as fs } from 'fs';
import path from 'path';

export const revalidate = 3600;

interface PostMeta {
  slug: string;
  title: string;
  date: string;
  lastUpdated?: string;
  excerpt: string;
  category?: string;
  language?: string;
  keyword?: string;
  type?: string;
  flag?: string;
  readingTime?: number;
  featured?: boolean;
  tags?: string[];
  youtubeAttribution?: boolean;
  wikipediaAttribution?: boolean;
  faqs?: Array<{ question: string; answer: string }>;
}

interface Props {
  params: { slug: string };
}

async function loadPostsIndex(): Promise<PostMeta[]> {
  try {
    const filePath = path.join(process.cwd(), 'public', 'data', 'posts-index.json');
    const raw = await fs.readFile(filePath, 'utf-8');
    const data = JSON.parse(raw);
    return Array.isArray(data) ? data : (data.posts ?? []);
  } catch {
    return [];
  }
}

async function getPostContent(slug: string, post: PostMeta): Promise<string> {
  try {
    const mdxPath = path.join(process.cwd(), 'public', 'blog', `${slug}.mdx`);
    const raw = await fs.readFile(mdxPath, 'utf-8');
    // Strip frontmatter (content between leading --- markers)
    const stripped = raw.replace(/^---[\s\S]*?---\s*/m, '');
    // Remove the first H1 heading if it duplicates the title
    return stripped.replace(/^#\s+.+\n?/, '').trim();
  } catch {
    return post.excerpt;
  }
}

function formatDate(dateStr: string): string {
  return new Date(dateStr).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  });
}

function estimateReadingTime(content: string): number {
  const words = content.trim().split(/\s+/).length;
  return Math.max(1, Math.ceil(words / 200));
}

function extractHeadings(content: string): Array<{ id: string; text: string; level: number }> {
  const headingRegex = /^(#{1,3})\s+(.+)$/gm;
  const headings: Array<{ id: string; text: string; level: number }> = [];
  let match;
  while ((match = headingRegex.exec(content)) !== null) {
    const level = match[1].length;
    const text = match[2];
    const id = text.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '');
    headings.push({ id, text, level });
  }
  return headings;
}

function renderMarkdown(content: string): string {
  return content
    .replace(/^### (.+)$/gm, '<h3>$1</h3>')
    .replace(/^## (.+)$/gm, '<h2>$1</h2>')
    .replace(/^# (.+)$/gm, '<h1>$1</h1>')
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.+?)\*/g, '<em>$1</em>')
    .replace(/`(.+?)`/g, '<code>$1</code>')
    .replace(/^\- (.+)$/gm, '<li>$1</li>')
    .replace(/(<li>.*<\/li>\n?)+/g, (match) => `<ul>${match}</ul>`)
    .replace(/^\d+\. (.+)$/gm, '<li>$1</li>')
    .replace(/^(?!<[hul]|<li|<\/ul|<p>|\n)(.*\S.*)$/gm, '<p>$1</p>')
    .replace(/\n{2,}/g, '\n');
}

export async function generateStaticParams() {
  const posts = await loadPostsIndex();
  return posts.map((p) => ({ slug: p.slug }));
}

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const posts = await loadPostsIndex();
  const post = posts.find((p) => p.slug === params.slug);

  if (!post) return { title: 'Article Not Found | TrendPulse Blog' };

  return {
    title: `${post.title} | TrendPulse Blog`,
    description: post.excerpt,
    openGraph: {
      type: 'article',
      title: post.title,
      description: post.excerpt,
      url: `https://global-trend-map-web.vercel.app/blog/${post.slug}`,
      publishedTime: post.date,
      modifiedTime: post.lastUpdated || post.date,
      authors: ['Global Trends Editorial Team'],
      tags: post.tags,
    },
    twitter: {
      card: 'summary_large_image',
      title: post.title,
      description: post.excerpt,
    },
    alternates: {
      canonical: `https://global-trend-map-web.vercel.app/blog/${post.slug}`,
    },
  };
}

const LANG_META: Record<string, { label: string; flag: string }> = {
  en: { label: 'English', flag: '🇺🇸' },
  kr: { label: '한국어',  flag: '🇰🇷' },
  jp: { label: '日本語',  flag: '🇯🇵' },
};

export default async function BlogPostPage({ params }: Props) {
  const posts = await loadPostsIndex();
  const post = posts.find((p) => p.slug === params.slug);

  if (!post) notFound();

  const content = await getPostContent(params.slug, post);
  const readingTime = post.readingTime || estimateReadingTime(content);
  const headings = extractHeadings(content);

  // Language variants: replace trailing -en / -kr / -jp
  const currentLang = post.language || 'en';
  const baseSlug = params.slug.replace(/-(?:en|kr|jp)$/, '');
  const langVariants = (['en', 'kr', 'jp'] as const).map((lang) => {
    const variantSlug = `${baseSlug}-${lang}`;
    const exists = posts.some((p) => p.slug === variantSlug);
    return { lang, slug: variantSlug, exists };
  }).filter((v) => v.exists);

  // Related posts: exclude current post and its language variants
  const variantSlugs = new Set(langVariants.map((v) => v.slug));
  const relatedPosts = posts
    .filter((p) => p.language === 'en' && !variantSlugs.has(p.slug))
    .slice(0, 3);

  // Structured data
  const articleSchema = {
    '@context': 'https://schema.org',
    '@type': 'Article',
    headline: post.title,
    description: post.excerpt,
    author: {
      '@type': 'Organization',
      name: 'Global Trends Editorial Team',
      url: 'https://global-trend-map-web.vercel.app/about',
    },
    publisher: {
      '@type': 'Organization',
      name: 'TrendPulse',
      url: 'https://global-trend-map-web.vercel.app',
      logo: { '@type': 'ImageObject', url: 'https://global-trend-map-web.vercel.app/logo.png' },
    },
    datePublished: post.date,
    dateModified: post.lastUpdated || post.date,
    url: `https://global-trend-map-web.vercel.app/blog/${post.slug}`,
    keywords: post.tags?.join(', '),
  };

  const faqSchema = post.faqs && post.faqs.length > 0
    ? {
        '@context': 'https://schema.org',
        '@type': 'FAQPage',
        mainEntity: post.faqs.map((faq) => ({
          '@type': 'Question',
          name: faq.question,
          acceptedAnswer: { '@type': 'Answer', text: faq.answer },
        })),
      }
    : null;

  return (
    <>
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(articleSchema) }}
      />
      {faqSchema && (
        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{ __html: JSON.stringify(faqSchema) }}
        />
      )}

      <div style={{ minHeight: '100vh', background: 'var(--bg-base)' }}>
        {/* Header */}
        <header
          style={{
            background: 'var(--bg-surface)',
            borderBottom: '1px solid var(--border-subtle)',
            padding: '14px 24px',
            display: 'flex',
            alignItems: 'center',
            gap: '12px',
          }}
        >
          <Link href="/" style={{ textDecoration: 'none', display: 'flex', alignItems: 'center', gap: '6px' }}>
            <div style={{ width: '24px', height: '24px', background: 'linear-gradient(135deg, #6366f1, #a855f7)', borderRadius: '6px', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '12px' }}>🌍</div>
            <span style={{ fontWeight: 800, fontSize: '16px', color: 'var(--text-primary)' }}>Trend<span style={{ color: '#818cf8' }}>Pulse</span></span>
          </Link>
          <span style={{ color: 'var(--border-normal)' }}>/</span>
          <Link href="/blog" style={{ fontSize: '13px', color: 'var(--text-secondary)', textDecoration: 'none' }}>Blog</Link>
          <span style={{ color: 'var(--border-normal)' }}>/</span>
          <span style={{ fontSize: '13px', color: 'var(--text-muted)', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{post.title}</span>
        </header>

        <div style={{ maxWidth: '1100px', margin: '0 auto', padding: '40px 24px', display: 'grid', gridTemplateColumns: '1fr 260px', gap: '40px' }}>
          {/* Main content */}
          <main>
            {/* Article header */}
            <header style={{ marginBottom: '32px' }}>
              {post.category && (
                <span
                  style={{
                    display: 'inline-block',
                    padding: '3px 12px',
                    background: 'rgba(99,102,241,0.15)',
                    border: '1px solid rgba(99,102,241,0.3)',
                    borderRadius: '100px',
                    fontSize: '11px',
                    fontWeight: 700,
                    color: '#818cf8',
                    letterSpacing: '0.08em',
                    textTransform: 'uppercase',
                    marginBottom: '16px',
                  }}
                >
                  {post.category}
                </span>
              )}

              <h1
                style={{
                  fontSize: '2rem',
                  fontWeight: 800,
                  color: 'var(--text-primary)',
                  lineHeight: 1.25,
                  marginBottom: '12px',
                }}
              >
                {post.title}
              </h1>

              {/* Language switcher */}
              {langVariants.length > 1 && (
                <div style={{ display: 'flex', gap: '6px', marginBottom: '16px', flexWrap: 'wrap' }}>
                  {langVariants.map(({ lang, slug }) => {
                    const meta = LANG_META[lang];
                    const isCurrent = lang === currentLang;
                    return isCurrent ? (
                      <span
                        key={lang}
                        style={{
                          display: 'inline-flex', alignItems: 'center', gap: '4px',
                          padding: '4px 12px',
                          background: 'rgba(99,102,241,0.2)',
                          border: '1px solid rgba(99,102,241,0.5)',
                          borderRadius: '100px',
                          fontSize: '12px', fontWeight: 700, color: '#818cf8',
                        }}
                      >
                        {meta.flag} {meta.label}
                      </span>
                    ) : (
                      <Link
                        key={lang}
                        href={`/blog/${slug}`}
                        style={{
                          display: 'inline-flex', alignItems: 'center', gap: '4px',
                          padding: '4px 12px',
                          background: 'var(--bg-elevated)',
                          border: '1px solid var(--border-subtle)',
                          borderRadius: '100px',
                          fontSize: '12px', fontWeight: 600, color: 'var(--text-secondary)',
                          textDecoration: 'none',
                        }}
                      >
                        {meta.flag} {meta.label}
                      </Link>
                    );
                  })}
                </div>
              )}

              <p style={{ fontSize: '16px', color: 'var(--text-secondary)', lineHeight: 1.7, marginBottom: '20px' }}>
                {post.excerpt}
              </p>

              <div
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '16px',
                  paddingBottom: '20px',
                  borderBottom: '1px solid var(--border-subtle)',
                  flexWrap: 'wrap',
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <div
                    style={{
                      width: '32px',
                      height: '32px',
                      borderRadius: '50%',
                      background: 'linear-gradient(135deg, #6366f1, #a855f7)',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      fontSize: '14px',
                    }}
                  >
                    ✍️
                  </div>
                  <div>
                    <div style={{ fontSize: '13px', fontWeight: 600, color: 'var(--text-primary)' }}>Global Trends Editorial Team</div>
                    <div style={{ fontSize: '11px', color: 'var(--text-muted)' }}>TrendPulse</div>
                  </div>
                </div>

                <div style={{ display: 'flex', gap: '12px', fontSize: '12px', color: 'var(--text-muted)' }}>
                  <span>Published {formatDate(post.date)}</span>
                  {post.lastUpdated && post.lastUpdated !== post.date && (
                    <span>· Updated {formatDate(post.lastUpdated)}</span>
                  )}
                  <span>· {readingTime} min read</span>
                </div>

                {/* Social share */}
                <div style={{ display: 'flex', gap: '6px', marginLeft: 'auto' }}>
                  {[
                    { label: 'X', href: `https://twitter.com/intent/tweet?text=${encodeURIComponent(post.title)}&url=${encodeURIComponent('https://global-trend-map-web.vercel.app/blog/' + post.slug)}` },
                    { label: 'FB', href: `https://www.facebook.com/sharer/sharer.php?u=${encodeURIComponent('https://global-trend-map-web.vercel.app/blog/' + post.slug)}` },
                    { label: 'Reddit', href: `https://reddit.com/submit?url=${encodeURIComponent('https://global-trend-map-web.vercel.app/blog/' + post.slug)}&title=${encodeURIComponent(post.title)}` },
                  ].map((btn) => (
                    <a
                      key={btn.label}
                      href={btn.href}
                      target="_blank"
                      rel="noopener noreferrer"
                      style={{
                        padding: '5px 10px',
                        background: 'var(--bg-elevated)',
                        border: '1px solid var(--border-subtle)',
                        borderRadius: '6px',
                        color: 'var(--text-secondary)',
                        fontSize: '11px',
                        fontWeight: 600,
                        textDecoration: 'none',
                      }}
                    >
                      {btn.label}
                    </a>
                  ))}
                </div>
              </div>
            </header>

            {/* Tags */}
            {post.tags && post.tags.length > 0 && (
              <div style={{ display: 'flex', gap: '6px', flexWrap: 'wrap', marginBottom: '28px' }}>
                {post.tags.map((tag) => (
                  <span
                    key={tag}
                    style={{
                      padding: '3px 10px',
                      background: 'var(--bg-elevated)',
                      border: '1px solid var(--border-subtle)',
                      borderRadius: '100px',
                      fontSize: '11px',
                      color: 'var(--text-muted)',
                    }}
                  >
                    #{tag}
                  </span>
                ))}
              </div>
            )}

            {/* Article body */}
            <div
              className="prose-dark"
              dangerouslySetInnerHTML={{ __html: renderMarkdown(content) }}
              style={{ marginBottom: '40px' }}
            />

            {/* Attributions */}
            {(post.youtubeAttribution || post.wikipediaAttribution) && (
              <div
                style={{
                  background: 'var(--bg-surface)',
                  border: '1px solid var(--border-subtle)',
                  borderRadius: '10px',
                  padding: '14px 16px',
                  marginBottom: '28px',
                  fontSize: '12px',
                  color: 'var(--text-muted)',
                }}
              >
                <strong style={{ color: 'var(--text-secondary)', display: 'block', marginBottom: '6px' }}>Data Sources & Attribution</strong>
                {post.youtubeAttribution && (
                  <p style={{ marginBottom: '4px' }}>Video data sourced via YouTube Data API v3. Built with YouTube Data API. YouTube is a trademark of Google LLC.</p>
                )}
                {post.wikipediaAttribution && (
                  <p>Background information sourced from Wikipedia, available under Creative Commons Attribution-ShareAlike License (CC BY-SA).</p>
                )}
              </div>
            )}

            {/* FAQ section */}
            {post.faqs && post.faqs.length > 0 && (
              <div style={{ marginBottom: '40px' }}>
                <h2 style={{ fontSize: '1.25rem', fontWeight: 700, color: 'var(--text-primary)', marginBottom: '16px' }}>Frequently Asked Questions</h2>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                  {post.faqs.map((faq, i) => (
                    <details
                      key={i}
                      style={{
                        background: 'var(--bg-card)',
                        border: '1px solid var(--border-subtle)',
                        borderRadius: '10px',
                        padding: '14px 16px',
                      }}
                    >
                      <summary
                        style={{
                          fontWeight: 600,
                          color: 'var(--text-primary)',
                          fontSize: '14px',
                          cursor: 'pointer',
                        }}
                      >
                        {faq.question}
                      </summary>
                      <p style={{ marginTop: '10px', color: 'var(--text-secondary)', fontSize: '14px', lineHeight: 1.7 }}>
                        {faq.answer}
                      </p>
                    </details>
                  ))}
                </div>
              </div>
            )}

            {/* Related posts */}
            {relatedPosts.length > 0 && (
              <div>
                <h2 style={{ fontSize: '1.1rem', fontWeight: 700, color: 'var(--text-primary)', marginBottom: '14px' }}>Related Articles</h2>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                  {relatedPosts.map((related) => (
                    <Link
                      key={related.slug}
                      href={`/blog/${related.slug}`}
                      style={{
                        display: 'flex',
                        gap: '12px',
                        alignItems: 'flex-start',
                        padding: '14px',
                        background: 'var(--bg-card)',
                        border: '1px solid var(--border-subtle)',
                        borderRadius: '10px',
                        textDecoration: 'none',
                      }}
                    >
                      <div style={{ flex: 1 }}>
                        <div style={{ fontSize: '13px', fontWeight: 600, color: 'var(--text-primary)', marginBottom: '4px' }}>{related.title}</div>
                        <div style={{ fontSize: '11px', color: 'var(--text-muted)' }}>{formatDate(related.date)} · {related.readingTime} min read</div>
                      </div>
                      <span style={{ color: 'var(--text-muted)', fontSize: '16px' }}>→</span>
                    </Link>
                  ))}
                </div>
              </div>
            )}
          </main>

          {/* Sidebar — Table of contents */}
          <aside style={{ position: 'sticky', top: '20px', alignSelf: 'start' }}>
            {headings.length > 0 && (
              <div
                style={{
                  background: 'var(--bg-card)',
                  border: '1px solid var(--border-subtle)',
                  borderRadius: '12px',
                  padding: '16px',
                  marginBottom: '16px',
                }}
              >
                <div style={{ fontSize: '11px', fontFamily: 'Space Mono, monospace', fontWeight: 700, letterSpacing: '0.1em', color: 'var(--text-muted)', textTransform: 'uppercase', marginBottom: '12px' }}>
                  Table of Contents
                </div>
                <nav>
                  {headings.map((h) => (
                    <a
                      key={h.id}
                      href={`#${h.id}`}
                      style={{
                        display: 'block',
                        padding: '5px 0',
                        fontSize: '12px',
                        color: 'var(--text-secondary)',
                        textDecoration: 'none',
                        borderLeft: h.level === 2 ? '2px solid var(--border-subtle)' : 'none',
                        paddingLeft: h.level === 2 ? '8px' : h.level === 3 ? '20px' : '0',
                      }}
                    >
                      {h.text}
                    </a>
                  ))}
                </nav>
              </div>
            )}

            {/* Back to map CTA */}
            <div
              style={{
                background: 'linear-gradient(135deg, rgba(99,102,241,0.15), rgba(168,85,247,0.15))',
                border: '1px solid rgba(99,102,241,0.3)',
                borderRadius: '12px',
                padding: '16px',
                textAlign: 'center',
              }}
            >
              <div style={{ fontSize: '28px', marginBottom: '8px' }}>🌍</div>
              <div style={{ fontSize: '13px', fontWeight: 600, color: 'var(--text-primary)', marginBottom: '8px' }}>
                Explore live trends
              </div>
              <div style={{ fontSize: '12px', color: 'var(--text-secondary)', marginBottom: '12px' }}>
                See what 142 countries are searching for right now
              </div>
              <Link
                href="/"
                style={{
                  display: 'block',
                  padding: '10px',
                  background: 'var(--accent-indigo)',
                  borderRadius: '8px',
                  color: 'white',
                  fontSize: '13px',
                  fontWeight: 600,
                  textDecoration: 'none',
                }}
              >
                Open Map →
              </Link>
            </div>
          </aside>
        </div>

        <footer
          style={{
            borderTop: '1px solid var(--border-subtle)',
            padding: '20px 24px',
            textAlign: 'center',
            fontSize: '12px',
            color: 'var(--text-muted)',
            background: 'var(--bg-surface)',
          }}
        >
          © {new Date().getFullYear()} TrendPulse ·{' '}
          <Link href="/" style={{ color: 'var(--text-muted)' }}>Home</Link> ·{' '}
          <Link href="/blog" style={{ color: 'var(--text-muted)' }}>Blog</Link> ·{' '}
          <Link href="/privacy-policy" style={{ color: 'var(--text-muted)' }}>Privacy</Link>
        </footer>
      </div>
    </>
  );
}
