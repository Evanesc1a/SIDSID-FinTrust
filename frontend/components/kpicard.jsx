import React from 'react'

export default function KpiCard({ titulo, valor, subtitulo, icono: Icono, color = '#3b82f6', trend, loading }) {
  return (
    <div style={{
      background: '#0d1b2e',
      border: '1px solid #1e3a5f',
      borderRadius: 12,
      padding: '20px 24px',
      display: 'flex', flexDirection: 'column', gap: 10,
      transition: 'border-color 0.2s, box-shadow 0.2s',
      position: 'relative', overflow: 'hidden',
    }}
    onMouseEnter={e => {
      e.currentTarget.style.borderColor = `${color}55`
      e.currentTarget.style.boxShadow = `0 0 24px ${color}18`
    }}
    onMouseLeave={e => {
      e.currentTarget.style.borderColor = '#1e3a5f'
      e.currentTarget.style.boxShadow = 'none'
    }}>
      {/* Accent line top */}
      <div style={{ position:'absolute', top:0, left:0, right:0, height:2, background:`linear-gradient(90deg, ${color}, transparent)` }} />

      <div style={{ display:'flex', justifyContent:'space-between', alignItems:'flex-start' }}>
        <span style={{ color: '#94a3b8', fontSize: '0.8rem', fontWeight: 500, textTransform:'uppercase', letterSpacing:'0.08em' }}>
          {titulo}
        </span>
        {Icono && (
          <span style={{
            background: `${color}18`, border: `1px solid ${color}33`,
            borderRadius: 8, padding: 7, display:'flex', color,
          }}>
            <Icono size={15} />
          </span>
        )}
      </div>

      {loading ? (
        <div style={{ height: 36, background: '#1e3a5f', borderRadius: 6, animation: 'pulse 1.5s infinite' }} />
      ) : (
        <div style={{ display:'flex', alignItems:'baseline', gap: 8 }}>
          <span style={{
            fontFamily: 'Space Grotesk, sans-serif',
            fontSize: '2rem', fontWeight: 700, color: '#e2e8f0',
            letterSpacing: '-0.02em', lineHeight: 1,
          }}>
            {valor ?? '—'}
          </span>
          {trend !== undefined && (
            <span style={{ fontSize:'0.75rem', color: trend >= 0 ? '#ef4444' : '#10b981' }}>
              {trend >= 0 ? '↑' : '↓'} {Math.abs(trend)}%
            </span>
          )}
        </div>
      )}

      {subtitulo && (
        <span style={{ color: '#475569', fontSize: '0.75rem' }}>{subtitulo}</span>
      )}
    </div>
  )
}
