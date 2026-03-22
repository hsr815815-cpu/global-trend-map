import { Metadata } from 'next';
import Link from 'next/link';

export const metadata: Metadata = {
  title: 'Privacy Policy | TrendPulse',
  description: 'TrendPulse Privacy Policy. Learn how we collect, use, and protect your data in compliance with GDPR and CCPA.',
  robots: { index: true, follow: true },
  alternates: { canonical: 'https://global-trend-map-web.vercel.app/privacy-policy' },
};

export default function PrivacyPolicyPage() {
  return (
    <div style={{ minHeight: '100vh', background: 'var(--bg-base)' }}>
      <header style={{ background: 'var(--bg-surface)', borderBottom: '1px solid var(--border-subtle)', padding: '14px 24px' }}>
        <Link href="/" style={{ display: 'flex', alignItems: 'center', gap: '8px', textDecoration: 'none', width: 'fit-content' }}>
          <div style={{ width: '26px', height: '26px', background: 'linear-gradient(135deg, #6366f1, #a855f7)', borderRadius: '7px', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '13px' }}>🌍</div>
          <span style={{ fontWeight: 800, fontSize: '17px', color: 'var(--text-primary)' }}>Trend<span style={{ color: '#818cf8' }}>Pulse</span></span>
        </Link>
      </header>

      <main className="legal-page">
        <h1>Privacy Policy</h1>
        <p className="last-updated">Last updated: March 23, 2026 · Effective date: March 23, 2026</p>

        <p>TrendPulse ("we," "our," or "us") is committed to protecting your privacy. This Privacy Policy explains how we collect, use, disclose, and safeguard your information when you visit our website at global-trend-map-web.vercel.app (the "Site"). Please read this policy carefully. If you disagree with its terms, please discontinue use of the Site.</p>

        <h2>1. Information We Collect</h2>
        <p>We collect information in the following ways:</p>

        <p><strong>Information collected automatically:</strong> When you visit the Site, we automatically collect certain information about your device and browsing activity, including:</p>
        <ul>
          <li>IP address (anonymized before storage)</li>
          <li>Browser type and version</li>
          <li>Operating system</li>
          <li>Referring URLs</li>
          <li>Pages visited and time spent on those pages</li>
          <li>Date and time of visits</li>
          <li>Geographic region (country/city level, derived from anonymized IP)</li>
          <li>Search queries and interactions within the Site</li>
        </ul>

        <p><strong>Information you provide voluntarily:</strong> If you contact us via our contact form, we collect:</p>
        <ul>
          <li>Your name</li>
          <li>Your email address</li>
          <li>The content of your message</li>
        </ul>

        <p><strong>Cookies and tracking technologies:</strong> We use cookies, web beacons, and similar technologies. See our <Link href="/cookie-policy">Cookie Policy</Link> for full details.</p>

        <h2>2. How We Use Your Information</h2>
        <p>We use the information we collect to:</p>
        <ul>
          <li>Operate, maintain, and improve the Site</li>
          <li>Analyze usage patterns and understand how visitors interact with the Site</li>
          <li>Detect and prevent fraud, abuse, and security issues</li>
          <li>Respond to your inquiries and support requests</li>
          <li>Send administrative communications (if you have opted in)</li>
          <li>Comply with legal obligations</li>
          <li>Display relevant advertising through Google AdSense</li>
        </ul>

        <h2>3. Legal Basis for Processing (GDPR)</h2>
        <p>If you are located in the European Economic Area (EEA) or United Kingdom, our legal basis for collecting and using your personal information is:</p>
        <ul>
          <li><strong>Consent</strong> — For analytics cookies and advertising cookies, we rely on your explicit consent given through our cookie banner</li>
          <li><strong>Legitimate interests</strong> — For essential site security, fraud prevention, and improving our services</li>
          <li><strong>Legal obligation</strong> — When required by applicable law</li>
        </ul>

        <h2>4. Google Analytics 4 (GA4)</h2>
        <p>We use Google Analytics 4 to analyze Site usage. GA4 uses cookies to collect anonymized data about how visitors use our Site. We have configured GA4 with:</p>
        <ul>
          <li>IP anonymization enabled (last octet of IP addresses is masked)</li>
          <li>Data retention set to 14 months</li>
          <li>No sharing of data with Google for advertising purposes</li>
          <li>Consent Mode enabled — GA4 only activates after you accept analytics cookies</li>
        </ul>
        <p>You can opt out of Google Analytics by installing the <a href="https://tools.google.com/dlpage/gaoptout" target="_blank" rel="noopener noreferrer">Google Analytics Opt-out Browser Add-on</a>.</p>

        <h2>5. Google AdSense</h2>
        <p>We display advertisements through Google AdSense. Google uses cookies to serve ads based on your prior visits to our Site and other sites on the Internet. You may opt out of personalized advertising by visiting <a href="https://www.google.com/settings/ads" target="_blank" rel="noopener noreferrer">Google Ad Settings</a> or <a href="https://optout.aboutads.info/" target="_blank" rel="noopener noreferrer">AboutAds.info</a>.</p>

        <h2>6. Data Sharing and Disclosure</h2>
        <p>We do not sell, trade, or rent your personal information to third parties. We may share information in the following limited circumstances:</p>
        <ul>
          <li><strong>Service providers</strong> — Google Analytics, Google AdSense, and Formspree (contact form processing), each bound by their own privacy policies and data processing agreements</li>
          <li><strong>Legal requirements</strong> — If required by law, court order, or governmental authority</li>
          <li><strong>Business transfers</strong> — In connection with a merger, acquisition, or sale of assets (you will be notified of any such change)</li>
          <li><strong>Protection of rights</strong> — To protect the rights, property, or safety of TrendPulse, our users, or others</li>
        </ul>

        <h2>7. Data Retention</h2>
        <p>We retain personal data for as long as necessary to fulfill the purposes described in this policy, or as required by applicable law:</p>
        <ul>
          <li>GA4 analytics data: 14 months, then automatically deleted</li>
          <li>Contact form submissions: 12 months from the date of submission, then deleted</li>
          <li>Cookie consent preferences: Stored in your browser's localStorage; cleared when you clear browser data</li>
        </ul>

        <h2>8. Your Rights (GDPR)</h2>
        <p>If you are in the EEA or UK, you have the following rights regarding your personal data:</p>
        <ul>
          <li><strong>Right of access</strong> — Request a copy of the personal data we hold about you</li>
          <li><strong>Right to rectification</strong> — Request correction of inaccurate personal data</li>
          <li><strong>Right to erasure</strong> — Request deletion of your personal data ("right to be forgotten")</li>
          <li><strong>Right to restriction</strong> — Request that we limit how we use your data</li>
          <li><strong>Right to data portability</strong> — Receive your data in a structured, machine-readable format</li>
          <li><strong>Right to object</strong> — Object to processing based on legitimate interests</li>
          <li><strong>Right to withdraw consent</strong> — Withdraw consent at any time (via our cookie banner)</li>
        </ul>
        <p>To exercise these rights, contact us at hsr815815@gmail.com. We will respond within 30 days.</p>

        <h2>9. Your Rights (CCPA — California Residents)</h2>
        <p>If you are a California resident, you have the right to:</p>
        <ul>
          <li>Know what personal information we collect, use, disclose, and sell</li>
          <li>Request deletion of your personal information</li>
          <li>Opt out of the sale of personal information (Note: We do not sell personal information)</li>
          <li>Non-discrimination for exercising your privacy rights</li>
        </ul>

        <h2>10. Cookies</h2>
        <p>We use essential, analytics, and advertising cookies. You can manage your cookie preferences at any time using the cookie banner (accessible by clearing your localStorage and refreshing the page). See our <Link href="/cookie-policy">Cookie Policy</Link> for a complete list of cookies used.</p>

        <h2>11. Children's Privacy</h2>
        <p>The Site is not directed to children under the age of 13 (or 16 in the EEA). We do not knowingly collect personal information from children. If you believe we have inadvertently collected information from a child, please contact us immediately and we will delete it.</p>

        <h2>12. International Data Transfers</h2>
        <p>We are based globally. Your information may be transferred to and processed in countries other than your country of residence, including the United States. These countries may have different data protection laws. When we transfer data from the EEA to third countries, we rely on appropriate safeguards such as Standard Contractual Clauses (SCCs).</p>

        <h2>13. Security</h2>
        <p>We implement appropriate technical and organizational measures to protect your personal information against unauthorized access, alteration, disclosure, or destruction. The Site is served over HTTPS. However, no method of transmission over the Internet is 100% secure.</p>

        <h2>14. Links to Third-Party Sites</h2>
        <p>The Site may contain links to third-party websites. We are not responsible for the privacy practices of those sites. We encourage you to review the privacy policies of any third-party sites you visit.</p>

        <h2>15. Changes to This Policy</h2>
        <p>We may update this Privacy Policy from time to time. We will notify you of any material changes by updating the "Last updated" date at the top of this page. Your continued use of the Site after changes are posted constitutes acceptance of the updated policy.</p>

        <h2>16. Contact Us</h2>
        <p>If you have questions or concerns about this Privacy Policy or our data practices, please contact us:</p>
        <ul>
          <li>Email: hsr815815@gmail.com</li>
          <li>Contact form: <Link href="/contact">Contact page</Link></li>
        </ul>
        <p>If you are in the EEA and have an unresolved privacy concern, you have the right to file a complaint with your local data protection authority (DPA).</p>
      </main>

      <footer style={{ borderTop: '1px solid var(--border-subtle)', padding: '20px 24px', textAlign: 'center', fontSize: '12px', color: 'var(--text-muted)', background: 'var(--bg-surface)' }}>
        © {new Date().getFullYear()} TrendPulse · <Link href="/terms" style={{ color: 'var(--text-muted)' }}>Terms</Link> · <Link href="/cookie-policy" style={{ color: 'var(--text-muted)' }}>Cookie Policy</Link>
      </footer>
    </div>
  );
}
