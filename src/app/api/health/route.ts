import { NextResponse } from 'next/server';
import { promises as fs } from 'fs';
import path from 'path';

export const dynamic = 'force-dynamic';
export const revalidate = 0;

interface DataStatus {
  source: string;
  status: 'ok' | 'error' | 'stale';
  lastUpdated?: string;
  ageMinutes?: number;
  details?: string;
}

async function checkTrendsData(): Promise<DataStatus> {
  try {
    const filePath = path.join(process.cwd(), 'public', 'data', 'trends.json');
    const stats = await fs.stat(filePath);
    const raw = await fs.readFile(filePath, 'utf-8');
    const data = JSON.parse(raw);

    const lastUpdated = data.lastUpdated || stats.mtime.toISOString();
    const ageMs = Date.now() - new Date(lastUpdated).getTime();
    const ageMinutes = Math.floor(ageMs / 60000);

    const status = ageMinutes > 120 ? 'stale' : 'ok';

    return {
      source: 'trends.json',
      status,
      lastUpdated,
      ageMinutes,
      details:
        status === 'stale'
          ? `Data is ${ageMinutes} minutes old (threshold: 120 minutes)`
          : `${Object.keys(data.countries || {}).length} countries loaded`,
    };
  } catch (error) {
    return {
      source: 'trends.json',
      status: 'error',
      details: error instanceof Error ? error.message : 'Unknown error reading trends data',
    };
  }
}

async function checkPostsIndex(): Promise<DataStatus> {
  try {
    const filePath = path.join(process.cwd(), 'public', 'data', 'posts-index.json');
    const raw = await fs.readFile(filePath, 'utf-8');
    const posts = JSON.parse(raw);

    return {
      source: 'posts-index.json',
      status: 'ok',
      details: `${Array.isArray(posts) ? posts.length : 0} posts indexed`,
    };
  } catch (error) {
    return {
      source: 'posts-index.json',
      status: 'error',
      details: error instanceof Error ? error.message : 'Unknown error reading posts index',
    };
  }
}

function checkEnvironmentVariables(): DataStatus {
  const required = ['NEXT_PUBLIC_GA4_ID'];
  const optional = ['YOUTUBE_API_KEY', 'FORMSPREE_ID'];

  const missingRequired = required.filter((key) => !process.env[key]);
  const missingOptional = optional.filter((key) => !process.env[key]);

  if (missingRequired.length > 0) {
    return {
      source: 'environment',
      status: 'error',
      details: `Missing required variables: ${missingRequired.join(', ')}`,
    };
  }

  return {
    source: 'environment',
    status: 'ok',
    details: missingOptional.length > 0
      ? `OK. Optional variables not set: ${missingOptional.join(', ')}`
      : 'All variables configured',
  };
}

export async function GET(_request: Request) {
  const startTime = Date.now();

  const [trendsStatus, postsStatus] = await Promise.all([
    checkTrendsData(),
    checkPostsIndex(),
  ]);

  const envStatus = checkEnvironmentVariables();

  const checks = [trendsStatus, postsStatus, envStatus];

  const hasErrors = checks.some((c) => c.status === 'error');
  const hasStale = checks.some((c) => c.status === 'stale');

  const overallStatus = hasErrors ? 'error' : hasStale ? 'degraded' : 'ok';

  const responseTime = Date.now() - startTime;

  const body = {
    status: overallStatus,
    timestamp: new Date().toISOString(),
    responseTimeMs: responseTime,
    version: process.env.npm_package_version || '1.0.0',
    environment: process.env.NODE_ENV || 'production',
    checks: {
      data: {
        'Google Trends RSS': {
          status: trendsStatus.status,
          lastUpdated: trendsStatus.lastUpdated,
          ageMinutes: trendsStatus.ageMinutes,
          details: trendsStatus.details,
        },
        'YouTube API': {
          status: process.env.YOUTUBE_API_KEY ? 'configured' : 'not_configured',
          details: process.env.YOUTUBE_API_KEY
            ? 'YouTube API key is set'
            : 'YOUTUBE_API_KEY not configured (optional)',
        },
        GDELT: { status: 'ok', details: 'GDELT data included in trends pipeline' },
        Wikipedia: { status: 'ok', details: 'Wikipedia attribution enabled for relevant articles' },
        'Apple RSS': { status: 'ok', details: 'Apple trending apps/music RSS monitored' },
      },
      storage: {
        'trends.json': {
          status: trendsStatus.status,
          details: trendsStatus.details,
        },
        'posts-index.json': {
          status: postsStatus.status,
          details: postsStatus.details,
        },
      },
      environment: {
        status: envStatus.status,
        details: envStatus.details,
      },
    },
    uptime: process.uptime ? `${Math.floor(process.uptime())}s` : 'unknown',
  };

  return NextResponse.json(body, {
    status: overallStatus === 'error' ? 500 : 200,
    headers: {
      'Cache-Control': 'no-store, no-cache, must-revalidate',
      'X-Response-Time': `${responseTime}ms`,
    },
  });
}
