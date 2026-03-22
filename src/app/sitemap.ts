import { MetadataRoute } from 'next';
import { promises as fs } from 'fs';
import path from 'path';

const SITE_URL = 'https://global-trend-map.vercel.app';

interface PostMeta {
  slug: string;
  date: string;
  lastUpdated?: string;
}

interface TrendsData {
  countries: Record<string, unknown>;
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

async function loadCountryCodes(): Promise<string[]> {
  try {
    const filePath = path.join(process.cwd(), 'public', 'data', 'trends.json');
    const raw = await fs.readFile(filePath, 'utf-8');
    const data = JSON.parse(raw) as TrendsData;
    return Object.keys(data.countries).map((code) => code.toLowerCase());
  } catch {
    return ['us', 'kr', 'jp', 'gb', 'de', 'in', 'br', 'fr', 'au', 'mx'];
  }
}

export default async function sitemap(): Promise<MetadataRoute.Sitemap> {
  const [posts, countryCodes] = await Promise.all([
    loadPostsIndex(),
    loadCountryCodes(),
  ]);

  const now = new Date().toISOString();

  // Static pages
  const staticPages: MetadataRoute.Sitemap = [
    {
      url: SITE_URL,
      lastModified: now,
      changeFrequency: 'hourly',
      priority: 1.0,
    },
    {
      url: `${SITE_URL}/blog`,
      lastModified: now,
      changeFrequency: 'hourly',
      priority: 0.9,
    },
    {
      url: `${SITE_URL}/about`,
      lastModified: '2026-03-23T00:00:00Z',
      changeFrequency: 'monthly',
      priority: 0.7,
    },
    {
      url: `${SITE_URL}/contact`,
      lastModified: '2026-03-23T00:00:00Z',
      changeFrequency: 'monthly',
      priority: 0.6,
    },
    {
      url: `${SITE_URL}/privacy-policy`,
      lastModified: '2026-03-23T00:00:00Z',
      changeFrequency: 'yearly',
      priority: 0.3,
    },
    {
      url: `${SITE_URL}/terms`,
      lastModified: '2026-03-23T00:00:00Z',
      changeFrequency: 'yearly',
      priority: 0.3,
    },
    {
      url: `${SITE_URL}/cookie-policy`,
      lastModified: '2026-03-23T00:00:00Z',
      changeFrequency: 'yearly',
      priority: 0.3,
    },
    {
      url: `${SITE_URL}/dmca`,
      lastModified: '2026-03-23T00:00:00Z',
      changeFrequency: 'yearly',
      priority: 0.2,
    },
    {
      url: `${SITE_URL}/disclaimer`,
      lastModified: '2026-03-23T00:00:00Z',
      changeFrequency: 'yearly',
      priority: 0.2,
    },
    {
      url: `${SITE_URL}/editorial-policy`,
      lastModified: '2026-03-23T00:00:00Z',
      changeFrequency: 'yearly',
      priority: 0.3,
    },
  ];

  // Blog post pages
  const blogPages: MetadataRoute.Sitemap = posts.map((post) => ({
    url: `${SITE_URL}/blog/${post.slug}`,
    lastModified: post.lastUpdated || post.date,
    changeFrequency: 'weekly' as const,
    priority: 0.8,
  }));

  // Country pages
  const countryPages: MetadataRoute.Sitemap = countryCodes.map((code) => ({
    url: `${SITE_URL}/country/${code}`,
    lastModified: now,
    changeFrequency: 'hourly' as const,
    priority: 0.85,
  }));

  return [...staticPages, ...blogPages, ...countryPages];
}
