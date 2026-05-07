import api from './api'

export const alertasService = {
  listar: (params = {}) => api.get('/alertas', { params }),
  obtener: (id) => api.get(`/alertas/${id}`),
  resolver: (id, accion, notas = '') => api.put(`/alertas/${id}/resolver`, { accion, notas }),
  resumen: () => api.get('/alertas/resumen'),
}
