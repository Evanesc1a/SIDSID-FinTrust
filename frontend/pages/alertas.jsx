import React, { useState } from 'react'
import { useAlertas } from '../hooks/usealertas'
import AlertaRow from '../components/alertarow'
import NivelBadge from '../components/nivelbadge'
import { Filter, RefreshCw, Bell, CheckCircle, AlertTriangle, Search } from 'lucide-react'

const NIVELES = ['', 'BAJO', 'MEDIO', 'ALTO', 'CRITICO']
const ESTADOS = ['', 'NUEVA', 'REVISADA', 'RESUELTA', 'DESCARTADA']

export default function Alertas() {
  const [nivel, setNivel] = useState('')
  const [estado, setEstado] = useState('NUEVA')
  const [search, setSearch] = useState('')

  const { alertas, resumen, loading, recargar } = useAlertas({
    ...(nivel ? { nivel } : {}),
    ...(estado ? { estado } : {}),
    limite: 100,
  })

  const filtradas = alertas.filter(a =>
    !search || a.descripcion?.toLowerCase().includes(search.toLowerCase()) ||
    a.usuario_nombre?.toLowerCase().includes(search.toLowerCase())
  )

  const selectStyle = {
    background:'#060b14', border:'1px solid #1e3a5f', borderRadius:8,
    padding:'7px 12px', color:'#94a3b8', fontSize:'0.8rem', cursor:'pointer',
    outline:'none', fontFamily:'DM Sans, sans-serif',
  }

  return (
    <div style={{ padding:'28px 32px', maxWidth:1400, margin:'0 auto' }}>
      {/* Header */}
      <div style={{ display:'flex', justifyContent:'space-between', alignItems:'flex-start', marginBottom:28 }}>
        <div>
          <h1 style={{ fontFamily:'Space Grotesk, sans-serif', fontSize:'1.5rem', fontWeight:700, color:'#e2e8f0', margin:0 }}>
            Gestión de Alertas
          </h1>
          <p style={{ color:'#475569', fontSize:'0.8rem', margin:'4px 0 0', fontFamily:'JetBrains Mono, monospace' }}>
            Centro de revisión y resolución de incidentes
          </p>
        </div>
        <button onClick={recargar} style={{
          background:'#0a1628', border:'1px solid #1e3a5f', borderRadius:8,
          padding:'8px 16px', cursor:'pointer', color:'#64748b',
          display:'flex', alignItems:'center', gap:6, fontSize:'0.8rem',
        }}>
          <RefreshCw size={13} style={{ animation: loading ? 'spin 0.6s linear infinite' : 'none' }} />
          Actualizar
        </button>
      </div>

      {/* Summary badges */}
      {resumen && (
        <div style={{ display:'grid', gridTemplateColumns:'repeat(4, 1fr)', gap:12, marginBottom:24 }}>
          {Object.entries(resumen.por_nivel).map(([nivel, count]) => (
            <div key={nivel}
              onClick={() => setNivel(prev => prev === nivel ? '' : nivel)}
              style={{
                background:'#0d1b2e', border:`1px solid ${nivel === nivel ? '#1e3a5f' : '#1e3a5f'}`,
                borderRadius:10, padding:'14px 18px', cursor:'pointer',
                display:'flex', justifyContent:'space-between', alignItems:'center',
                transition:'all 0.15s',
              }}
              onMouseEnter={e => e.currentTarget.style.borderColor = '#2563eb44'}
              onMouseLeave={e => e.currentTarget.style.borderColor = '#1e3a5f'}
            >
              <NivelBadge nivel={nivel} />
              <span style={{
                fontFamily:'Space Grotesk, sans-serif', fontSize:'1.5rem', fontWeight:700,
                color: count > 0 ? '#e2e8f0' : '#334155',
              }}>
                {count}
              </span>
            </div>
          ))}
        </div>
      )}

      {/* Filters */}
      <div style={{
        background:'#0d1b2e', border:'1px solid #1e3a5f', borderRadius:10,
        padding:'14px 20px', marginBottom:16,
        display:'flex', gap:12, alignItems:'center', flexWrap:'wrap',
      }}>
        <Filter size={14} color="#475569" />

        {/* Search */}
        <div style={{ position:'relative', flex:1, minWidth:200 }}>
          <Search size={13} style={{ position:'absolute', left:10, top:'50%', transform:'translateY(-50%)', color:'#475569' }} />
          <input value={search} onChange={e => setSearch(e.target.value)}
            placeholder="Buscar alertas..."
            style={{ ...selectStyle, paddingLeft:32, width:'100%', boxSizing:'border-box' }}
          />
        </div>

        <select value={nivel} onChange={e => setNivel(e.target.value)} style={selectStyle}>
          <option value="">Todos los niveles</option>
          {NIVELES.slice(1).map(n => <option key={n} value={n}>{n}</option>)}
        </select>

        <select value={estado} onChange={e => setEstado(e.target.value)} style={selectStyle}>
          <option value="">Todos los estados</option>
          {ESTADOS.slice(1).map(s => <option key={s} value={s}>{s}</option>)}
        </select>

        <span style={{ color:'#334155', fontSize:'0.75rem', fontFamily:'JetBrains Mono, monospace', marginLeft:'auto' }}>
          {filtradas.length} resultado{filtradas.length !== 1 ? 's' : ''}
        </span>
      </div>

      {/* Table header */}
      {filtradas.length > 0 && (
        <div style={{
          display:'grid', gridTemplateColumns:'130px 1fr 160px 100px 90px 36px',
          gap:16, padding:'8px 20px', marginBottom:4,
        }}>
          {['Nivel', 'Descripción', 'Factores', 'Tiempo', 'Estado', ''].map((h, i) => (
            <span key={i} style={{ color:'#334155', fontSize:'0.68rem', fontFamily:'JetBrains Mono, monospace', textTransform:'uppercase', letterSpacing:'0.08em' }}>{h}</span>
          ))}
        </div>
      )}

      {/* List */}
      {loading ? (
        <div style={{ display:'flex', flexDirection:'column', gap:6 }}>
          {[...Array(6)].map((_, i) => (
            <div key={i} style={{ height:60, background:'#0d1b2e', borderRadius:10, border:'1px solid #1e3a5f', animation:'pulse 1.5s infinite' }} />
          ))}
        </div>
      ) : filtradas.length === 0 ? (
        <div style={{ textAlign:'center', padding:'60px 32px', background:'#0d1b2e', borderRadius:12, border:'1px solid #1e3a5f' }}>
          <CheckCircle size={36} color="#10b981" style={{ marginBottom:12 }} />
          <p style={{ color:'#e2e8f0', fontSize:'0.95rem', fontWeight:600, margin:'0 0 6px' }}>No hay alertas</p>
          <p style={{ color:'#475569', fontSize:'0.8rem', margin:0 }}>No se encontraron alertas con los filtros aplicados.</p>
        </div>
      ) : (
        <div>
          {filtradas.map(a => <AlertaRow key={a.id} alerta={a} />)}
        </div>
      )}

      <style>{`
        @keyframes spin { to { transform: rotate(360deg); } }
        @keyframes pulse { 0%,100% { opacity:1; } 50% { opacity:0.6; } }
        select option { background: #0a1628; }
      `}</style>
    </div>
  )
}
