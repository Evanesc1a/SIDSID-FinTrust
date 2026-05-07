import React from 'react'
import { useNavigate } from 'react-router-dom'
import NivelBadge from './nivelbadge'
import { ChevronRight, Clock, User, AlertTriangle } from 'lucide-react'

function timeAgo(dateStr) {
  const diff = (Date.now() - new Date(dateStr).getTime()) / 1000
  if (diff < 60) return 'hace un momento'
  if (diff < 3600) return `hace ${Math.floor(diff / 60)}m`
  if (diff < 86400) return `hace ${Math.floor(diff / 3600)}h`
  return `hace ${Math.floor(diff / 86400)}d`
}

const ESTADO_CONFIG = {
  NUEVA:      { color: '#3b82f6', label: 'Nueva' },
  REVISADA:   { color: '#f59e0b', label: 'Revisada' },
  RESUELTA:   { color: '#10b981', label: 'Resuelta' },
  DESCARTADA: { color: '#475569', label: 'Descartada' },
}

export default function AlertaRow({ alerta, onResolver }) {
  const navigate = useNavigate()
  const estado = ESTADO_CONFIG[alerta.estado] || ESTADO_CONFIG['NUEVA']

  return (
    <div
      onClick={() => navigate(`/alertas/${alerta.id}`)}
      style={{
        display: 'grid',
        gridTemplateColumns: '130px 1fr 160px 100px 90px 36px',
        alignItems: 'center', gap: 16,
        padding: '14px 20px',
        background: '#0d1b2e',
        border: '1px solid #1e3a5f',
        borderRadius: 10, cursor: 'pointer',
        transition: 'background 0.15s, border-color 0.15s',
        marginBottom: 6,
      }}
      onMouseEnter={e => {
        e.currentTarget.style.background = '#112240'
        e.currentTarget.style.borderColor = '#2563eb44'
      }}
      onMouseLeave={e => {
        e.currentTarget.style.background = '#0d1b2e'
        e.currentTarget.style.borderColor = '#1e3a5f'
      }}
    >
      {/* Nivel */}
      <NivelBadge nivel={alerta.nivel_riesgo} pulse={alerta.estado === 'NUEVA'} />

      {/* Descripcion */}
      <div>
        <div style={{ color: '#e2e8f0', fontSize: '0.85rem', fontWeight: 500, marginBottom: 3,
          overflow:'hidden', textOverflow:'ellipsis', whiteSpace:'nowrap' }}>
          {alerta.descripcion || 'Sin descripción'}
        </div>
        <div style={{ display:'flex', alignItems:'center', gap:6, color:'#475569', fontSize:'0.72rem' }}>
          <User size={11} />
          <span style={{ fontFamily:'JetBrains Mono, monospace' }}>{alerta.usuario_nombre || alerta.usuario_id?.slice(0,8)}</span>
        </div>
      </div>

      {/* Factores */}
      <div style={{ display:'flex', gap: 4, flexWrap:'wrap' }}>
        {(alerta.factores || []).slice(0, 2).map((f, i) => (
          <span key={i} style={{
            fontSize:'0.65rem', background:'#0a1628', border:'1px solid #1e3a5f',
            borderRadius: 4, padding:'2px 6px', color:'#64748b',
            overflow:'hidden', textOverflow:'ellipsis', whiteSpace:'nowrap',
            maxWidth: 140,
          }}>
            {f}
          </span>
        ))}
      </div>

      {/* Tiempo */}
      <div style={{ display:'flex', alignItems:'center', gap:5, color:'#475569', fontSize:'0.75rem' }}>
        <Clock size={12} />
        {timeAgo(alerta.fecha_creacion)}
      </div>

      {/* Estado */}
      <span style={{
        fontSize:'0.72rem', fontWeight:600,
        color: estado.color,
        fontFamily:'JetBrains Mono, monospace',
      }}>
        {estado.label}
      </span>

      {/* Arrow */}
      <ChevronRight size={15} color="#1e3a5f" />
    </div>
  )
}
