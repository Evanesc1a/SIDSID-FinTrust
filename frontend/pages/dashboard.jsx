import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  AreaChart, Area, BarChart, Bar, XAxis, YAxis,
  Tooltip, ResponsiveContainer, Cell
} from 'recharts'
import { useMetricas } from '../hooks/usemetricas'
import { useAlertas } from '../hooks/usealertas'
import KpiCard from '../components/kpicard'
import AlertaRow from '../components/alertarow'
import {
  Shield, Activity, AlertTriangle, Users, Zap,
  TrendingUp, Target, CheckCircle, RefreshCw
} from 'lucide-react'

const NIVEL_COLORS = { BAJO:'#10b981', MEDIO:'#f59e0b', ALTO:'#f97316', CRITICO:'#ef4444' }

function CustomTooltip({ active, payload, label }) {
  if (!active || !payload?.length) return null
  return (
    <div style={{ background:'#0d1b2e', border:'1px solid #1e3a5f', borderRadius:8, padding:'8px 14px', fontSize:'0.8rem' }}>
      <p style={{ color:'#94a3b8', margin:'0 0 4px' }}>{label}</p>
      {payload.map((p, i) => (
        <p key={i} style={{ color: p.color || '#3b82f6', margin:0 }}>{p.name}: <strong>{p.value}</strong></p>
      ))}
    </div>
  )
}

export default function Dashboard() {
  const { metricas, loading, recargar } = useMetricas(30000)
  const { alertas } = useAlertas({ estado: 'NUEVA', limite: 5 })
  const navigate = useNavigate()
  const [refreshing, setRefreshing] = useState(false)

  const handleRefresh = async () => {
    setRefreshing(true)
    await recargar()
    setTimeout(() => setRefreshing(false), 600)
  }

  const distribData = metricas ? Object.entries(metricas.alertas.distribucion_nivel).map(([k, v]) => ({
    nivel: k, count: v, color: NIVEL_COLORS[k],
  })) : []

  return (
    <div style={{ padding:'28px 32px', maxWidth:1400, margin:'0 auto' }}>
      {/* Header */}
      <div style={{ display:'flex', justifyContent:'space-between', alignItems:'center', marginBottom:32 }}>
        <div>
          <h1 style={{ fontFamily:'Space Grotesk, sans-serif', fontSize:'1.5rem', fontWeight:700, color:'#e2e8f0', margin:0 }}>
            Panel de Monitoreo
          </h1>
          <p style={{ color:'#475569', fontSize:'0.8rem', margin:'4px 0 0', fontFamily:'JetBrains Mono, monospace' }}>
            SIDSID — Detección de anomalías en tiempo real
          </p>
        </div>
        <div style={{ display:'flex', gap:10, alignItems:'center' }}>
          <div style={{ display:'flex', alignItems:'center', gap:6, color:'#10b981', fontSize:'0.75rem', fontFamily:'JetBrains Mono, monospace' }}>
            <span style={{ width:7, height:7, background:'#10b981', borderRadius:'50%', animation:'pulse 2s infinite' }} />
            SISTEMA ACTIVO
          </div>
          <button onClick={handleRefresh} style={{
            background:'#0a1628', border:'1px solid #1e3a5f', borderRadius:8,
            padding:'7px 10px', cursor:'pointer', color:'#64748b', display:'flex',
            transition:'all 0.15s',
          }}
          onMouseEnter={e => { e.currentTarget.style.borderColor = '#3b82f6'; e.currentTarget.style.color = '#3b82f6' }}
          onMouseLeave={e => { e.currentTarget.style.borderColor = '#1e3a5f'; e.currentTarget.style.color = '#64748b' }}>
            <RefreshCw size={14} style={{ animation: refreshing ? 'spin 0.6s linear infinite' : 'none' }} />
          </button>
        </div>
      </div>

      {/* KPI Grid */}
      <div style={{ display:'grid', gridTemplateColumns:'repeat(4, 1fr)', gap:16, marginBottom:28 }}>
        <KpiCard
          titulo="Sesiones (24h)"
          valor={metricas?.sesiones.total_24h}
          subtitulo={`${metricas?.sesiones.anomalas_24h || 0} anómalas detectadas`}
          icono={Activity}
          color="#3b82f6"
          loading={loading}
        />
        <KpiCard
          titulo="Alertas nuevas"
          valor={metricas?.alertas.nuevas}
          subtitulo={`${metricas?.alertas.criticas || 0} críticas sin revisar`}
          icono={AlertTriangle}
          color="#ef4444"
          loading={loading}
        />
        <KpiCard
          titulo="Tasa anomalía"
          valor={metricas ? `${metricas.sesiones.tasa_anomalia}%` : null}
          subtitulo="Últimas 24 horas"
          icono={TrendingUp}
          color="#f59e0b"
          loading={loading}
        />
        <KpiCard
          titulo="Usuarios activos"
          valor={metricas?.usuarios.activos}
          subtitulo={`${metricas?.usuarios.bloqueados || 0} bloqueados`}
          icono={Users}
          color="#10b981"
          loading={loading}
        />
      </div>

      {/* Charts row */}
      <div style={{ display:'grid', gridTemplateColumns:'2fr 1fr', gap:16, marginBottom:28 }}>
        {/* Tendencia */}
        <div style={{ background:'#0d1b2e', border:'1px solid #1e3a5f', borderRadius:12, padding:'22px 24px' }}>
          <div style={{ display:'flex', justifyContent:'space-between', alignItems:'center', marginBottom:20 }}>
            <div>
              <h3 style={{ fontFamily:'Space Grotesk, sans-serif', color:'#e2e8f0', fontSize:'0.9rem', fontWeight:600, margin:0 }}>
                Tendencia de anomalías
              </h3>
              <p style={{ color:'#475569', fontSize:'0.72rem', margin:'3px 0 0', fontFamily:'JetBrains Mono, monospace' }}>Últimos 7 días</p>
            </div>
            <Activity size={16} color="#3b82f6" />
          </div>
          {loading ? (
            <div style={{ height:200, background:'#0a1628', borderRadius:8, animation:'pulse 1.5s infinite' }} />
          ) : (
            <ResponsiveContainer width="100%" height={200}>
              <AreaChart data={metricas?.tendencia_anomalias || []}>
                <defs>
                  <linearGradient id="gradBlue" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%"  stopColor="#3b82f6" stopOpacity={0.25} />
                    <stop offset="95%" stopColor="#3b82f6" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <XAxis dataKey="fecha" tick={{ fill:'#475569', fontSize:11, fontFamily:'JetBrains Mono, monospace' }}
                  axisLine={false} tickLine={false}
                  tickFormatter={v => v?.slice(5)} />
                <YAxis tick={{ fill:'#475569', fontSize:11 }} axisLine={false} tickLine={false} />
                <Tooltip content={<CustomTooltip />} />
                <Area type="monotone" dataKey="anomalas" name="Anómalas"
                  stroke="#3b82f6" strokeWidth={2} fill="url(#gradBlue)" dot={{ fill:'#3b82f6', r:3 }} />
              </AreaChart>
            </ResponsiveContainer>
          )}
        </div>

        {/* Distribución por nivel */}
        <div style={{ background:'#0d1b2e', border:'1px solid #1e3a5f', borderRadius:12, padding:'22px 24px' }}>
          <div style={{ display:'flex', justifyContent:'space-between', alignItems:'center', marginBottom:20 }}>
            <div>
              <h3 style={{ fontFamily:'Space Grotesk, sans-serif', color:'#e2e8f0', fontSize:'0.9rem', fontWeight:600, margin:0 }}>
                Alertas por nivel
              </h3>
              <p style={{ color:'#475569', fontSize:'0.72rem', margin:'3px 0 0', fontFamily:'JetBrains Mono, monospace' }}>Últimos 7 días</p>
            </div>
            <Target size={16} color="#f59e0b" />
          </div>
          {loading ? (
            <div style={{ height:200, background:'#0a1628', borderRadius:8, animation:'pulse 1.5s infinite' }} />
          ) : (
            <ResponsiveContainer width="100%" height={200}>
              <BarChart data={distribData} barSize={32}>
                <XAxis dataKey="nivel" tick={{ fill:'#475569', fontSize:10, fontFamily:'JetBrains Mono, monospace' }}
                  axisLine={false} tickLine={false} />
                <YAxis tick={{ fill:'#475569', fontSize:11 }} axisLine={false} tickLine={false} />
                <Tooltip content={<CustomTooltip />} />
                <Bar dataKey="count" name="Alertas" radius={[4,4,0,0]}>
                  {distribData.map((entry, i) => (
                    <Cell key={i} fill={entry.color} opacity={0.85} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          )}
        </div>
      </div>

      {/* Métricas IA */}
      {metricas?.modelo_ia && (
        <div style={{ background:'#0d1b2e', border:'1px solid #1e3a5f', borderRadius:12, padding:'22px 24px', marginBottom:28 }}>
          <div style={{ display:'flex', justifyContent:'space-between', alignItems:'center', marginBottom:16 }}>
            <h3 style={{ fontFamily:'Space Grotesk, sans-serif', color:'#e2e8f0', fontSize:'0.9rem', fontWeight:600, margin:0 }}>
              Métricas del Modelo IA — Isolation Forest
            </h3>
            <Zap size={16} color="#0891b2" />
          </div>
          <div style={{ display:'grid', gridTemplateColumns:'repeat(5, 1fr)', gap:16 }}>
            {[
              { label:'Precisión', val: metricas.modelo_ia.precision, fmt: v => `${(v*100).toFixed(1)}%` },
              { label:'Recall', val: metricas.modelo_ia.recall, fmt: v => `${(v*100).toFixed(1)}%` },
              { label:'F1-Score', val: metricas.modelo_ia.f1_score, fmt: v => `${(v*100).toFixed(1)}%` },
              { label:'FPR', val: metricas.modelo_ia.fpr, fmt: v => `${(v*100).toFixed(1)}%` },
              { label:'Train samples', val: metricas.modelo_ia.n_train, fmt: v => v?.toLocaleString() },
            ].map(({ label, val, fmt }) => (
              <div key={label} style={{ textAlign:'center', padding:'12px', background:'#0a1628', borderRadius:8, border:'1px solid #1e3a5f' }}>
                <div style={{ fontFamily:'Space Grotesk, sans-serif', fontSize:'1.3rem', fontWeight:700, color:'#0891b2' }}>
                  {val !== undefined ? fmt(val) : '—'}
                </div>
                <div style={{ color:'#475569', fontSize:'0.7rem', marginTop:4, fontFamily:'JetBrains Mono, monospace', textTransform:'uppercase', letterSpacing:'0.06em' }}>
                  {label}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Últimas alertas */}
      <div style={{ background:'#0d1b2e', border:'1px solid #1e3a5f', borderRadius:12, padding:'22px 24px' }}>
        <div style={{ display:'flex', justifyContent:'space-between', alignItems:'center', marginBottom:16 }}>
          <h3 style={{ fontFamily:'Space Grotesk, sans-serif', color:'#e2e8f0', fontSize:'0.9rem', fontWeight:600, margin:0 }}>
            Alertas recientes sin revisar
          </h3>
          <button onClick={() => navigate('/alertas')} style={{
            background:'transparent', border:'1px solid #1e3a5f', borderRadius:6,
            padding:'5px 12px', color:'#3b82f6', fontSize:'0.75rem', cursor:'pointer',
            fontFamily:'Space Grotesk, sans-serif',
          }}>
            Ver todas →
          </button>
        </div>
        {alertas.length === 0 ? (
          <div style={{ textAlign:'center', padding:'32px', color:'#475569' }}>
            <CheckCircle size={28} color="#10b981" style={{ marginBottom:8 }} />
            <p style={{ margin:0, fontSize:'0.85rem' }}>No hay alertas pendientes</p>
          </div>
        ) : (
          <div>
            {/* Header */}
            <div style={{
              display:'grid', gridTemplateColumns:'130px 1fr 160px 100px 90px 36px',
              gap:16, padding:'8px 20px', marginBottom:6,
            }}>
              {['Nivel', 'Descripción', 'Factores', 'Tiempo', 'Estado', ''].map((h, i) => (
                <span key={i} style={{ color:'#334155', fontSize:'0.68rem', fontFamily:'JetBrains Mono, monospace', textTransform:'uppercase', letterSpacing:'0.08em' }}>{h}</span>
              ))}
            </div>
            {alertas.map(a => <AlertaRow key={a.id} alerta={a} />)}
          </div>
        )}
      </div>

      <style>{`
        @keyframes spin { to { transform: rotate(360deg); } }
        @keyframes pulse { 0%,100% { opacity:1; } 50% { opacity:0.5; } }
      `}</style>
    </div>
  )
}
