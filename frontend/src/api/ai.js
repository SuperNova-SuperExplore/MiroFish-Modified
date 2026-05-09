import service from './index'

export const aiApi = {
  getProviders() {
    return service.get('/api/ai/providers')
  },

  getActive() {
    return service.get('/api/ai/active')
  },

  saveProvider(data) {
    return service.post('/api/ai/providers', data)
  },

  getProvider(providerId) {
    return service.get(`/api/ai/providers/${providerId}`)
  },

  deleteProvider(providerId) {
    return service.delete(`/api/ai/providers/${providerId}`)
  },

  activateProvider(providerId) {
    return service.post(`/api/ai/providers/${providerId}/activate`)
  },

  testProvider(data) {
    return service.post('/api/ai/test', data)
  },

  getModels(params = {}) {
    return service.get('/api/ai/models', { params })
  }
}

export default aiApi
