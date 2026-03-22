import { Metadata } from 'next';
import Link from 'next/link';

export const metadata: Metadata = {
  title: 'Editorial Policy | TrendPulse',
  description: 'TrendPulse editorial standards, content policies, and guidelines for the Trend Insights Blog.',
  alternates: { canonical: 'https://global-trend-map-web.vercel.app/editorial-policy' },
};

export default function EditorialPolicyPage() {
  return (
    <div style={{ minHeight: '100vh', background: 'var(--bg-base)' }}>
      <header style={{ background: 'var(--bg-surface)', borderBottom: '1px solid var(--border-subtle)', padding: '14px 24px' }}>
        <Link href="/" style={{ display: 'flex', alignItems: 'center', gap: '8px', textDecoration: 'none', width: 'fit-content' }}>
          <div style={{ width: '26px', height: '26px', background: 'linear-gradient(135deg, #6366f1, #a855f7)', borderRadius: '7px', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '13px' }}>🌍</div>
          <span style={{ fontWeight: 800, fontSize: '17px', color: 'var(--text-primary)' }}>Trend<span style={{ color: '#818cf8' }}>Pulse</span></span>
        </Link>
      </header>

      <main className="legal-page">
        <h1>Editorial Policy</h1>
        <p className="last-updated">Last updated: March 23, 2026</p>

        <p>TrendPulse's Trend Insights Blog is committed to high journalistic standards, transparency, and accuracy. This Editorial Policy outlines the principles, processes, and standards that govern all content published on TrendPulse.</p>

        <h2>1. Mission Statement</h2>
        <p>Our editorial mission is to provide accurate, informative, and engaging analysis of global search trend data. We help readers understand what the world is paying attention to, why certain topics surge in search interest, and what the data reveals about collective human curiosity.</p>
        <p>We are committed to:</p>
        <ul>
          <li><strong>Accuracy</strong> — Every factual claim must be verifiable and sourced</li>
          <li><strong>Transparency</strong> — We clearly disclose our data sources and methodology</li>
          <li><strong>Independence</strong> — Editorial decisions are made independently from advertising</li>
          <li><strong>Fairness</strong> — We represent diverse global perspectives fairly</li>
          <li><strong>Accountability</strong> — We correct errors promptly and transparently</li>
        </ul>

        <h2>2. Editorial Independence</h2>
        <p>Editorial content on TrendPulse is produced independently of our advertising operations. Advertisers have no influence over our editorial content, including which trends we highlight, how we analyze data, or which conclusions we draw. We do not accept payment for favorable coverage.</p>
        <p>All sponsored or promotional content, if any, is clearly labeled as "Sponsored" or "Advertisement" and is visually distinct from editorial content.</p>

        <h2>3. Data Sources & Transparency</h2>
        <p>All trend data displayed on TrendPulse is sourced from publicly available APIs and feeds, including:</p>
        <ul>
          <li>Google Trends (via public RSS feeds)</li>
          <li>YouTube Data API v3 (where available)</li>
          <li>GDELT Project (public domain global news data)</li>
          <li>Public RSS feeds from major news organizations</li>
        </ul>
        <p>When editorial articles reference specific data points, we include the data source. When YouTube data is used, articles include the attribution: "Data sourced via YouTube Data API v3. Built with YouTube Data API."</p>
        <p>When information from Wikipedia is used as background context, we include attribution: "Background information sourced from Wikipedia, available under Creative Commons Attribution-ShareAlike License (CC BY-SA)."</p>

        <h2>4. Content Standards</h2>

        <p><strong>Accuracy:</strong> We verify factual claims before publication. Where data is uncertain or disputed, we say so. We distinguish clearly between facts, analysis, and opinion.</p>

        <p><strong>Completeness:</strong> We strive to present trend data in its full context, including factors that may influence search spikes (e.g., seasonal patterns, news events, algorithmic changes).</p>

        <p><strong>Balance:</strong> When covering politically or socially sensitive topics, we represent multiple perspectives fairly. We do not editorialize in news coverage.</p>

        <p><strong>Attribution:</strong> We attribute all sources, data, quotes, and referenced work. We do not plagiarize.</p>

        <p><strong>Corrections:</strong> We correct errors promptly. Significant corrections are noted at the top of the affected article with a date and description of what was corrected.</p>

        <h2>5. Content Restrictions</h2>
        <p>Consistent with our commitment to being a safe, advertiser-friendly platform, TrendPulse will not publish editorial content that:</p>
        <ul>
          <li>Promotes, glorifies, or instructs on violence, terrorism, or extremism</li>
          <li>Contains hate speech targeting individuals or groups based on race, ethnicity, religion, gender, sexual orientation, disability, or national origin</li>
          <li>Promotes illegal activities</li>
          <li>Contains adult or sexually explicit content</li>
          <li>Spreads misinformation or deliberately false claims</li>
          <li>Promotes gambling, drugs, or other restricted categories under Google AdSense policies</li>
          <li>Infringes copyright or other intellectual property rights</li>
        </ul>

        <h2>6. Automated Content</h2>
        <p>Some trend summaries and data descriptions on TrendPulse are generated or assisted by automated systems, including AI writing assistance. All automatically generated content is:</p>
        <ul>
          <li>Reviewed by an editorial team member before publication</li>
          <li>Factually verified against source data</li>
          <li>Held to the same accuracy and quality standards as manually written content</li>
        </ul>
        <p>We do not publish unreviewed AI-generated content. If AI assistance was material to the creation of an article, we disclose this.</p>

        <h2>7. Reader Corrections & Feedback</h2>
        <p>We take reader feedback seriously. If you believe we have published inaccurate information, please contact us via our <Link href="/contact">Contact page</Link> with the following information:</p>
        <ul>
          <li>The URL of the article in question</li>
          <li>A description of the alleged inaccuracy</li>
          <li>Supporting evidence or sources</li>
        </ul>
        <p>We will investigate all credible correction requests and respond within 5 business days.</p>

        <h2>8. Conflicts of Interest</h2>
        <p>Editorial team members are required to disclose any potential conflicts of interest before writing about topics where they have a personal or financial stake. Where conflicts exist and cannot be resolved, the editorial team member will not be assigned to cover the topic.</p>

        <h2>9. SEO & Traffic Considerations</h2>
        <p>We write for human readers, not search engines. While we apply SEO best practices (descriptive titles, structured content, appropriate keywords), we never compromise accuracy, fairness, or completeness for the sake of search rankings. We do not engage in keyword stuffing, clickbait headlines, or misleading titles.</p>

        <h2>10. Comments & Community</h2>
        <p>TrendPulse does not currently host public comments. If and when we introduce community features, we will publish community guidelines at that time.</p>

        <h2>11. Contact the Editorial Team</h2>
        <p>For editorial inquiries, corrections, press requests, or partnership discussions:</p>
        <ul>
          <li>Email: hsr815815@gmail.com</li>
          <li>Contact form: <Link href="/contact">Contact page</Link></li>
        </ul>
      </main>

      <footer style={{ borderTop: '1px solid var(--border-subtle)', padding: '20px 24px', textAlign: 'center', fontSize: '12px', color: 'var(--text-muted)', background: 'var(--bg-surface)' }}>
        © {new Date().getFullYear()} TrendPulse · <Link href="/about" style={{ color: 'var(--text-muted)' }}>About</Link> · <Link href="/contact" style={{ color: 'var(--text-muted)' }}>Contact</Link>
      </footer>
    </div>
  );
}
