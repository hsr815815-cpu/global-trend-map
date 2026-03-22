'use client';

import { useState } from 'react';
import Link from 'next/link';

export default function ContactPage() {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    subject: '',
    message: '',
    inquiry: 'general',
  });
  const [status, setStatus] = useState<'idle' | 'sending' | 'sent' | 'error'>('idle');

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    setFormData((prev) => ({ ...prev, [e.target.name]: e.target.value }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setStatus('sending');

    try {
      const res = await fetch('https://formspree.io/f/xqeyvaay', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
        body: JSON.stringify(formData),
      });

      if (res.ok) {
        setStatus('sent');
        setFormData({ name: '', email: '', subject: '', message: '', inquiry: 'general' });
      } else {
        setStatus('error');
      }
    } catch {
      setStatus('error');
    }
  };

  return (
    <div style={{ minHeight: '100vh', background: 'var(--bg-base)' }}>
      <header style={{ background: 'var(--bg-surface)', borderBottom: '1px solid var(--border-subtle)', padding: '14px 24px' }}>
        <Link href="/" style={{ display: 'flex', alignItems: 'center', gap: '8px', textDecoration: 'none', width: 'fit-content' }}>
          <div style={{ width: '26px', height: '26px', background: 'linear-gradient(135deg, #6366f1, #a855f7)', borderRadius: '7px', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '13px' }}>🌍</div>
          <span style={{ fontWeight: 800, fontSize: '17px', color: 'var(--text-primary)' }}>Trend<span style={{ color: '#818cf8' }}>Pulse</span></span>
        </Link>
      </header>

      <main style={{ maxWidth: '720px', margin: '0 auto', padding: '48px 24px' }}>
        <div style={{ marginBottom: '36px' }}>
          <h1 style={{ fontSize: '2rem', fontWeight: 800, color: 'var(--text-primary)', marginBottom: '10px' }}>Contact Us</h1>
          <p style={{ fontSize: '15px', color: 'var(--text-secondary)', lineHeight: 1.7 }}>
            We'd love to hear from you. Whether you have a question about our data, spotted an error, want to collaborate, or just want to say hello — reach out using the form below.
          </p>
        </div>

        {/* Contact info cards */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '12px', marginBottom: '32px' }}>
          {[
            { icon: '📧', title: 'Email', info: 'hsr815815@gmail.com', sub: 'General inquiries' },
            { icon: '⏱️', title: 'Response Time', info: '24–48 hours', sub: 'Business days' },
            { icon: '🌍', title: 'Team', info: 'Global', sub: 'Distributed team' },
          ].map((item) => (
            <div key={item.title} style={{ background: 'var(--bg-card)', border: '1px solid var(--border-subtle)', borderRadius: '12px', padding: '16px', textAlign: 'center' }}>
              <div style={{ fontSize: '24px', marginBottom: '8px' }}>{item.icon}</div>
              <div style={{ fontSize: '11px', fontFamily: 'Space Mono, monospace', color: 'var(--text-muted)', letterSpacing: '0.08em', textTransform: 'uppercase', marginBottom: '4px' }}>{item.title}</div>
              <div style={{ fontSize: '13px', fontWeight: 700, color: 'var(--text-primary)', marginBottom: '2px' }}>{item.info}</div>
              <div style={{ fontSize: '11px', color: 'var(--text-muted)' }}>{item.sub}</div>
            </div>
          ))}
        </div>

        {/* Form */}
        <div style={{ background: 'var(--bg-card)', border: '1px solid var(--border-subtle)', borderRadius: '16px', padding: '28px' }}>
          {status === 'sent' ? (
            <div style={{ textAlign: 'center', padding: '32px 0' }}>
              <div style={{ fontSize: '48px', marginBottom: '16px' }}>✅</div>
              <h2 style={{ fontSize: '20px', fontWeight: 700, color: 'var(--text-primary)', marginBottom: '10px' }}>Message Sent!</h2>
              <p style={{ color: 'var(--text-secondary)', fontSize: '14px', lineHeight: 1.7, marginBottom: '20px' }}>
                Thank you for reaching out. We typically respond within 24–48 business hours.
              </p>
              <button
                onClick={() => setStatus('idle')}
                style={{ padding: '10px 24px', background: 'var(--accent-indigo)', border: 'none', borderRadius: '8px', color: 'white', fontSize: '14px', fontWeight: 600, cursor: 'pointer' }}
              >
                Send Another Message
              </button>
            </div>
          ) : (
            <form onSubmit={handleSubmit}>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px', marginBottom: '16px' }}>
                <div>
                  <label className="form-label" htmlFor="name">Your Name *</label>
                  <input id="name" name="name" type="text" required value={formData.name} onChange={handleChange} className="form-input" placeholder="Jane Smith" />
                </div>
                <div>
                  <label className="form-label" htmlFor="email">Email Address *</label>
                  <input id="email" name="email" type="email" required value={formData.email} onChange={handleChange} className="form-input" placeholder="jane@example.com" />
                </div>
              </div>

              <div style={{ marginBottom: '16px' }}>
                <label className="form-label" htmlFor="inquiry">Inquiry Type</label>
                <select id="inquiry" name="inquiry" value={formData.inquiry} onChange={handleChange} className="form-input">
                  <option value="general">General Question</option>
                  <option value="data">Data Accuracy / Correction</option>
                  <option value="press">Press / Media Inquiry</option>
                  <option value="partnership">Partnership / Collaboration</option>
                  <option value="dmca">DMCA / Copyright</option>
                  <option value="feedback">Feedback / Feature Request</option>
                  <option value="other">Other</option>
                </select>
              </div>

              <div style={{ marginBottom: '16px' }}>
                <label className="form-label" htmlFor="subject">Subject *</label>
                <input id="subject" name="subject" type="text" required value={formData.subject} onChange={handleChange} className="form-input" placeholder="Brief subject of your message" />
              </div>

              <div style={{ marginBottom: '24px' }}>
                <label className="form-label" htmlFor="message">Message *</label>
                <textarea
                  id="message"
                  name="message"
                  required
                  value={formData.message}
                  onChange={handleChange}
                  className="form-input"
                  placeholder="Please provide as much detail as possible so we can help you effectively."
                  rows={6}
                  style={{ resize: 'vertical', minHeight: '120px' }}
                />
              </div>

              {status === 'error' && (
                <div style={{ background: 'rgba(244,63,94,0.12)', border: '1px solid rgba(244,63,94,0.3)', borderRadius: '8px', padding: '12px 16px', marginBottom: '16px', fontSize: '13px', color: '#fb7185' }}>
                  Something went wrong. Please try again or email us directly at hsr815815@gmail.com
                </div>
              )}

              <button
                type="submit"
                disabled={status === 'sending'}
                style={{
                  width: '100%',
                  padding: '14px',
                  background: status === 'sending' ? 'var(--bg-elevated)' : 'var(--accent-indigo)',
                  border: 'none',
                  borderRadius: '10px',
                  color: 'white',
                  fontSize: '15px',
                  fontWeight: 700,
                  cursor: status === 'sending' ? 'not-allowed' : 'pointer',
                  transition: 'all 0.15s ease',
                }}
              >
                {status === 'sending' ? 'Sending…' : 'Send Message'}
              </button>

              <p style={{ marginTop: '12px', fontSize: '11px', color: 'var(--text-muted)', textAlign: 'center' }}>
                By submitting this form, you agree to our <Link href="/privacy-policy" style={{ color: 'var(--text-muted)' }}>Privacy Policy</Link>. We never share your contact details with third parties.
              </p>
            </form>
          )}
        </div>

        <div style={{ marginTop: '32px', background: 'var(--bg-card)', border: '1px solid var(--border-subtle)', borderRadius: '12px', padding: '20px' }}>
          <h2 style={{ fontSize: '15px', fontWeight: 700, color: 'var(--text-primary)', marginBottom: '12px' }}>Other Ways to Reach Us</h2>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
            {[
              { label: 'Data corrections & factual errors', link: null, note: 'Use the form above with inquiry type "Data Accuracy / Correction"' },
              { label: 'DMCA & copyright takedown requests', link: '/dmca', note: 'See our DMCA Policy for the required request format' },
              { label: 'Press & media inquiries', link: null, note: 'Use the form above with inquiry type "Press / Media Inquiry"' },
              { label: 'Privacy-related requests (GDPR/CCPA)', link: '/privacy-policy', note: 'See our Privacy Policy for data subject rights' },
            ].map((item) => (
              <div key={item.label} style={{ display: 'flex', gap: '10px', alignItems: 'flex-start' }}>
                <span style={{ color: '#818cf8', marginTop: '2px' }}>→</span>
                <div>
                  <span style={{ fontSize: '13px', fontWeight: 600, color: 'var(--text-primary)' }}>{item.label}</span>
                  {item.link && (
                    <Link href={item.link} style={{ color: '#818cf8', marginLeft: '6px', fontSize: '13px' }}>({item.link.replace('/', '')})</Link>
                  )}
                  <div style={{ fontSize: '12px', color: 'var(--text-muted)', marginTop: '2px' }}>{item.note}</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </main>

      <footer style={{ borderTop: '1px solid var(--border-subtle)', padding: '20px 24px', textAlign: 'center', fontSize: '12px', color: 'var(--text-muted)', background: 'var(--bg-surface)' }}>
        © {new Date().getFullYear()} TrendPulse · <Link href="/" style={{ color: 'var(--text-muted)' }}>Home</Link> · <Link href="/about" style={{ color: 'var(--text-muted)' }}>About</Link>
      </footer>
    </div>
  );
}
