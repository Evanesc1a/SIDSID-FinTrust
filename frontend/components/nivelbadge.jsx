import React from 'react'

const CONFIG = {
  BAJO:    { label: 'BAJO',    dot: '#10b981', bg: 'rgba(16,185,129,0.1)',  border: 'rgba(16,185,129,0.35)',  text: '#10b981' },
  MEDIO:   { label: 'MEDIO',   dot: '#f59e0b', bg: 'rgba(245,158,11,0.1)', border: 'rgba(245,158,11,0.35)', text: '#f59e0b' },
  ALTO:    { label: 'ALTO',    dot: '#f97316', bg: 'rgba(249,115,22,0.1)', border: 'rgba(249,115,22,0.35)', text: '#f97316' },
  CRITICO: { label: 'CRÍTICO', dot: '#ef4444', bg: 'rgba(239,68,68,0.12)', border: 'rgba(239,68,68,0.4)',  text: '#ef4444' },
}

export default function NivelBadge({ nivel, size = 'sm', pulse = false }) {
  const cfg = CONFIG[nivel] || CONFIG['BAJO']
  const padding = size === 'lg' ? '5px 12px' : '3px 9px'
  const fontSize = size === 'lg' ? '0.75rem' : '0.68rem'
  const dotSize = size === 'lg' ? 8 : 6

  return (
    <span style={{
      display: 'inline-flex', alignItems: 'center', gap: 6,
      background: cfg.bg, border: `1px solid ${cfg.border}`,
      borderRadius: 999, padding, color: cfg.text,
      fontFamily: 'JetBrains Mono, monospace',
      fontSize, fontWeight: 600, letterSpacing: '0.05em',
      whiteSpace: 'nowrap',
    }}>
      <span style={{
        width: dotSize, height: dotSize,
        borderRadius: '50%', background: cfg.dot, flexShrink: 0,
        ...(pulse && nivel === 'CRITICO' ? {
          boxShadow: `0 0 0 3px rgba(239,68,68,0.3)`,
          animation: 'pulse 1.5s infinite',
        } : {}),
      }} />
      {cfg.label}
    </span>
  )
}
