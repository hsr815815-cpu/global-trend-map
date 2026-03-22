import { MetadataRoute } from 'next';

const SITE_URL = 'https://global-trend-map.vercel.app';

export default function robots(): MetadataRoute.Robots {
  return {
    rules: [
      {
        userAgent: '*',
        allow: '/',
        disallow: [
          '/api/',
          '/_next/',
          '/report/',
        ],
      },
      {
        // Allow Google's AdsBot to crawl for AdSense eligibility
        userAgent: 'AdsBot-Google',
        allow: '/',
        disallow: ['/api/', '/_next/', '/report/'],
      },
    ],
    sitemap: `${SITE_URL}/sitemap.xml`,
    host: SITE_URL,
  };
}
