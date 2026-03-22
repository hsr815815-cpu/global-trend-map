import { NextResponse } from 'next/server';

export const dynamic = 'force-dynamic';

const SITE_URL = 'https://global-trend-map.vercel.app';
const SITE_NAME = 'TrendPulse';

export async function GET(request: Request) {
  const { searchParams } = new URL(request.url);

  const type = searchParams.get('type') || 'page';
  const countryCode = searchParams.get('country')?.toUpperCase();
  const keyword = searchParams.get('keyword');
  const customUrl = searchParams.get('url');

  let shareUrl: string;
  let title: string;
  let description: string;

  switch (type) {
    case 'country':
      if (!countryCode) {
        return NextResponse.json({ error: 'Missing country parameter' }, { status: 400 });
      }
      shareUrl = `${SITE_URL}/country/${countryCode.toLowerCase()}`;
      title = `${countryCode} Trending Now | ${SITE_NAME}`;
      description = `See what's trending in ${countryCode} right now on TrendPulse — real-time global trend visualization.`;
      break;

    case 'trend':
      if (!keyword) {
        return NextResponse.json({ error: 'Missing keyword parameter' }, { status: 400 });
      }
      shareUrl = `${SITE_URL}?q=${encodeURIComponent(keyword)}`;
      title = `"${keyword}" is trending globally | ${SITE_NAME}`;
      description = `"${keyword}" is currently trending. Explore more global trends on TrendPulse.`;
      break;

    case 'page':
    default:
      shareUrl = customUrl || SITE_URL;
      title = `Real-Time Global Trend Map | ${SITE_NAME}`;
      description = `Explore what 142 countries are searching for right now. Interactive world map with live trend data, temperature scores, and velocity indicators.`;
  }

  // Generate share links for major platforms
  const encodedUrl = encodeURIComponent(shareUrl);
  const encodedTitle = encodeURIComponent(title);
  const encodedDesc = encodeURIComponent(description);

  const shareLinks = {
    twitter: `https://twitter.com/intent/tweet?text=${encodedTitle}&url=${encodedUrl}`,
    facebook: `https://www.facebook.com/sharer/sharer.php?u=${encodedUrl}&quote=${encodedDesc}`,
    reddit: `https://reddit.com/submit?url=${encodedUrl}&title=${encodedTitle}`,
    linkedin: `https://www.linkedin.com/sharing/share-offsite/?url=${encodedUrl}`,
    whatsapp: `https://wa.me/?text=${encodeURIComponent(`${title} ${shareUrl}`)}`,
    telegram: `https://t.me/share/url?url=${encodedUrl}&text=${encodedTitle}`,
    email: `mailto:?subject=${encodedTitle}&body=${encodeURIComponent(`I found this interesting: ${shareUrl}`)}`,
  };

  // Embed code
  const embedCode = `<iframe
  src="${SITE_URL}/embed"
  width="800"
  height="500"
  frameborder="0"
  style="border-radius:12px;"
  title="${SITE_NAME} Global Trend Map"
  loading="lazy"
></iframe>`;

  return NextResponse.json(
    {
      success: true,
      shareUrl,
      title,
      description,
      shareLinks,
      embedCode,
      ogImage: `${SITE_URL}/og-image.png`,
      siteName: SITE_NAME,
    },
    {
      headers: {
        'Cache-Control': 'public, max-age=300, stale-while-revalidate=60',
        'Access-Control-Allow-Origin': '*',
      },
    }
  );
}

export async function OPTIONS(_request: Request) {
  return new NextResponse(null, {
    status: 200,
    headers: {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'GET, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type',
    },
  });
}
