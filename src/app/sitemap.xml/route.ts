import { promises as fs } from 'fs';
import path from 'path';
import { NextResponse } from 'next/server';

export const dynamic = 'force-dynamic';

const SITE_URL = 'https://global-trend-map-web.vercel.app';

async function getCountryCodes(): Promise<string[]> {
  try {
    const raw = await fs.readFile(
      path.join(process.cwd(), 'public', 'data', 'trends.json'),
      'utf-8'
    );
    const data = JSON.parse(raw);
    return Object.keys(data.countries).map((c) => c.toLowerCase());
  } catch {
    return ['us', 'kr', 'jp', 'gb', 'de', 'in', 'br', 'fr', 'au', 'mx'];
  }
}

async function getPostSlugs(): Promise<{ slug: string; date: string }[]> {
  try {
    const raw = await fs.readFile(
      path.join(process.cwd(), 'public', 'data', 'posts-index.json'),
      'utf-8'
    );
    return JSON.parse(raw);
  } catch {
    return [];
  }
}

function url(loc: string, lastmod: string, changefreq: string, priority: string) {
  return `  <url>\n    <loc>${loc}</loc>\n    <lastmod>${lastmod}</lastmod>\n    <changefreq>${changefreq}</changefreq>\n    <priority>${priority}</priority>\n  </url>`;
}

export async function GET() {
  const now = new Date().toISOString();
  const [countryCodes, posts] = await Promise.all([getCountryCodes(), getPostSlugs()]);

  const staticUrls = [
    url(SITE_URL, now, 'hourly', '1.0'),
    url(`${SITE_URL}/blog`, now, 'hourly', '0.9'),
    url(`${SITE_URL}/about`, '2026-03-23T00:00:00Z', 'monthly', '0.7'),
    url(`${SITE_URL}/contact`, '2026-03-23T00:00:00Z', 'monthly', '0.6'),
    url(`${SITE_URL}/privacy-policy`, '2026-03-23T00:00:00Z', 'yearly', '0.3'),
    url(`${SITE_URL}/terms`, '2026-03-23T00:00:00Z', 'yearly', '0.3'),
    url(`${SITE_URL}/cookie-policy`, '2026-03-23T00:00:00Z', 'yearly', '0.3'),
    url(`${SITE_URL}/dmca`, '2026-03-23T00:00:00Z', 'yearly', '0.2'),
    url(`${SITE_URL}/disclaimer`, '2026-03-23T00:00:00Z', 'yearly', '0.2'),
    url(`${SITE_URL}/editorial-policy`, '2026-03-23T00:00:00Z', 'yearly', '0.3'),
  ];

  const postUrls = posts.map((p) =>
    url(`${SITE_URL}/blog/${p.slug}`, p.date, 'weekly', '0.8')
  );

  const countryUrls = countryCodes.map((c) =>
    url(`${SITE_URL}/country/${c}`, now, 'hourly', '0.85')
  );

  const xml = [
    '<?xml version="1.0" encoding="UTF-8"?>',
    '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
    ...staticUrls,
    ...postUrls,
    ...countryUrls,
    '</urlset>',
  ].join('\n');

  return new NextResponse(xml, {
    status: 200,
    headers: {
      'Content-Type': 'application/xml; charset=utf-8',
      'Cache-Control': 'no-cache, no-store, must-revalidate',
      'X-Robots-Tag': 'noindex',
    },
  });
}
