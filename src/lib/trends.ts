// ============================================================
// TRENDS — Server-side data loading (uses Node.js fs)
// Re-exports all pure utilities from trend-utils
// ============================================================

// Re-export everything from the client-safe utils
export * from './trend-utils';

import { promises as fs } from 'fs';
import path from 'path';
import type { TrendsData } from './trend-utils';

// ============================================================
// DATA LOADING (SERVER ONLY)
// ============================================================

let cachedData: TrendsData | null = null;
let cacheTime: number = 0;
const CACHE_TTL = 5 * 60 * 1000; // 5 minutes

export async function loadTrendsData(): Promise<TrendsData> {
  const now = Date.now();

  // Return cached data if fresh
  if (cachedData && now - cacheTime < CACHE_TTL) {
    return cachedData;
  }

  try {
    const filePath = path.join(process.cwd(), 'public', 'data', 'trends.json');
    const raw = await fs.readFile(filePath, 'utf-8');
    const data: TrendsData = JSON.parse(raw);
    cachedData = data;
    cacheTime = now;
    return data;
  } catch (error) {
    console.error('Failed to load trends data:', error);
    return getFallbackData();
  }
}

export function getFallbackData(): TrendsData {
  return {
    lastUpdated: new Date().toISOString(),
    countries: {
      US: {
        name: 'United States',
        flag: '🇺🇸',
        trends: [
          {
            rank: 1,
            keyword: 'Trending Now',
            volume: '1M+',
            category: 'news',
            temperature: 72,
            velocity: 'rising',
          },
        ],
      },
    },
    global: {
      temperature: 72,
      topTrend: {
        keyword: 'Trending Now',
        country: 'US',
        volume: '1M+',
        category: 'news',
      },
      totalCountries: 36,
      totalTrends: 720,
      risingFast: [],
      categoryBreakdown: {
        sports: 28,
        tech: 22,
        music: 18,
        news: 16,
        movies: 10,
        finance: 6,
      },
    },
  };
}
