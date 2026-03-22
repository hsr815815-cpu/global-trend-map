'use client';
import { useEffect } from 'react';

export default function Error({ error, reset }: { error: Error & { digest?: string }; reset: () => void }) {
  useEffect(() => { console.error(error); }, [error]);
  return (
    <div style={{ minHeight: '100vh', background: '#080810', display: 'flex', alignItems: 'center', justifyContent: 'center', flexDirection: 'column', gap: '16px', color: '#e2e8f0', fontFamily: 'sans-serif' }}>
      <div style={{ fontSize: '48px' }}>⚠️</div>
      <h2 style={{ fontSize: '24px', fontWeight: 700 }}>Something went wrong</h2>
      <p style={{ color: '#64748b', maxWidth: '400px', textAlign: 'center' }}>The dashboard encountered an error loading trend data. This is usually temporary.</p>
      <button onClick={reset} style={{ background: 'linear-gradient(135deg, #6366f1, #8b5cf6)', color: 'white', border: 'none', padding: '10px 24px', borderRadius: '8px', cursor: 'pointer', fontSize: '14px', fontWeight: 600 }}>Try again</button>
    </div>
  );
}
