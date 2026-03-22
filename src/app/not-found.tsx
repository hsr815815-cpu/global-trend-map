import Link from 'next/link';
export default function NotFound() {
  return (
    <div style={{ minHeight: '100vh', background: '#080810', display: 'flex', alignItems: 'center', justifyContent: 'center', flexDirection: 'column', gap: '16px', color: '#e2e8f0', fontFamily: 'sans-serif' }}>
      <div style={{ fontSize: '72px' }}>🌐</div>
      <h1 style={{ fontSize: '32px', fontWeight: 800 }}>404 — Page Not Found</h1>
      <p style={{ color: '#64748b' }}>The page you&#39;re looking for doesn&#39;t exist.</p>
      <Link href="/" style={{ background: 'linear-gradient(135deg, #6366f1, #8b5cf6)', color: 'white', padding: '10px 24px', borderRadius: '8px', textDecoration: 'none', fontWeight: 600 }}>Back to Dashboard</Link>
    </div>
  );
}
