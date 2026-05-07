import { useState, useEffect, useCallback } from 'react'
import { alertasService } from '../services/alertasservice'

export function useAlertas(filtros = {}) {
  const [alertas, setAlertas] = useState([])
  const [resumen, setResumen] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  const cargar = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const [listRes, resRes] = await Promise.all([
        alertasService.listar(filtros),
        alertasService.resumen(),
      ])
      setAlertas(listRes.data)
      setResumen(resRes.data)
    } catch (e) {
      setError(e.response?.data?.error || 'Error al cargar alertas')
    } finally {
      setLoading(false)
    }
  }, [JSON.stringify(filtros)])

  useEffect(() => { cargar() }, [cargar])

  const resolver = async (id, accion, notas) => {
    await alertasService.resolver(id, accion, notas)
    await cargar()
  }

  return { alertas, resumen, loading, error, recargar: cargar, resolver }
}
