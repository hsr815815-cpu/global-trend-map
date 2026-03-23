import { NextResponse } from 'next/server';

const REPO  = 'hsr815815-cpu/global-trend-map';
const WF_ID = 'collect-data.yml';

export async function POST(req: Request) {
  // Simple shared-secret auth — set CRON_SECRET in Vercel env vars
  const secret = req.headers.get('x-cron-secret') ?? '';
  if (!process.env.CRON_SECRET || secret !== process.env.CRON_SECRET) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
  }

  const pat = process.env.GITHUB_PAT;
  if (!pat) {
    return NextResponse.json({ error: 'GITHUB_PAT not configured' }, { status: 500 });
  }

  const res = await fetch(
    `https://api.github.com/repos/${REPO}/actions/workflows/${WF_ID}/dispatches`,
    {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${pat}`,
        Accept: 'application/vnd.github+json',
        'X-GitHub-Api-Version': '2022-11-28',
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ ref: 'main' }),
    }
  );

  if (res.status === 204) {
    return NextResponse.json({ ok: true, triggered: new Date().toISOString() });
  }

  const body = await res.text();
  return NextResponse.json({ error: 'GitHub API failed', status: res.status, body }, { status: 502 });
}
