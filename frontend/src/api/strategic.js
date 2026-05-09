import service from './index'

export const strategicApi = {
  getModes() {
    return service.get('/api/strategic/modes')
  },

  listOperations(params = {}) {
    return service.get('/api/strategic/operations', { params })
  },

  getOperation(operationId) {
    return service.get(`/api/strategic/operations/${operationId}`)
  },

  getNextActions(operationId) {
    return service.get(`/api/strategic/operations/${operationId}/next-actions`)
  }
}

export default strategicApi
