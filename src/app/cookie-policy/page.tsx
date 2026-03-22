import { Metadata } from 'next';
import Link from 'next/link';

export const metadata: Metadata = {
  title: 'Cookie Policy | TrendPulse',
  description: 'TrendPulse Cookie Policy. Full details on the cookies we use and how to manage your cookie preferences.',
  alternates: { canonical: 'https://global-trend-map-web.vercel.app/cookie-policy' },
};

export default function CookiePolicyPage() {
  return (
    <div style={{ minHeight: '100vh', background: 'var(--bg-base)' }}>
      <header style={{ background: 'var(--bg-surface)', borderBottom: '1px solid var(--border-subtle)', padding: '14px 24px' }}>
        <Link href="/" style={{ display: 'flex', alignItems: 'center', gap: '8px', textDecoration: 'none', width: 'fit-content' }}>
          <div style={{ width: '26px', height: '26px', background: 'linear-gradient(135deg, #6366f1, #a855f7)', borderRadius: '7px', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '13px' }}>🌍</div>
          <span style={{ fontWeight: 800, fontSize: '17px', color: 'var(--text-primary)' }}>Trend<span style={{ color: '#818cf8' }}>Pulse</span></span>
        </Link>
      </header>

      <main className="legal-page">
        <h1>Cookie Policy</h1>
        <p className="last-updated">Last updated: March 23, 2026</p>

        <p>This Cookie Policy explains how TrendPulse ("we," "us," or "our") uses cookies and similar tracking technologies on our website at global-trend-map-web.vercel.app. It explains what these technologies are, why we use them, and your rights to control our use of them.</p>

        <h2>1. What Are Cookies?</h2>
        <p>Cookies are small data files placed on your computer or mobile device when you visit a website. They are widely used to make websites work, to work more efficiently, and to provide reporting information to website owners.</p>
        <p>Cookies set by the website owner (in this case, TrendPulse) are called "first-party cookies." Cookies set by parties other than the website owner are called "third-party cookies." Third-party cookies enable features or functionality to be provided on or through the website (e.g., advertising, interactive content, and analytics). The parties that set these third-party cookies can recognize your device both when it visits the website in question and also when it visits certain other websites.</p>

        <h2>2. Types of Cookies We Use</h2>

        <h2>2.1 Essential Cookies</h2>
        <p>These cookies are strictly necessary for the website to function and cannot be switched off in our systems. They are usually only set in response to actions made by you, such as setting your privacy preferences. You can set your browser to block or alert you about these cookies, but some parts of the site will not then work.</p>
        <div style={{ background: 'var(--bg-surface)', border: '1px solid var(--border-subtle)', borderRadius: '10px', padding: '16px', marginTop: '12px', overflowX: 'auto' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '13px' }}>
            <thead>
              <tr style={{ borderBottom: '1px solid var(--border-subtle)' }}>
                <th style={{ textAlign: 'left', padding: '8px', color: 'var(--text-secondary)', fontWeight: 600 }}>Cookie Name</th>
                <th style={{ textAlign: 'left', padding: '8px', color: 'var(--text-secondary)', fontWeight: 600 }}>Purpose</th>
                <th style={{ textAlign: 'left', padding: '8px', color: 'var(--text-secondary)', fontWeight: 600 }}>Duration</th>
                <th style={{ textAlign: 'left', padding: '8px', color: 'var(--text-secondary)', fontWeight: 600 }}>Type</th>
              </tr>
            </thead>
            <tbody>
              <tr style={{ borderBottom: '1px solid var(--border-subtle)' }}>
                <td style={{ padding: '10px 8px', color: 'var(--text-primary)', fontFamily: 'Space Mono, monospace', fontSize: '12px' }}>trendpulse_cookie_consent</td>
                <td style={{ padding: '10px 8px', color: 'var(--text-secondary)' }}>Stores your cookie consent preferences</td>
                <td style={{ padding: '10px 8px', color: 'var(--text-secondary)' }}>Until browser storage is cleared</td>
                <td style={{ padding: '10px 8px', color: 'var(--text-secondary)' }}>localStorage (first-party)</td>
              </tr>
            </tbody>
          </table>
        </div>

        <h2>2.2 Analytics Cookies</h2>
        <p>These cookies allow us to count visits and traffic sources so we can measure and improve the performance of our site. They help us understand which pages are most and least popular and see how visitors move around the site. All information these cookies collect is aggregated and therefore anonymous. If you do not allow these cookies, we will not know when you have visited our site and will not be able to monitor its performance.</p>
        <div style={{ background: 'var(--bg-surface)', border: '1px solid var(--border-subtle)', borderRadius: '10px', padding: '16px', marginTop: '12px', overflowX: 'auto' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '13px' }}>
            <thead>
              <tr style={{ borderBottom: '1px solid var(--border-subtle)' }}>
                <th style={{ textAlign: 'left', padding: '8px', color: 'var(--text-secondary)', fontWeight: 600 }}>Cookie Name</th>
                <th style={{ textAlign: 'left', padding: '8px', color: 'var(--text-secondary)', fontWeight: 600 }}>Purpose</th>
                <th style={{ textAlign: 'left', padding: '8px', color: 'var(--text-secondary)', fontWeight: 600 }}>Duration</th>
                <th style={{ textAlign: 'left', padding: '8px', color: 'var(--text-secondary)', fontWeight: 600 }}>Provider</th>
              </tr>
            </thead>
            <tbody>
              {[
                { name: '_ga', purpose: 'Distinguishes unique users by assigning a randomly generated number as a client identifier', duration: '2 years', provider: 'Google Analytics' },
                { name: '_ga_XXXXXXXX', purpose: 'Used to persist session state', duration: '2 years', provider: 'Google Analytics (GA4)' },
                { name: '_gid', purpose: 'Distinguishes users', duration: '24 hours', provider: 'Google Analytics' },
                { name: '_gat', purpose: 'Used to throttle request rate', duration: '1 minute', provider: 'Google Analytics' },
              ].map((cookie) => (
                <tr key={cookie.name} style={{ borderBottom: '1px solid var(--border-subtle)' }}>
                  <td style={{ padding: '10px 8px', color: 'var(--text-primary)', fontFamily: 'Space Mono, monospace', fontSize: '11px' }}>{cookie.name}</td>
                  <td style={{ padding: '10px 8px', color: 'var(--text-secondary)' }}>{cookie.purpose}</td>
                  <td style={{ padding: '10px 8px', color: 'var(--text-secondary)' }}>{cookie.duration}</td>
                  <td style={{ padding: '10px 8px', color: 'var(--text-secondary)' }}>{cookie.provider}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <h2>2.3 Advertising Cookies</h2>
        <p>These cookies may be set through our site by our advertising partner, Google AdSense. They may be used by Google to build a profile of your interests and show you relevant adverts on other sites. They do not store directly personal information, but are based on uniquely identifying your browser and internet device. If you do not allow these cookies, you will experience less targeted advertising.</p>
        <div style={{ background: 'var(--bg-surface)', border: '1px solid var(--border-subtle)', borderRadius: '10px', padding: '16px', marginTop: '12px', overflowX: 'auto' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '13px' }}>
            <thead>
              <tr style={{ borderBottom: '1px solid var(--border-subtle)' }}>
                <th style={{ textAlign: 'left', padding: '8px', color: 'var(--text-secondary)', fontWeight: 600 }}>Cookie Name</th>
                <th style={{ textAlign: 'left', padding: '8px', color: 'var(--text-secondary)', fontWeight: 600 }}>Purpose</th>
                <th style={{ textAlign: 'left', padding: '8px', color: 'var(--text-secondary)', fontWeight: 600 }}>Duration</th>
                <th style={{ textAlign: 'left', padding: '8px', color: 'var(--text-secondary)', fontWeight: 600 }}>Provider</th>
              </tr>
            </thead>
            <tbody>
              {[
                { name: 'DSID', purpose: 'Used to identify a signed-in user in non-Google sites, used for ad targeting', duration: '2 weeks', provider: 'Google' },
                { name: 'IDE', purpose: 'Used by Google DoubleClick to register and report actions after viewing or clicking an ad', duration: '1 year', provider: 'Google' },
                { name: 'NID', purpose: 'Contains a unique ID that Google uses to remember preferences and other information', duration: '6 months', provider: 'Google' },
                { name: 'CONSENT', purpose: 'Used to store user cookie consent preferences on Google domains', duration: '2 years', provider: 'Google' },
              ].map((cookie) => (
                <tr key={cookie.name} style={{ borderBottom: '1px solid var(--border-subtle)' }}>
                  <td style={{ padding: '10px 8px', color: 'var(--text-primary)', fontFamily: 'Space Mono, monospace', fontSize: '11px' }}>{cookie.name}</td>
                  <td style={{ padding: '10px 8px', color: 'var(--text-secondary)' }}>{cookie.purpose}</td>
                  <td style={{ padding: '10px 8px', color: 'var(--text-secondary)' }}>{cookie.duration}</td>
                  <td style={{ padding: '10px 8px', color: 'var(--text-secondary)' }}>{cookie.provider}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <h2>3. How to Control Cookies</h2>
        <p>You have the right to decide whether to accept or reject cookies (except essential cookies).</p>

        <p><strong>Cookie banner:</strong> When you first visit our Site, you will see a cookie consent banner. You can choose to "Accept All," "Essential Only," or "Reject All." To change your preferences, clear your browser's localStorage and refresh the page to see the banner again.</p>

        <p><strong>Browser controls:</strong> You can set or amend your web browser controls to accept or refuse cookies. If you choose to reject cookies, you may still use our Site, though your access to some functionality may be restricted. Because the means by which you can refuse cookies through your web browser controls vary from browser to browser, visit your browser's help menu for more information.</p>

        <p><strong>Google Analytics opt-out:</strong> You can opt out of Google Analytics by installing the <a href="https://tools.google.com/dlpage/gaoptout" target="_blank" rel="noopener noreferrer">Google Analytics Opt-out Browser Add-on</a>.</p>

        <p><strong>Google Ad Settings:</strong> You can opt out of interest-based advertising from Google at <a href="https://www.google.com/settings/ads" target="_blank" rel="noopener noreferrer">Google Ad Settings</a>.</p>

        <p><strong>Industry opt-out tools:</strong></p>
        <ul>
          <li><a href="https://optout.aboutads.info/" target="_blank" rel="noopener noreferrer">Digital Advertising Alliance (DAA) Opt-Out</a></li>
          <li><a href="https://optout.networkadvertising.org/" target="_blank" rel="noopener noreferrer">Network Advertising Initiative (NAI) Opt-Out</a></li>
          <li><a href="https://www.youronlinechoices.com/" target="_blank" rel="noopener noreferrer">Your Online Choices (EU)</a></li>
        </ul>

        <h2>4. Updates to This Cookie Policy</h2>
        <p>We may update this Cookie Policy from time to time to reflect changes in the cookies we use or for other operational, legal, or regulatory reasons. Please revisit this page regularly to stay informed about our use of cookies.</p>

        <h2>5. Contact Us</h2>
        <p>If you have questions about our use of cookies, contact us at hsr815815@gmail.com or via our <Link href="/contact">Contact page</Link>.</p>
      </main>

      <footer style={{ borderTop: '1px solid var(--border-subtle)', padding: '20px 24px', textAlign: 'center', fontSize: '12px', color: 'var(--text-muted)', background: 'var(--bg-surface)' }}>
        © {new Date().getFullYear()} TrendPulse · <Link href="/privacy-policy" style={{ color: 'var(--text-muted)' }}>Privacy Policy</Link> · <Link href="/terms" style={{ color: 'var(--text-muted)' }}>Terms</Link>
      </footer>
    </div>
  );
}
