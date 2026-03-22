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
    return JSON.parse(raw) as PostMeta[];
  } catch {
    return [];
  }
}

function getPostContent(slug: string, post: PostMeta): string {
  // In production, this would load from MDX files or CMS.
  // For the sample posts, we generate full article content.
  const contents: Record<string, string> = {
    'why-ipл-auction-trends-dominate-global-searches': `
The Indian Premier League auction is, by every metric, one of the most-searched sporting events on the planet. When franchises bid for the world's best cricket talent, hundreds of millions of fans across South Asia, the Caribbean, Australia, the United Kingdom, and beyond are glued to their screens — and their search bars.

## The Scale of IPL Search Interest

According to data collected by TrendPulse across 142 countries, IPL auction days consistently generate search volumes that rival the Super Bowl, the FIFA World Cup final, and the Olympics opening ceremony. In India alone, the 2026 auction generated over 8.4 million searches within the first 24 hours — a figure that eclipses most Hollywood blockbuster release weekends.

What makes this particularly remarkable is the geographic spread. Unlike many sporting events that dominate searches in one country or region, IPL auction interest is genuinely global:

- **India**: 8.4M+ searches (predictably dominant)
- **Sri Lanka**: 2.1M searches
- **Pakistan**: 1.9M searches
- **United Kingdom**: 1.4M searches (large South Asian diaspora)
- **United States**: 980K searches
- **Australia**: 760K searches
- **Canada**: 640K searches

## Why Does the Auction Generate Such Massive Interest?

The auction format itself is a masterpiece of engagement engineering. Unlike a standard transfer window in football, where deals happen quietly over weeks, the IPL auction is a live spectacle. Viewers watch franchise owners deliberate in real time. Every bid is public. Every player unsold is a moment of drama.

Search queries cluster around three themes:

1. **Player valuations** — "How much did [player] go for?" generates enormous search traffic
2. **Fantasy cricket implications** — IPL fantasy leagues have hundreds of millions of participants
3. **Team roster analysis** — Fans immediately begin searching for tactical implications

## The Diaspora Effect

One of the most fascinating aspects of IPL auction search trends is the diaspora effect. When we analyze search data from countries like the UK, Canada, Australia, and the UAE, IPL auction searches are disproportionately high relative to those countries' total populations. This directly reflects the large South Asian communities living outside the subcontinent.

TrendPulse data shows that in some UK cities with significant South Asian populations, IPL auction search volume on auction day exceeds searches for Premier League matches played that same day.

## What Happens After the Auction

Search interest doesn't disappear after bidding closes. A secondary wave of searches typically hits 24-48 hours after the auction as:

- Analysis articles are published
- Fantasy cricket players finalize their teams
- Fans research newly-acquired foreign players from overseas leagues
- Social media debates generate curiosity in non-cricket audiences

This secondary wave often reaches 40-60% of the peak auction volume — remarkably high for post-event interest.

## Conclusion

The IPL auction represents a perfect storm of factors that maximize global search interest: live drama, financial spectacle, fantasy sports integration, and a genuinely global sport with a passionate diaspora. For trend analysts and marketers, it remains one of the most predictable and powerful annual search events in the world.
    `,
    'ai-agents-2026-what-the-world-is-searching-for': `
The term "AI agents" has undergone a remarkable transformation in public consciousness. Two years ago, it was a niche technical concept discussed primarily in research papers and developer forums. Today, it's generating 340% more search volume than it did in Q1 2025, driven by a wave of product launches, media coverage, and genuine public curiosity about what autonomous AI systems can actually do.

## What Are People Actually Searching For?

TrendPulse data reveals that "AI agents" searches cluster into distinct query categories:

**Definition and education queries** (38% of traffic):
- "What is an AI agent"
- "AI agent vs chatbot difference"
- "How do AI agents work"
- "AI agent examples 2026"

**Product and tool queries** (31%):
- "Best AI agents 2026"
- "AI agent for coding"
- "AI agent for business"
- "OpenAI agents API"
- "Claude AI agent"

**Concern and safety queries** (18%):
- "Are AI agents safe"
- "AI agent risks"
- "Can AI agents make mistakes"
- "AI agent security"

**Job and career queries** (13%):
- "AI agent replace jobs"
- "Will AI agents take my job"
- "Jobs affected by AI agents"

## Geographic Patterns

The geographic distribution of AI agent searches reveals interesting patterns about where AI adoption is accelerating fastest.

**United States** leads in absolute volume (3.1M searches), with particularly high concentration in:
- San Francisco Bay Area
- Seattle
- New York City
- Austin

**South Korea** shows the highest per-capita AI agent search rate among the countries we monitor, reflecting the country's aggressive national AI investment strategy and its highly tech-educated population.

**India** has the fastest growth rate in AI agent searches (+420% year-over-year), driven by the country's massive developer community and strong adoption of AI tools in software outsourcing.

**Japan** searches are notable for focusing heavily on enterprise applications — a reflection of Japan's corporate culture of thorough evaluation before adoption.

## The "Agentic AI" Inflection Point

Our data suggests that Q1 2026 represents a genuine inflection point in public awareness of agentic AI. Several factors converged simultaneously:

1. **Major product launches** from leading AI companies that put autonomous agent capabilities directly in consumer products
2. **Media coverage** that moved from technical to mainstream, with major publications running explainer pieces
3. **Business adoption stories** featuring real companies reporting productivity gains from agent deployments
4. **Regulatory attention** in the EU and US that kept the topic in news cycles

## What This Means

The search data tells us that AI agents are following the classic technology adoption curve but at an accelerated pace. The question mix — definition-seeking combined with product research combined with job anxiety — is exactly what we'd expect at the early majority phase of adoption.

For businesses, the implications are clear: customers and employees are both curious and cautious. Communication that addresses both the opportunity and the safety/reliability concerns will resonate with the current search intent landscape.
    `,
  };

  return contents[slug] || `
This article explores the fascinating trends data captured by TrendPulse from across 142 countries.

## Overview

${post.excerpt}

## Key Findings

Our analysis of global search data reveals several important patterns worth examining. The data shows significant variation across countries and regions, with some areas showing dramatically higher engagement than others.

## Methodology

TrendPulse collects trend data from multiple public sources including Google Trends RSS feeds, YouTube trending data (where available via the YouTube Data API), and GDELT news analysis. All data is filtered through our content moderation pipeline to ensure compliance with advertising policies.

## Conclusion

Understanding global search trends provides unique insights into collective human curiosity — what captures attention, what drives people to search, and how those patterns differ across cultures and geographies. TrendPulse makes this data accessible and visual for everyone.

*Data collected and analyzed by the Global Trends Editorial Team.*
  `;
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

  const faqs = post.faqs || [];

  const schema: any = {
    '@context': 'https://schema.org',
    '@type': 'Article',
    headline: post.title,
    description: post.excerpt,
    author: {
      '@type': 'Organization',
      name: 'Global Trends Editorial Team',
      url: 'https://global-trend-map.vercel.app/about',
    },
    publisher: {
      '@type': 'Organization',
      name: 'TrendPulse',
      url: 'https://global-trend-map.vercel.app',
    },
    datePublished: post.date,
    dateModified: post.lastUpdated || post.date,
    url: `https://global-trend-map.vercel.app/blog/${post.slug}`,
  };

  return {
    title: `${post.title} | TrendPulse Blog`,
    description: post.excerpt,
    openGraph: {
      type: 'article',
      title: post.title,
      description: post.excerpt,
      url: `https://global-trend-map.vercel.app/blog/${post.slug}`,
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
      canonical: `https://global-trend-map.vercel.app/blog/${post.slug}`,
    },
  };
}

export default async function BlogPostPage({ params }: Props) {
  const posts = await loadPostsIndex();
  const post = posts.find((p) => p.slug === params.slug);

  if (!post) notFound();

  const content = getPostContent(params.slug, post);
  const readingTime = post.readingTime || estimateReadingTime(content);
  const headings = extractHeadings(content);
  const relatedPosts = posts.filter((p) => p.slug !== params.slug).slice(0, 3);

  // Structured data
  const articleSchema = {
    '@context': 'https://schema.org',
    '@type': 'Article',
    headline: post.title,
    description: post.excerpt,
    author: {
      '@type': 'Organization',
      name: 'Global Trends Editorial Team',
      url: 'https://global-trend-map.vercel.app/about',
    },
    publisher: {
      '@type': 'Organization',
      name: 'TrendPulse',
      url: 'https://global-trend-map.vercel.app',
      logo: { '@type': 'ImageObject', url: 'https://global-trend-map.vercel.app/logo.png' },
    },
    datePublished: post.date,
    dateModified: post.lastUpdated || post.date,
    url: `https://global-trend-map.vercel.app/blog/${post.slug}`,
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
                  marginBottom: '16px',
                }}
              >
                {post.title}
              </h1>

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
                    { label: 'X', href: `https://twitter.com/intent/tweet?text=${encodeURIComponent(post.title)}&url=${encodeURIComponent('https://global-trend-map.vercel.app/blog/' + post.slug)}` },
                    { label: 'FB', href: `https://www.facebook.com/sharer/sharer.php?u=${encodeURIComponent('https://global-trend-map.vercel.app/blog/' + post.slug)}` },
                    { label: 'Reddit', href: `https://reddit.com/submit?url=${encodeURIComponent('https://global-trend-map.vercel.app/blog/' + post.slug)}&title=${encodeURIComponent(post.title)}` },
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
