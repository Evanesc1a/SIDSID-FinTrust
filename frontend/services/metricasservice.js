import api from './api'

export const metricasService = {
  obtener: () => api.get('/metricas'),
}
