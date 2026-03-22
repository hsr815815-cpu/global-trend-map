import { Metadata } from 'next';
import Link from 'next/link';

export const metadata: Metadata = {
  title: 'DMCA Policy | TrendPulse',
  description: 'TrendPulse DMCA copyright takedown policy. How to submit a copyright infringement notice.',
  alternates: { canonical: 'https://global-trend-map.vercel.app/dmca' },
};

export default function DMCAPage() {
  return (
    <div style={{ minHeight: '100vh', background: 'var(--bg-base)' }}>
      <header style={{ background: 'var(--bg-surface)', borderBottom: '1px solid var(--border-subtle)', padding: '14px 24px' }}>
        <Link href="/" style={{ display: 'flex', alignItems: 'center', gap: '8px', textDecoration: 'none', width: 'fit-content' }}>
          <div style={{ width: '26px', height: '26px', background: 'linear-gradient(135deg, #6366f1, #a855f7)', borderRadius: '7px', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '13px' }}>🌍</div>
          <span style={{ fontWeight: 800, fontSize: '17px', color: 'var(--text-primary)' }}>Trend<span style={{ color: '#818cf8' }}>Pulse</span></span>
        </Link>
      </header>

      <main className="legal-page">
        <h1>DMCA Policy</h1>
        <p className="last-updated">Last updated: March 23, 2026</p>

        <p>TrendPulse respects intellectual property rights and complies with the Digital Millennium Copyright Act (DMCA), 17 U.S.C. § 512. If you believe that material on our Site infringes your copyright, please submit a notification to our designated DMCA agent using the process described below.</p>

        <h2>1. Reporting Copyright Infringement</h2>
        <p>To file a DMCA takedown notice, you must provide a written communication that includes <strong>all</strong> of the following elements:</p>
        <ul>
          <li><strong>Identification of the copyrighted work</strong> — A description of the work you claim has been infringed, or a list of works if multiple works are involved</li>
          <li><strong>Identification of the infringing material</strong> — A description of the material you claim is infringing, with enough detail for us to locate it on the Site (e.g., a URL)</li>
          <li><strong>Your contact information</strong> — Your full legal name, mailing address, telephone number, and email address</li>
          <li><strong>Statement of good faith</strong> — A statement that you have a good faith belief that the use of the material in the manner complained of is not authorized by the copyright owner, its agent, or the law</li>
          <li><strong>Statement of accuracy</strong> — A statement that the information in the notification is accurate, and under penalty of perjury, that you are authorized to act on behalf of the copyright owner</li>
          <li><strong>Physical or electronic signature</strong> — The physical or electronic signature of the copyright owner or authorized agent</li>
        </ul>

        <h2>2. Where to Send Notices</h2>
        <p>Send your DMCA notice to our designated agent:</p>
        <div style={{ background: 'var(--bg-surface)', border: '1px solid var(--border-subtle)', borderRadius: '10px', padding: '16px', marginTop: '10px', marginBottom: '10px' }}>
          <p style={{ margin: 0, color: 'var(--text-secondary)', lineHeight: 2 }}>
            <strong style={{ color: 'var(--text-primary)' }}>DMCA Agent: TrendPulse Editorial Team</strong><br />
            Email: hsr815815@gmail.com<br />
            Subject line: <span style={{ fontFamily: 'Space Mono, monospace', fontSize: '13px' }}>DMCA Takedown Notice — [Your Name]</span>
          </p>
        </div>
        <p>For fastest processing, please send notices via email. We aim to respond within 5 business days.</p>

        <h2>3. Counter-Notification</h2>
        <p>If you believe that your material was removed or access was disabled as a result of mistake or misidentification, you may submit a counter-notification. A valid counter-notification must include:</p>
        <ul>
          <li>Your physical or electronic signature</li>
          <li>Identification of the material removed and its location before removal</li>
          <li>A statement under penalty of perjury that you have a good faith belief the material was removed by mistake or misidentification</li>
          <li>Your name, address, and telephone number</li>
          <li>A statement consenting to jurisdiction of your federal judicial district (or the judicial district where TrendPulse is located if you are outside the US)</li>
        </ul>

        <h2>4. Repeat Infringer Policy</h2>
        <p>TrendPulse has a policy of terminating, in appropriate circumstances and at our discretion, users or accounts that are repeat infringers. We will terminate access of any user or account holder who repeatedly infringes the copyrights of others.</p>

        <h2>5. False Claims</h2>
        <p>Please be aware that under 17 U.S.C. § 512(f), any person who knowingly materially misrepresents that material or activity is infringing may be subject to liability for damages, including costs and attorneys' fees incurred in connection with the removal of allegedly infringing material. If you are not sure whether material on our Site infringes your copyright, please consult a legal advisor before filing a notice.</p>

        <h2>6. Voluntary Licensing</h2>
        <p>Before submitting a DMCA notice, please consider contacting us through our <Link href="/contact">Contact page</Link> to discuss potential licensing arrangements. We are open to working with content creators and rights holders to ensure appropriate attribution and use of materials.</p>

        <h2>7. Our Content Policy</h2>
        <p>TrendPulse's editorial content is original and created by our team. Trend data displayed on the Site is sourced from publicly available APIs and feeds. We believe our use of such data falls within fair use provisions, as we provide transformative analysis and visualization rather than reproduction.</p>
        <p>If you have a question about a specific piece of content, please reach out before filing a formal DMCA notice — most issues can be resolved quickly and informally.</p>
      </main>

      <footer style={{ borderTop: '1px solid var(--border-subtle)', padding: '20px 24px', textAlign: 'center', fontSize: '12px', color: 'var(--text-muted)', background: 'var(--bg-surface)' }}>
        © {new Date().getFullYear()} TrendPulse · <Link href="/terms" style={{ color: 'var(--text-muted)' }}>Terms</Link> · <Link href="/contact" style={{ color: 'var(--text-muted)' }}>Contact</Link>
      </footer>
    </div>
  );
}
