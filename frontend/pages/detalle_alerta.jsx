import React, { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { alertasService } from '../services/alertasservice'
import NivelBadge from '../components/nivelbadge'
import {
  ArrowLeft, Shield, Clock, User, Monitor,
  MapPin, Cpu, AlertTriangle, CheckCircle,
  XCircle, ChevronRight
} from 'lucide-react'

function timeStr(dateStr) {
  if (!dateStr) return '—'
  return new Date(dateStr).toLocaleString('es-CO', {
    year:'numeric', month:'short', day:'numeric',
    hour:'2-digit', minute:'2-digit',
  })
}

export default function DetalleAlerta() {
  const { id } = useParams()
  const navigate = useNavigate()
  const [alerta, setAlerta] = useState(null)
  const [loading, setLoading] = useState(true)
  const [accion, setAccion] = useState('')
  const [notas, setNotas] = useState('')
  const [resolving, setResolving] = useState(false)
  const [done, setDone] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    alertasService.obtener(id)
      .then(r => setAlerta(r.data))
      .catch(() => setError('No se pudo cargar la alerta'))
      .finally(() => setLoading(false))
  }, [id])

  const handleResolver = async () => {
    if (!accion) { setError('Selecciona una acción'); return }
    setResolving(true)
    setError('')
    try {
      const updated = await alertasService.resolver(id, accion, notas)
      setAlerta(updated.data)
      setDone(true)
    } catch (e) {
      setError(e.response?.data?.error || 'Error al procesar la acción')
    } finally {
      setResolving(false)
    }
  }

  const sectionStyle = {
    background:'#0d1b2e', border:'1px solid #1e3a5f',
    borderRadius:12, padding:'20px 24px', marginBottom:16,
  }

  const labelStyle = { color:'#475569', fontSize:'0.7rem', fontFamily:'JetBrains Mono, monospace', textTransform:'uppercase', letterSpacing:'0.08em', marginBottom:4, display:'block' }
  const valueStyle = { color:'#e2e8f0', fontSize:'0.875rem', fontFamily:'DM Sans, sans-serif' }

  if (loading) return (
    <div style={{ padding:32, display:'flex', justifyContent:'center' }}>
      <div style={{ width:36, height:36, border:'2px solid #1e3a5f', borderTopColor:'#3b82f6', borderRadius:'50%', animation:'spin 0.8s linear infinite' }} />
      <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
    </div>
  )

  if (!alerta) return (
    <div style={{ padding:32, color:'#ef4444', textAlign:'center' }}>
      {error || 'Alerta no encontrada'}
    </div>
  )

  return (
    <div style={{ padding:'28px 32px', maxWidth:900, margin:'0 auto' }}>
      {/* Back */}
      <button onClick={() => navigate(-1)} style={{
        background:'none', border:'none', cursor:'pointer', color:'#475569',
        display:'flex', alignItems:'center', gap:6, marginBottom:20,
        fontSize:'0.8rem', padding:0,
      }}
      onMouseEnter={e => e.currentTarget.style.color = '#94a3b8'}
      onMouseLeave={e => e.currentTarget.style.color = '#475569'}>
        <ArrowLeft size={14} /> Volver a alertas
      </button>

      {/* Header */}
      <div style={{ ...sectionStyle, borderColor: alerta.nivel_riesgo === 'CRITICO' ? 'rgba(239,68,68,0.4)' : '#1e3a5f' }}>
        <div style={{ display:'flex', justifyContent:'space-between', alignItems:'flex-start', marginBottom:16 }}>
          <div style={{ display:'flex', alignItems:'center', gap:12 }}>
            <NivelBadge nivel={alerta.nivel_riesgo} size="lg" pulse />
            <div>
              <span style={{ color:'#94a3b8', fontSize:'0.7rem', fontFamily:'JetBrains Mono, monospace', letterSpacing:'0.08em' }}>
                ID ALERTA
              </span>
              <div style={{ color:'#3b82f6', fontSize:'0.75rem', fontFamily:'JetBrains Mono, monospace' }}>
                {alerta.id}
              </div>
            </div>
          </div>
          <div style={{
            padding:'4px 12px', borderRadius:99,
            background: alerta.estado === 'NUEVA' ? 'rgba(59,130,246,0.1)' : alerta.estado === 'RESUELTA' ? 'rgba(16,185,129,0.1)' : 'rgba(71,85,105,0.2)',
            border: `1px solid ${alerta.estado === 'NUEVA' ? 'rgba(59,130,246,0.35)' : alerta.estado === 'RESUELTA' ? 'rgba(16,185,129,0.35)' : '#334155'}`,
            color: alerta.estado === 'NUEVA' ? '#3b82f6' : alerta.estado === 'RESUELTA' ? '#10b981' : '#64748b',
            fontSize:'0.72rem', fontFamily:'JetBrains Mono, monospace', fontWeight:600,
          }}>
            {alerta.estado}
          </div>
        </div>

        <p style={{ color:'#e2e8f0', fontSize:'0.95rem', margin:'0 0 12px', lineHeight:1.6 }}>
          {alerta.descripcion}
        </p>

        <div style={{ display:'flex', gap:20 }}>
          <div style={{ display:'flex', alignItems:'center', gap:6, color:'#475569', fontSize:'0.75rem' }}>
            <Clock size={12} />
            {timeStr(alerta.fecha_creacion)}
          </div>
          <div style={{ display:'flex', alignItems:'center', gap:6, color:'#475569', fontSize:'0.75rem' }}>
            <User size={12} />
            {alerta.usuario_nombre || alerta.usuario_id?.slice(0,12)}
          </div>
        </div>
      </div>

      {/* Score */}
      <div style={{ ...sectionStyle }}>
        <div style={{ display:'flex', justifyContent:'space-between', alignItems:'center', marginBottom:16 }}>
          <h3 style={{ fontFamily:'Space Grotesk, sans-serif', color:'#e2e8f0', fontSize:'0.9rem', fontWeight:600, margin:0 }}>
            Puntaje de Anomalía
          </h3>
          <Cpu size={15} color="#0891b2" />
        </div>
        <div style={{ display:'flex', alignItems:'center', gap:16 }}>
          <div style={{
            fontFamily:'Space Grotesk, sans-serif', fontSize:'2.5rem', fontWeight:700,
            color: alerta.nivel_riesgo === 'CRITICO' ? '#ef4444' : alerta.nivel_riesgo === 'ALTO' ? '#f97316' : alerta.nivel_riesgo === 'MEDIO' ? '#f59e0b' : '#10b981',
          }}>
            {typeof alerta.puntaje === 'number' ? alerta.puntaje.toFixed(4) : '—'}
          </div>
          <div>
            <div style={{ color:'#475569', fontSize:'0.72rem', fontFamily:'JetBrains Mono, monospace', marginBottom:4 }}>
              Escala: -∞ (muy anómalo) → +∞ (muy normal)
            </div>
            {/* Progress bar */}
            <div style={{ width:240, height:6, background:'#1e3a5f', borderRadius:3, overflow:'hidden' }}>
              <div style={{
                height:'100%', borderRadius:3,
                width: `${Math.min(100, Math.max(0, ((alerta.puntaje || 0) + 0.5) / 1 * 100))}%`,
                background: alerta.nivel_riesgo === 'CRITICO' ? '#ef4444' : alerta.nivel_riesgo === 'ALTO' ? '#f97316' : '#f59e0b',
                transition: 'width 0.5s ease',
              }} />
            </div>
          </div>
        </div>
      </div>

      {/* Factores */}
      {alerta.factores?.length > 0 && (
        <div style={sectionStyle}>
          <div style={{ display:'flex', justifyContent:'space-between', alignItems:'center', marginBottom:16 }}>
            <h3 style={{ fontFamily:'Space Grotesk, sans-serif', color:'#e2e8f0', fontSize:'0.9rem', fontWeight:600, margin:0 }}>
              Factores de Riesgo Detectados
            </h3>
            <AlertTriangle size={15} color="#f59e0b" />
          </div>
          <div style={{ display:'flex', flexDirection:'column', gap:8 }}>
            {alerta.factores.map((f, i) => (
              <div key={i} style={{
                display:'flex', alignItems:'center', gap:10,
                background:'#0a1628', border:'1px solid #1e3a5f', borderRadius:8, padding:'10px 14px',
              }}>
                <div style={{ width:6, height:6, borderRadius:'50%', background:'#f59e0b', flexShrink:0 }} />
                <span style={{ color:'#e2e8f0', fontSize:'0.85rem' }}>{f}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Datos de sesión */}
      <div style={sectionStyle}>
        <div style={{ display:'flex', justifyContent:'space-between', alignItems:'center', marginBottom:16 }}>
          <h3 style={{ fontFamily:'Space Grotesk, sans-serif', color:'#e2e8f0', fontSize:'0.9rem', fontWeight:600, margin:0 }}>
            Datos de la Sesión
          </h3>
          <Monitor size={15} color="#475569" />
        </div>
        <div style={{ display:'grid', gridTemplateColumns:'repeat(2, 1fr)', gap:16 }}>
          <div><span style={labelStyle}>ID Sesión</span><span style={{ ...valueStyle, fontFamily:'JetBrains Mono, monospace', fontSize:'0.75rem' }}>{alerta.sesion_id || '—'}</span></div>
          <div><span style={labelStyle}>Usuario</span><span style={valueStyle}>{alerta.usuario_nombre || alerta.usuario_id}</span></div>
          <div><span style={labelStyle}>Fecha de creación</span><span style={valueStyle}>{timeStr(alerta.fecha_creacion)}</span></div>
          {alerta.fecha_resolucion && <div><span style={labelStyle}>Fecha resolución</span><span style={valueStyle}>{timeStr(alerta.fecha_resolucion)}</span></div>}
        </div>
      </div>

      {/* Acción del analista */}
      {alerta.estado === 'NUEVA' && !done && (
        <div style={{ ...sectionStyle, border:'1px solid rgba(59,130,246,0.3)' }}>
          <h3 style={{ fontFamily:'Space Grotesk, sans-serif', color:'#e2e8f0', fontSize:'0.9rem', fontWeight:600, margin:'0 0 16px' }}>
            Acción del Analista
          </h3>
          <div style={{ display:'flex', gap:12, marginBottom:16 }}>
            {[
              { val:'RESOLVER', label:'Confirmar incidente', icon:CheckCircle, color:'#10b981' },
              { val:'DESCARTAR', label:'Falso positivo', icon:XCircle, color:'#ef4444' },
            ].map(({ val, label, icon: Icon, color }) => (
              <button key={val} onClick={() => setAccion(val)} style={{
                display:'flex', alignItems:'center', gap:8, flex:1,
                padding:'12px 16px', borderRadius:10, cursor:'pointer',
                background: accion === val ? `${color}18` : '#060b14',
                border: `1px solid ${accion === val ? color : '#1e3a5f'}`,
                color: accion === val ? color : '#64748b',
                fontFamily:'Space Grotesk, sans-serif', fontSize:'0.85rem', fontWeight:500,
                transition:'all 0.15s',
              }}>
                <Icon size={15} />
                {label}
              </button>
            ))}
          </div>
          <textarea
            value={notas} onChange={e => setNotas(e.target.value)}
            placeholder="Notas del analista (opcional)..."
            rows={3}
            style={{
              width:'100%', background:'#060b14', border:'1px solid #1e3a5f',
              borderRadius:8, padding:'10px 14px', color:'#e2e8f0', fontSize:'0.85rem',
              outline:'none', resize:'vertical', boxSizing:'border-box',
              fontFamily:'DM Sans, sans-serif', marginBottom:12,
            }}
            onFocus={e => e.target.style.borderColor = '#3b82f6'}
            onBlur={e => e.target.style.borderColor = '#1e3a5f'}
          />
          {error && <p style={{ color:'#ef4444', fontSize:'0.8rem', margin:'0 0 10px' }}>{error}</p>}
          <button onClick={handleResolver} disabled={resolving} style={{
            background: resolving ? '#1e3a5f' : 'linear-gradient(135deg, #1d4ed8, #0891b2)',
            border:'none', borderRadius:8, padding:'11px 24px', color:'white',
            fontSize:'0.875rem', fontWeight:600, cursor: resolving ? 'not-allowed' : 'pointer',
            fontFamily:'Space Grotesk, sans-serif', display:'flex', alignItems:'center', gap:8,
          }}>
            {resolving ? 'Procesando...' : 'Confirmar acción'}
          </button>
        </div>
      )}

      {/* Done state */}
      {done && (
        <div style={{ ...sectionStyle, border:'1px solid rgba(16,185,129,0.3)', textAlign:'center', padding:32 }}>
          <CheckCircle size={32} color="#10b981" style={{ marginBottom:8 }} />
          <p style={{ color:'#10b981', fontWeight:600, margin:'0 0 8px' }}>Alerta procesada correctamente</p>
          <button onClick={() => navigate('/alertas')} style={{
            background:'transparent', border:'1px solid #10b981', borderRadius:8,
            padding:'8px 20px', color:'#10b981', cursor:'pointer', fontSize:'0.85rem',
            fontFamily:'Space Grotesk, sans-serif',
          }}>
            Volver a alertas
          </button>
        </div>
      )}

      <style>{`
        @keyframes spin { to { transform: rotate(360deg); } }
        textarea::placeholder { color: #334155; }
      `}</style>
    </div>
  )
}
