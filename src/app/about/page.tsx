import { Metadata } from 'next';
import Link from 'next/link';

export const metadata: Metadata = {
  title: 'About TrendPulse — Real-Time Global Trend Map',
  description:
    'Learn about TrendPulse, the real-time global trend visualization platform that tracks trending searches across 142 countries. Meet the editorial team and discover our methodology.',
  alternates: { canonical: 'https://global-trend-map.vercel.app/about' },
};

export default function AboutPage() {
  return (
    <div style={{ minHeight: '100vh', background: 'var(--bg-base)' }}>
      <header style={{ background: 'var(--bg-surface)', borderBottom: '1px solid var(--border-subtle)', padding: '14px 24px' }}>
        <Link href="/" style={{ display: 'flex', alignItems: 'center', gap: '8px', textDecoration: 'none', width: 'fit-content' }}>
          <div style={{ width: '26px', height: '26px', background: 'linear-gradient(135deg, #6366f1, #a855f7)', borderRadius: '7px', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '13px' }}>🌍</div>
          <span style={{ fontWeight: 800, fontSize: '17px', color: 'var(--text-primary)' }}>Trend<span style={{ color: '#818cf8' }}>Pulse</span></span>
        </Link>
      </header>

      <main className="legal-page">
        <h1>About TrendPulse</h1>
        <p className="last-updated">The internet's window into global curiosity</p>

        <div style={{ background: 'linear-gradient(135deg, rgba(99,102,241,0.12), rgba(168,85,247,0.12))', border: '1px solid rgba(99,102,241,0.3)', borderRadius: '16px', padding: '24px', marginBottom: '32px' }}>
          <p style={{ fontSize: '18px', fontWeight: 500, color: 'var(--text-primary)', lineHeight: 1.7, margin: 0 }}>
            TrendPulse is a real-time global trend visualization platform that transforms raw search data into a living, breathing picture of what humanity cares about — right now.
          </p>
        </div>

        <h2>What We Do</h2>
        <p>Every hour, TrendPulse collects and processes trending search data from across 142 countries, applying a proprietary temperature scoring system (°T) to quantify how hot a topic is relative to normal search volume. The result is an interactive world map where you can see — at a glance — which countries are experiencing search surges, what topics are driving them, and how quickly they are rising or falling.</p>

        <p>We track trends across six primary categories:</p>
        <ul>
          <li><strong>Sports</strong> — From local league matches to global championships</li>
          <li><strong>Technology</strong> — Product launches, AI developments, and digital culture</li>
          <li><strong>Music</strong> — Artist announcements, album releases, and viral moments</li>
          <li><strong>News</strong> — Current events, political developments, and human interest stories</li>
          <li><strong>Movies & TV</strong> — Streaming releases, box office events, and entertainment</li>
          <li><strong>Finance</strong> — Market movements, economic indicators, and investment topics</li>
        </ul>

        <h2>Our Mission</h2>
        <p>We believe that understanding what people around the world are searching for — at the moment they are searching — reveals something profound about shared human experience. A natural disaster, a musical breakthrough, a sporting triumph, a technological leap: these events ripple across the globe as search waves that TrendPulse captures and visualizes.</p>

        <p>Our mission is to make this data accessible, beautiful, and meaningful to anyone — from curious individuals wondering what is trending in Japan today, to researchers studying the spread of information, to marketers seeking to understand global conversations.</p>

        <h2>The Editorial Team</h2>
        <p>The Global Trends Editorial Team at TrendPulse is a distributed group of data journalists, trend analysts, and technology writers. Together, we write the Trend Insights Blog, which provides in-depth analysis of major search trend events, explains the forces driving viral moments, and contextualizes data within broader cultural and economic stories.</p>

        <p>Our editorial standards prioritize accuracy, transparency, and fairness. We clearly distinguish between observed data (what people are searching for) and our analysis and interpretation of that data. We correct errors promptly and transparently.</p>

        <h2>Data Sources & Methodology</h2>
        <p>TrendPulse aggregates trend data from several public sources:</p>
        <ul>
          <li><strong>Google Trends RSS Feeds</strong> — Publicly available feeds showing trending search topics by region</li>
          <li><strong>YouTube Trending API</strong> — Top trending videos by country (via YouTube Data API v3, where quota permits)</li>
          <li><strong>GDELT Project</strong> — Global news and event data for news category trends</li>
          <li><strong>Public RSS Feeds</strong> — From major news organizations, app stores, and music platforms</li>
        </ul>

        <p>All data undergoes content moderation to comply with Google AdSense policies. Topics involving adult content, violence, hate speech, gambling, drugs, terrorism, or other restricted categories are automatically filtered and will not appear on TrendPulse.</p>

        <h2>The Temperature Score (°T)</h2>
        <p>Our proprietary Temperature Score (°T) measures the relative intensity of a trending topic on a scale of 0 to 100. The score is calculated based on the rate of search volume increase compared to baseline levels for that topic and region. A score of 90°T or above is classified as "SUPER HOT" — indicating a dramatic and sudden surge in search interest. The scale:</p>
        <ul>
          <li><strong>90–100°T — SUPER HOT</strong>: Explosive, viral-level search surge</li>
          <li><strong>75–89°T — HOT</strong>: Significant trending event with broad regional interest</li>
          <li><strong>60–74°T — WARM</strong>: Noteworthy trend with above-average engagement</li>
          <li><strong>40–59°T — RISING</strong>: Growing trend with upward momentum</li>
          <li><strong>0–39°T — COOL</strong>: Low or declining trend activity</li>
        </ul>

        <h2>Privacy & Advertising</h2>
        <p>TrendPulse is a free service supported by advertising. We use Google AdSense to display contextual advertisements. All advertising is clearly labeled and separated from editorial content. We respect user privacy and comply with GDPR, CCPA, and other applicable data protection regulations.</p>

        <p>We do not sell personal data. We do not display advertising to users who have not consented to analytics and advertising cookies. See our <Link href="/privacy-policy">Privacy Policy</Link> and <Link href="/cookie-policy">Cookie Policy</Link> for full details.</p>

        <h2>Updates & Data Freshness</h2>
        <p>Trend data is refreshed hourly by an automated pipeline (GitHub Actions). The "Updated X minutes ago" indicator in the header shows exactly when the current data was last collected. We aim for data that is never more than 90 minutes old under normal operating conditions.</p>

        <h2>Contact Us</h2>
        <p>We welcome feedback, corrections, press inquiries, and partnership discussions. Please use our <Link href="/contact">Contact page</Link> to reach the team. For DMCA takedown requests, see our <Link href="/dmca">DMCA Policy</Link>.</p>

        <h2>Legal</h2>
        <p>TrendPulse is an independent publication. All trend data is sourced from publicly available APIs and RSS feeds. We do not claim ownership of trend data. Content on the Trend Insights Blog is original writing by the Global Trends Editorial Team.</p>

        <p>For our complete legal terms, see: <Link href="/terms">Terms of Service</Link> · <Link href="/privacy-policy">Privacy Policy</Link> · <Link href="/disclaimer">Disclaimer</Link> · <Link href="/editorial-policy">Editorial Policy</Link></p>
      </main>

      <footer style={{ borderTop: '1px solid var(--border-subtle)', padding: '20px 24px', textAlign: 'center', fontSize: '12px', color: 'var(--text-muted)', background: 'var(--bg-surface)' }}>
        © {new Date().getFullYear()} TrendPulse · <Link href="/" style={{ color: 'var(--text-muted)' }}>Home</Link> · <Link href="/contact" style={{ color: 'var(--text-muted)' }}>Contact</Link>
      </footer>
    </div>
  );
}
