import { Metadata } from 'next';
import Link from 'next/link';

export const metadata: Metadata = {
  title: 'Disclaimer | TrendPulse',
  description: 'TrendPulse disclaimer regarding the accuracy and use of trend data displayed on the platform.',
  alternates: { canonical: 'https://global-trend-map-web.vercel.app/disclaimer' },
};

export default function DisclaimerPage() {
  return (
    <div style={{ minHeight: '100vh', background: 'var(--bg-base)' }}>
      <header style={{ background: 'var(--bg-surface)', borderBottom: '1px solid var(--border-subtle)', padding: '14px 24px' }}>
        <Link href="/" style={{ display: 'flex', alignItems: 'center', gap: '8px', textDecoration: 'none', width: 'fit-content' }}>
          <div style={{ width: '26px', height: '26px', background: 'linear-gradient(135deg, #6366f1, #a855f7)', borderRadius: '7px', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '13px' }}>🌍</div>
          <span style={{ fontWeight: 800, fontSize: '17px', color: 'var(--text-primary)' }}>Trend<span style={{ color: '#818cf8' }}>Pulse</span></span>
        </Link>
      </header>

      <main className="legal-page">
        <h1>Disclaimer</h1>
        <p className="last-updated">Last updated: March 23, 2026</p>

        <h2>1. General Disclaimer</h2>
        <p>The information provided by TrendPulse ("we," "us," or "our") on global-trend-map-web.vercel.app (the "Site") is for general informational and educational purposes only. All information on the Site is provided in good faith; however, we make no representation or warranty of any kind, express or implied, regarding the accuracy, adequacy, validity, reliability, availability, or completeness of any information on the Site.</p>

        <p><strong>UNDER NO CIRCUMSTANCE SHALL TRENDPULSE HAVE ANY LIABILITY TO YOU FOR ANY LOSS OR DAMAGE OF ANY KIND INCURRED AS A RESULT OF THE USE OF THE SITE OR RELIANCE ON ANY INFORMATION PROVIDED ON THE SITE.</strong></p>

        <h2>2. Data Accuracy Disclaimer</h2>
        <p>Trend data displayed on TrendPulse is aggregated from third-party sources including publicly available APIs and RSS feeds. We cannot guarantee:</p>
        <ul>
          <li>The real-time accuracy of trend data at any given moment</li>
          <li>That trend data represents absolute search volumes (data represents relative trends, not exact counts)</li>
          <li>That all trending topics in a given country are captured and displayed</li>
          <li>The geographic accuracy of trend attribution to specific countries</li>
          <li>That the Temperature Score (°T) accurately reflects the true intensity of any trend</li>
        </ul>
        <p>Trend data should be used as an indicative overview of public interest, not as precise scientific data. Do not make business, financial, or investment decisions based solely on information displayed on TrendPulse.</p>

        <h2>3. Financial Information Disclaimer</h2>
        <p>Any financial trends or market-related topics displayed on TrendPulse reflect trending search interest in financial topics — they do not constitute financial advice, investment recommendations, or market predictions. We are not financial advisors. Always consult a qualified financial professional before making investment decisions.</p>

        <h2>4. Health Information Disclaimer</h2>
        <p>Any health-related trends displayed on TrendPulse reflect public search interest only. They do not constitute medical advice, diagnosis, or treatment recommendations. Always seek the advice of a qualified healthcare provider with any questions you may have regarding a medical condition.</p>

        <h2>5. Editorial Content Disclaimer</h2>
        <p>Blog posts and editorial articles on TrendPulse represent the analysis and opinions of the Global Trends Editorial Team based on available data. They are not statements of fact about the topics discussed. We strive for accuracy and will correct errors when identified.</p>
        <p>Our editorial analysis reflects the state of trend data at the time of writing. As trends evolve rapidly, information in older articles may no longer reflect current conditions.</p>

        <h2>6. Third-Party Content Disclaimer</h2>
        <p>The Site may display references to or links to third-party websites, products, services, or content. We do not endorse any such third-party content. We are not responsible for:</p>
        <ul>
          <li>The accuracy, content, or opinions of third-party websites or services</li>
          <li>The availability of third-party websites or services</li>
          <li>The privacy practices of third-party websites or services</li>
          <li>Any products or services offered by third parties</li>
        </ul>

        <h2>7. Advertising Disclaimer</h2>
        <p>TrendPulse is supported by advertising through Google AdSense. Advertisements displayed on the Site are provided by Google and are based on your browsing behavior and site context. We do not personally select or endorse the specific products, services, or companies advertised. Advertised content is clearly labeled as advertising and is separate from editorial content.</p>

        <h2>8. No Professional Advice</h2>
        <p>The information on TrendPulse does not constitute professional advice of any kind including legal, financial, medical, psychological, or other professional advice. Always seek the advice of a qualified professional with questions you may have in those areas.</p>

        <h2>9. Errors and Omissions</h2>
        <p>While we take reasonable measures to ensure the accuracy of information on the Site, we cannot guarantee it is always up-to-date or complete. The Site may contain errors, omissions, or outdated information. If you spot an error, please contact us via our <Link href="/contact">Contact page</Link> so we can investigate and correct it promptly.</p>

        <h2>10. Technology Disclaimer</h2>
        <p>The Site and the data it displays are processed by automated systems including machine learning, algorithmic content filtering, and automated data aggregation. Automated systems are not perfect and may produce incorrect results. Human review of all content is not possible at scale. Our content moderation is handled programmatically and errors may occur.</p>

        <h2>11. Contact</h2>
        <p>Questions about this disclaimer? Contact us at hsr815815@gmail.com or via our <Link href="/contact">Contact page</Link>.</p>
      </main>

      <footer style={{ borderTop: '1px solid var(--border-subtle)', padding: '20px 24px', textAlign: 'center', fontSize: '12px', color: 'var(--text-muted)', background: 'var(--bg-surface)' }}>
        © {new Date().getFullYear()} TrendPulse · <Link href="/terms" style={{ color: 'var(--text-muted)' }}>Terms</Link> · <Link href="/privacy-policy" style={{ color: 'var(--text-muted)' }}>Privacy</Link>
      </footer>
    </div>
  );
}
