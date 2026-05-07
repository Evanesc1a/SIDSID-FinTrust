import { useState, useEffect, useCallback } from 'react'
import { metricasService } from '../services/metricasservice'

export function useMetricas(intervalo = 0) {
  const [metricas, setMetricas] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  const cargar = useCallback(async () => {
    try {
      const res = await metricasService.obtener()
      setMetricas(res.data)
      setError(null)
    } catch (e) {
      setError(e.response?.data?.error || 'Error al cargar métricas')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    cargar()
    if (intervalo > 0) {
      const id = setInterval(cargar, intervalo)
      return () => clearInterval(id)
    }
  }, [cargar, intervalo])

  return { metricas, loading, error, recargar: cargar }
}
