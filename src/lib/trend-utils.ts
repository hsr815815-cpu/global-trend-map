// ============================================================
// TREND UTILITIES — Client & Server Safe
// No Node.js-only imports (no 'fs', 'path', etc.)
// ============================================================

export type TrendCategory =
  | 'sports'
  | 'tech'
  | 'music'
  | 'news'
  | 'movies'
  | 'finance'
  | 'travel'
  | 'health'
  | 'all';

export type TrendVelocity = 'rising' | 'steady' | 'falling' | 'new';

export interface TrendItem {
  rank: number;
  keyword: string;
  keywordEn?: string;
  volume: string;
  category: TrendCategory;
  temperature: number;
  velocity: TrendVelocity;
}

export interface CountryData {
  name: string;
  flag: string;
  trends: TrendItem[];
}

export interface GlobalData {
  temperature: number;
  topTrend: {
    keyword: string;
    country: string;
    volume: string;
    category: string;
  };
  totalCountries: number;
  totalTrends: number;
  risingFast: Array<{ keyword: string; keywordEn?: string; country: string; change: string }>;
  categoryBreakdown: Record<string, number>;
}

export interface TrendsData {
  lastUpdated: string;
  countries: Record<string, CountryData>;
  global: GlobalData;
}

// ============================================================
// TEMPERATURE
// ============================================================

export type TemperatureLabel = 'SUPER HOT' | 'HOT' | 'WARM' | 'RISING' | 'COOL';

export function getTemperatureLabel(temperature: number): TemperatureLabel {
  if (temperature >= 90) return 'SUPER HOT';
  if (temperature >= 75) return 'HOT';
  if (temperature >= 60) return 'WARM';
  if (temperature >= 40) return 'RISING';
  return 'COOL';
}

export function getTemperatureColor(temperature: number): string {
  if (temperature >= 90) return '#ea580c';
  if (temperature >= 75) return '#dc2626';
  if (temperature >= 60) return '#7c3aed';
  if (temperature >= 40) return '#1d4ed8';
  return '#1e3a5f';
}

export function getTemperatureGradient(temperature: number): string {
  if (temperature >= 90) return 'linear-gradient(to right, #dc2626, #ea580c, #fbbf24)';
  if (temperature >= 75) return 'linear-gradient(to right, #7c3aed, #dc2626)';
  if (temperature >= 60) return 'linear-gradient(to right, #1d4ed8, #7c3aed)';
  if (temperature >= 40) return 'linear-gradient(to right, #1e3a5f, #1d4ed8)';
  return 'linear-gradient(to right, #0f172a, #1e3a5f)';
}

export function getMapFillColor(temperature: number): string {
  if (temperature >= 90) return '#ea580c';
  if (temperature >= 80) return '#dc2626';
  if (temperature >= 70) return '#9333ea';
  if (temperature >= 60) return '#7c3aed';
  if (temperature >= 50) return '#4338ca';
  if (temperature >= 40) return '#1d4ed8';
  if (temperature >= 30) return '#1e40af';
  return '#1e3a5f';
}

// ============================================================
// CATEGORY
// ============================================================

export const CATEGORY_ICONS: Record<string, string> = {
  sports: '⚽',
  tech: '💻',
  music: '🎵',
  news: '📰',
  movies: '🎬',
  finance: '📈',
  travel: '✈️',
  health: '❤️',
  all: '🌍',
};

export const CATEGORY_LABELS: Record<string, string> = {
  sports: 'Sports',
  tech: 'Technology',
  music: 'Music',
  news: 'News',
  movies: 'Movies & TV',
  finance: 'Finance',
  travel: 'Travel',
  health: 'Health',
  all: 'All',
};

export const CATEGORY_COLORS: Record<string, string> = {
  sports: '#10b981',
  tech: '#06b6d4',
  music: '#a855f7',
  news: '#f59e0b',
  movies: '#f43f5e',
  finance: '#22c55e',
  travel: '#3b82f6',
  health: '#ef4444',
  all: '#6366f1',
};

// ============================================================
// FILTERING
// ============================================================

export function filterTrendsByCategory(trends: TrendItem[], category: TrendCategory): TrendItem[] {
  if (category === 'all') return trends;
  return trends.filter((t) => t.category === category);
}

export function getTopGlobalTrends(
  data: TrendsData,
  limit: number = 10,
  category: TrendCategory = 'all'
): Array<TrendItem & { countryCode: string; countryName: string; flag: string }> {
  // Deduplicate by keyword — keep only the highest-temperature occurrence per keyword
  const best = new Map<string, TrendItem & { countryCode: string; countryName: string; flag: string }>();

  Object.entries(data.countries).forEach(([code, country]) => {
    country.trends.forEach((trend) => {
      if (category !== 'all' && trend.category !== category) return;
      const key = (trend.keywordEn || trend.keyword).toLowerCase().trim();
      const existing = best.get(key);
      if (!existing || trend.temperature > existing.temperature) {
        best.set(key, { ...trend, countryCode: code, countryName: country.name, flag: country.flag });
      }
    });
  });

  return Array.from(best.values())
    .sort((a, b) => b.temperature - a.temperature)
    .slice(0, limit);
}

export function getCountryTemperature(data: TrendsData, countryCode: string): number {
  const country = data.countries[countryCode];
  if (!country || country.trends.length === 0) return 0;
  return Math.round(country.trends.reduce((sum, t) => sum + t.temperature, 0) / country.trends.length);
}

// ============================================================
// TIME
// ============================================================

export function getMinutesAgo(isoString: string): number {
  const updated = new Date(isoString).getTime();
  const now = Date.now();
  return Math.floor((now - updated) / 60000);
}

export function formatUpdatedAgo(isoString: string): string {
  const minutes = getMinutesAgo(isoString);
  if (minutes < 1) return 'just now';
  if (minutes < 60) return `${minutes} minute${minutes !== 1 ? 's' : ''} ago`;
  const hours = Math.floor(minutes / 60);
  if (hours < 24) return `${hours} hour${hours !== 1 ? 's' : ''} ago`;
  const days = Math.floor(hours / 24);
  return `${days} day${days !== 1 ? 's' : ''} ago`;
}

export function getNextUpdateTime(): string {
  const now = new Date();
  const next = new Date(now);
  next.setHours(next.getHours() + 1, 0, 0, 0);
  const diffMin = Math.round((next.getTime() - now.getTime()) / 60000);
  return `${diffMin} min`;
}

// ============================================================
// VELOCITY
// ============================================================

export function getVelocityIcon(velocity: TrendVelocity): string {
  switch (velocity) {
    case 'rising': return '↑';
    case 'falling': return '↓';
    case 'new': return '★';
    case 'steady': return '→';
    default: return '→';
  }
}

export function getVelocityColor(velocity: TrendVelocity): string {
  switch (velocity) {
    case 'rising': return '#10b981';
    case 'falling': return '#f43f5e';
    case 'new': return '#f59e0b';
    case 'steady': return '#94a3b8';
    default: return '#94a3b8';
  }
}

// ============================================================
// BADGES
// ============================================================

export function getTrendBadge(trend: TrendItem, countryCode?: string): 'GLOBAL' | 'FIRE' | 'NEW' | null {
  if (countryCode === undefined && trend.temperature >= 85) return 'GLOBAL';
  if (trend.temperature >= 90) return 'FIRE';
  if (trend.velocity === 'new') return 'NEW';
  return null;
}

// ============================================================
// COUNTRY
// ============================================================

export const COUNTRY_ISO_TO_NAME: Record<string, string> = {
  US: 'United States', KR: 'South Korea', JP: 'Japan', GB: 'United Kingdom',
  DE: 'Germany', IN: 'India', BR: 'Brazil', FR: 'France', AU: 'Australia',
  MX: 'Mexico', CA: 'Canada', CN: 'China', RU: 'Russia', IT: 'Italy',
  ES: 'Spain', AR: 'Argentina', ZA: 'South Africa', NG: 'Nigeria',
  EG: 'Egypt', TR: 'Turkey', SA: 'Saudi Arabia', ID: 'Indonesia',
  PH: 'Philippines', TH: 'Thailand', VN: 'Vietnam', PL: 'Poland',
  NL: 'Netherlands', SE: 'Sweden', NO: 'Norway', CH: 'Switzerland',
};
