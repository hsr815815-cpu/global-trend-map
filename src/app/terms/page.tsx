import { Metadata } from 'next';
import Link from 'next/link';

export const metadata: Metadata = {
  title: 'Terms of Service | TrendPulse',
  description: 'TrendPulse Terms of Service. Read our terms and conditions for using the TrendPulse global trend map platform.',
  alternates: { canonical: 'https://global-trend-map-web.vercel.app/terms' },
};

export default function TermsPage() {
  return (
    <div style={{ minHeight: '100vh', background: 'var(--bg-base)' }}>
      <header style={{ background: 'var(--bg-surface)', borderBottom: '1px solid var(--border-subtle)', padding: '14px 24px' }}>
        <Link href="/" style={{ display: 'flex', alignItems: 'center', gap: '8px', textDecoration: 'none', width: 'fit-content' }}>
          <div style={{ width: '26px', height: '26px', background: 'linear-gradient(135deg, #6366f1, #a855f7)', borderRadius: '7px', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '13px' }}>🌍</div>
          <span style={{ fontWeight: 800, fontSize: '17px', color: 'var(--text-primary)' }}>Trend<span style={{ color: '#818cf8' }}>Pulse</span></span>
        </Link>
      </header>

      <main className="legal-page">
        <h1>Terms of Service</h1>
        <p className="last-updated">Last updated: March 23, 2026 · Effective date: March 23, 2026</p>

        <p>Please read these Terms of Service ("Terms") carefully before using TrendPulse ("the Site," "we," "us," or "our"). By accessing or using the Site, you agree to be bound by these Terms. If you do not agree to these Terms, please do not use the Site.</p>

        <h2>1. Acceptance of Terms</h2>
        <p>By accessing and using TrendPulse at global-trend-map-web.vercel.app, you accept and agree to be bound by these Terms and our <Link href="/privacy-policy">Privacy Policy</Link>, which is incorporated herein by reference. These Terms constitute a legally binding agreement between you and TrendPulse.</p>

        <h2>2. Description of Service</h2>
        <p>TrendPulse provides a real-time visualization of global search trends, aggregated from publicly available data sources. The Service includes:</p>
        <ul>
          <li>An interactive world map displaying trending topics by country</li>
          <li>Trend temperature scores and velocity indicators</li>
          <li>A Trend Insights Blog with editorial analysis</li>
          <li>Country-specific trend detail pages</li>
          <li>An embed widget for use on third-party websites</li>
        </ul>
        <p>We reserve the right to modify, suspend, or discontinue any part of the Service at any time without notice.</p>

        <h2>3. Permitted Use</h2>
        <p>You may use the Site for lawful, personal, non-commercial purposes. Specifically, you may:</p>
        <ul>
          <li>View and browse trend data for personal research and curiosity</li>
          <li>Share links to TrendPulse pages on social media and other platforms</li>
          <li>Embed the TrendPulse widget on your website using our official embed code</li>
          <li>Reference TrendPulse data in journalism or research, with appropriate attribution</li>
        </ul>

        <h2>4. Prohibited Uses</h2>
        <p>You must not use the Site to:</p>
        <ul>
          <li>Scrape, crawl, or systematically extract data from the Site without express written permission</li>
          <li>Reproduce, republish, or redistribute Site content without attribution and without complying with our <Link href="/editorial-policy">Editorial Policy</Link></li>
          <li>Use automated tools to access the Site in ways that impose unreasonable load on our infrastructure</li>
          <li>Attempt to gain unauthorized access to any portion of the Site or its underlying systems</li>
          <li>Transmit any viruses, malware, or other harmful code</li>
          <li>Use the Site for any illegal purpose or in violation of applicable law</li>
          <li>Misrepresent TrendPulse data as your own original research without attribution</li>
          <li>Manipulate or attempt to game our trend detection systems</li>
          <li>Use the Site in any way that could damage the reputation of TrendPulse</li>
        </ul>

        <h2>5. Intellectual Property</h2>
        <p>The Site and its original content (including the TrendPulse logo, design, Temperature Score methodology, and editorial articles) are and will remain the exclusive property of TrendPulse and its licensors. Our content is protected by copyright, trademark, and other intellectual property laws.</p>

        <p>Trend data displayed on the Site is derived from publicly available sources. We do not claim proprietary rights to underlying trend data. However, our aggregation, presentation, scoring methodology, and editorial analysis are our intellectual property.</p>

        <p>The "TrendPulse" name, logo, and brand are our trademarks. You may not use them without express written permission.</p>

        <h2>6. Third-Party Data Sources</h2>
        <p>TrendPulse aggregates data from third-party sources including Google Trends, YouTube, GDELT, and public RSS feeds. We do not warrant the accuracy, completeness, or timeliness of this data. Third-party data is subject to those providers' own terms and conditions.</p>
        <ul>
          <li>Google Trends: Subject to Google's Terms of Service</li>
          <li>YouTube Data API: Built with YouTube Data API. Subject to YouTube Terms of Service</li>
          <li>GDELT: Public domain data</li>
        </ul>

        <h2>7. Advertising</h2>
        <p>The Site is supported by advertising through Google AdSense. Advertisements are clearly labeled and separate from editorial content. We do not endorse the products or services advertised on the Site. Clicking an advertisement is at your own risk.</p>

        <h2>8. Disclaimer of Warranties</h2>
        <p>THE SITE IS PROVIDED "AS IS" AND "AS AVAILABLE" WITHOUT WARRANTIES OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE, AND NON-INFRINGEMENT. WE DO NOT WARRANT THAT THE SITE WILL BE UNINTERRUPTED, ERROR-FREE, OR FREE OF VIRUSES OR OTHER HARMFUL COMPONENTS. WE DO NOT WARRANT THE ACCURACY, COMPLETENESS, OR TIMELINESS OF ANY TREND DATA DISPLAYED.</p>

        <h2>9. Limitation of Liability</h2>
        <p>TO THE FULLEST EXTENT PERMITTED BY APPLICABLE LAW, TRENDPULSE SHALL NOT BE LIABLE FOR ANY INDIRECT, INCIDENTAL, SPECIAL, CONSEQUENTIAL, OR PUNITIVE DAMAGES, INCLUDING BUT NOT LIMITED TO LOSS OF PROFITS, DATA, GOODWILL, OR OTHER INTANGIBLE LOSSES, ARISING FROM OR RELATING TO YOUR USE OF OR INABILITY TO USE THE SITE, EVEN IF WE HAVE BEEN ADVISED OF THE POSSIBILITY OF SUCH DAMAGES.</p>
        <p>OUR TOTAL LIABILITY TO YOU FOR ANY CLAIM ARISING FROM THESE TERMS OR YOUR USE OF THE SITE SHALL NOT EXCEED USD $100.</p>

        <h2>10. Indemnification</h2>
        <p>You agree to indemnify, defend, and hold harmless TrendPulse and its officers, directors, employees, and agents from any claims, liabilities, damages, losses, and expenses (including reasonable attorneys' fees) arising out of or in any way connected with your use of the Site, your violation of these Terms, or your violation of any third-party rights.</p>

        <h2>11. Embed Widget License</h2>
        <p>We grant you a limited, non-exclusive, non-transferable, revocable license to embed the TrendPulse widget on your website using our official embed code. This license is conditioned on:</p>
        <ul>
          <li>Not modifying the embed code in ways that remove our branding</li>
          <li>Not using the embed on websites that violate our <Link href="/editorial-policy">Editorial Policy</Link> (e.g., adult content, hate sites, misinformation sites)</li>
          <li>Complying with all applicable laws regarding cookie consent on your website</li>
        </ul>
        <p>We reserve the right to revoke this license at any time for any reason.</p>

        <h2>12. External Links</h2>
        <p>The Site may contain links to third-party websites. These links are provided for your convenience only. We have no control over the content of those sites and accept no responsibility for them. The inclusion of any link does not imply endorsement by TrendPulse.</p>

        <h2>13. Termination</h2>
        <p>We reserve the right to terminate or restrict your access to the Site at any time, for any reason, without notice. Upon termination, your right to use the Site immediately ceases. Provisions of these Terms that by their nature should survive termination shall survive, including intellectual property provisions, disclaimer of warranties, indemnification, and limitations of liability.</p>

        <h2>14. Governing Law & Dispute Resolution</h2>
        <p>These Terms are governed by and construed in accordance with applicable law, without regard to conflict of law principles. Any dispute arising from these Terms shall be resolved through binding arbitration, except that either party may seek injunctive relief in court for intellectual property disputes.</p>

        <h2>15. Changes to Terms</h2>
        <p>We may modify these Terms at any time. We will provide notice of material changes by updating the "Last updated" date. Your continued use of the Site after changes are posted constitutes acceptance of the updated Terms.</p>

        <h2>16. Contact</h2>
        <p>Questions about these Terms? Contact us at hsr815815@gmail.com or via our <Link href="/contact">Contact page</Link>.</p>
      </main>

      <footer style={{ borderTop: '1px solid var(--border-subtle)', padding: '20px 24px', textAlign: 'center', fontSize: '12px', color: 'var(--text-muted)', background: 'var(--bg-surface)' }}>
        © {new Date().getFullYear()} TrendPulse · <Link href="/privacy-policy" style={{ color: 'var(--text-muted)' }}>Privacy</Link> · <Link href="/disclaimer" style={{ color: 'var(--text-muted)' }}>Disclaimer</Link>
      </footer>
    </div>
  );
}
