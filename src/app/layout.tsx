import type { Metadata } from 'next';
import { Space_Grotesk, Space_Mono } from 'next/font/google';
import Script from 'next/script';
import './globals.css';
import CookieBanner from '@/components/CookieBanner';

const spaceGrotesk = Space_Grotesk({
  subsets: ['latin'],
  variable: '--font-space-grotesk',
  display: 'swap',
  weight: ['300', '400', '500', '600', '700'],
});

const spaceMono = Space_Mono({
  subsets: ['latin'],
  variable: '--font-space-mono',
  display: 'swap',
  weight: ['400', '700'],
});

const GA4_ID = process.env.NEXT_PUBLIC_GA4_ID || 'G-7MK156YMMH';
const SITE_URL = 'https://global-trend-map-web.vercel.app';

export const metadata: Metadata = {
  metadataBase: new URL(SITE_URL),
  title: {
    default: 'TrendPulse — Real-Time Global Trend Map',
    template: '%s | TrendPulse',
  },
  description:
    'Explore real-time trending searches and viral topics from 142 countries on a live interactive world map. Discover what the world is searching for right now.',
  keywords: [
    'global trends',
    'trending searches',
    'world map trends',
    'real-time trends',
    'Google trends map',
    'viral topics',
    'trending now',
    'global search trends',
    'country trends',
    'trend tracker',
  ],
  authors: [{ name: 'Global Trends Editorial Team', url: SITE_URL }],
  creator: 'TrendPulse',
  publisher: 'TrendPulse',
  verification: {
    google: 'u1CEFl-YCOe2kKB-43GzPxwKT87gFstteaUbv3nYpbs',
  },
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
      'max-video-preview': -1,
      'max-image-preview': 'large',
      'max-snippet': -1,
    },
  },
  openGraph: {
    type: 'website',
    locale: 'en_US',
    url: SITE_URL,
    siteName: 'TrendPulse',
    title: 'TrendPulse — Real-Time Global Trend Map',
    description:
      'Explore what 142 countries are searching for right now. Interactive world map with live trend data, temperature scores, and velocity indicators.',
    images: [
      {
        url: `${SITE_URL}/og-image.png`,
        width: 1200,
        height: 630,
        alt: 'TrendPulse — Real-Time Global Trend Map',
      },
    ],
  },
  twitter: {
    card: 'summary_large_image',
    title: 'TrendPulse — Real-Time Global Trend Map',
    description: 'Explore what 142 countries are searching for right now.',
    images: [`${SITE_URL}/og-image.png`],
    creator: '@trendpulse',
  },
  alternates: {
    canonical: SITE_URL,
    languages: {
      'en-US': SITE_URL,
      'ko-KR': `${SITE_URL}/ko`,
      'ja-JP': `${SITE_URL}/ja`,
      'x-default': SITE_URL,
    },
  },
  manifest: '/manifest.json',
  icons: {
    icon: [
      { url: '/favicon.ico' },
      { url: '/icon-16.png', sizes: '16x16', type: 'image/png' },
      { url: '/icon-32.png', sizes: '32x32', type: 'image/png' },
      { url: '/icon-192.png', sizes: '192x192', type: 'image/png' },
      { url: '/icon-512.png', sizes: '512x512', type: 'image/png' },
    ],
    apple: [{ url: '/apple-touch-icon.png', sizes: '180x180' }],
  },
  other: {
    'google-adsense-account': 'ca-pub-XXXXXXXXXX',
  },
};

const schemaWebSite = {
  '@context': 'https://schema.org',
  '@type': 'WebSite',
  name: 'TrendPulse',
  url: SITE_URL,
  description:
    'Real-time global trend visualization showing trending searches by country.',
  potentialAction: {
    '@type': 'SearchAction',
    target: {
      '@type': 'EntryPoint',
      urlTemplate: `${SITE_URL}/search?q={search_term_string}`,
    },
    'query-input': 'required name=search_term_string',
  },
  publisher: {
    '@type': 'Organization',
    name: 'TrendPulse',
    url: SITE_URL,
    logo: {
      '@type': 'ImageObject',
      url: `${SITE_URL}/logo.png`,
    },
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html
      lang="en"
      className={`${spaceGrotesk.variable} ${spaceMono.variable}`}
    >
      <head>
        {/* hreflang alternates */}
        <link rel="alternate" hrefLang="en" href={SITE_URL} />
        <link rel="alternate" hrefLang="ko" href={`${SITE_URL}/ko`} />
        <link rel="alternate" hrefLang="ja" href={`${SITE_URL}/ja`} />
        <link rel="alternate" hrefLang="x-default" href={SITE_URL} />

        {/* Schema.org structured data */}
        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{ __html: JSON.stringify(schemaWebSite) }}
        />

        {/* GA4 — direct script injection for reliable detection */}
        {GA4_ID && (
          <>
            {/* eslint-disable-next-line @next/next/no-sync-scripts */}
            <script async src={`https://www.googletagmanager.com/gtag/js?id=${GA4_ID}`} />
            <script
              dangerouslySetInnerHTML={{
                __html: `
                  window.dataLayer = window.dataLayer || [];
                  function gtag(){dataLayer.push(arguments);}
                  gtag('js', new Date());
                  gtag('config', '${GA4_ID}', { anonymize_ip: true });
                `,
              }}
            />
          </>
        )}
      </head>
      <body className="antialiased">
        {children}
        <CookieBanner />
      </body>
    </html>
  );
}
