import service, { requestWithRetry } from './index'

/* Internal note */
export function generateOntology(formData) {
  return requestWithRetry(() =>
    service({
      url: '/api/graph/ontology/generate',
      method: 'post',
      data: formData,
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
  )
}

/* Internal note */
export function buildGraph(data) {
  return requestWithRetry(() =>
    service({
      url: '/api/graph/build',
      method: 'post',
      data
    })
  )
}

/* Internal note */
export function getTaskStatus(taskId) {
  return service({
    url: `/api/graph/task/${taskId}`,
    method: 'get'
  })
}

/* Internal note */
export function getGraphData(graphId) {
  return service({
    url: `/api/graph/data/${graphId}`,
    method: 'get'
  })
}

/* Internal note */
export function getProject(projectId) {
  return service({
    url: `/api/graph/project/${projectId}`,
    method: 'get'
  })
}

/**
 * Auto-generate seed files from a topic via web search + LLM
 * @param {Object} data - { topic, lang, num_queries }
 * @returns {Promise}
 */
export function generateSeed(data) {
  return requestWithRetry(() =>
    service({
      url: '/api/graph/seed/generate',
      method: 'post',
      data,
      timeout: 300000  // 5 min timeout — seed gen takes time
    })
  )
}
