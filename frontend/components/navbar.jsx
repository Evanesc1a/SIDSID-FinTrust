import React, { useState } from 'react'
import { NavLink, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/authcontext'
import {
  Shield, LayoutDashboard, Bell, Users,
  LogOut, ChevronDown, Activity, Menu, X
} from 'lucide-react'

const NAV = [
  { to: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { to: '/alertas',   label: 'Alertas',   icon: Bell },
  { to: '/usuarios',  label: 'Usuarios',  icon: Users },
]

export default function Navbar({ alertasNuevas = 0 }) {
  const { usuario, logout } = useAuth()
  const navigate = useNavigate()
  const [menuOpen, setMenuOpen] = useState(false)

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  return (
    <nav style={{
      background: '#0a1628',
      borderBottom: '1px solid #1e3a5f',
      height: 60, display:'flex', alignItems:'center',
      padding: '0 24px', position:'sticky', top:0, zIndex:100,
      backdropFilter: 'blur(10px)',
    }}>
      {/* Logo */}
      <div style={{ display:'flex', alignItems:'center', gap:10, marginRight:40 }}>
        <div style={{
          background: 'linear-gradient(135deg, #1d4ed8, #0891b2)',
          borderRadius: 8, padding:6, display:'flex',
        }}>
          <Shield size={18} color="white" />
        </div>
        <div>
          <div style={{ fontFamily:'Space Grotesk, sans-serif', fontWeight:700, fontSize:'0.95rem', color:'#e2e8f0', lineHeight:1 }}>
            SIDSID
          </div>
          <div style={{ fontSize:'0.6rem', color:'#475569', letterSpacing:'0.1em', fontFamily:'JetBrains Mono, monospace' }}>
            FINTRUST
          </div>
        </div>
      </div>

      {/* Nav links */}
      <div style={{ display:'flex', gap:4, flex:1 }}>
        {NAV.map(({ to, label, icon: Icon }) => (
          <NavLink key={to} to={to} style={({ isActive }) => ({
            display:'flex', alignItems:'center', gap:7,
            padding:'6px 14px', borderRadius:8,
            color: isActive ? '#e2e8f0' : '#64748b',
            background: isActive ? '#1e3a5f' : 'transparent',
            textDecoration:'none', fontSize:'0.85rem', fontWeight:500,
            transition:'all 0.15s', position:'relative',
          })}>
            <Icon size={15} />
            {label}
            {label === 'Alertas' && alertasNuevas > 0 && (
              <span style={{
                background:'#ef4444', color:'white',
                borderRadius:10, padding:'1px 6px',
                fontSize:'0.65rem', fontWeight:700,
                fontFamily:'JetBrains Mono, monospace',
                minWidth:18, textAlign:'center',
              }}>
                {alertasNuevas > 99 ? '99+' : alertasNuevas}
              </span>
            )}
          </NavLink>
        ))}
      </div>

      {/* User menu */}
      {usuario && (
        <div style={{ display:'flex', alignItems:'center', gap:10 }}>
          <div style={{
            display:'flex', alignItems:'center', gap:8,
            padding:'6px 12px', border:'1px solid #1e3a5f',
            borderRadius:8, cursor:'default',
          }}>
            <div style={{
              width:28, height:28, borderRadius:'50%',
              background:'linear-gradient(135deg, #1d4ed8, #0891b2)',
              display:'flex', alignItems:'center', justifyContent:'center',
              fontSize:'0.75rem', fontWeight:700, color:'white',
            }}>
              {usuario.nombre?.[0]?.toUpperCase() || 'A'}
            </div>
            <div>
              <div style={{ fontSize:'0.8rem', color:'#e2e8f0', fontWeight:500 }}>{usuario.nombre}</div>
              <div style={{ fontSize:'0.65rem', color:'#475569', fontFamily:'JetBrains Mono, monospace', textTransform:'uppercase' }}>
                {usuario.rol}
              </div>
            </div>
          </div>
          <button
            onClick={handleLogout}
            style={{
              background:'transparent', border:'1px solid #1e3a5f',
              borderRadius:8, padding:'7px 10px', cursor:'pointer',
              color:'#64748b', display:'flex', alignItems:'center',
              transition:'all 0.15s',
            }}
            onMouseEnter={e => { e.currentTarget.style.borderColor = '#ef444455'; e.currentTarget.style.color = '#ef4444' }}
            onMouseLeave={e => { e.currentTarget.style.borderColor = '#1e3a5f'; e.currentTarget.style.color = '#64748b' }}
            title="Cerrar sesión"
          >
            <LogOut size={15} />
          </button>
        </div>
      )}
    </nav>
  )
}
