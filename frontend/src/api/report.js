import service, { requestWithRetry } from './index'

/* Internal note */
export const generateReport = (data) => {
  return requestWithRetry(() => service.post('/api/report/generate', data), 3, 1000)
}

/* Internal note */
export const getReportStatus = (reportId) => {
  return service.get(`/api/report/generate/status`, { params: { report_id: reportId } })
}

/* Internal note */
export const getAgentLog = (reportId, fromLine = 0) => {
  return service.get(`/api/report/${reportId}/agent-log`, { params: { from_line: fromLine } })
}

/* Internal note */
export const getConsoleLog = (reportId, fromLine = 0) => {
  return service.get(`/api/report/${reportId}/console-log`, { params: { from_line: fromLine } })
}

/* Internal note */
export const getReport = (reportId) => {
  return service.get(`/api/report/${reportId}`)
}

export const getReportSections = (reportId) => {
  return service.get(`/api/report/${reportId}/sections`)
}

/* Internal note */
export const chatWithReport = (data) => {
  return requestWithRetry(() => service.post('/api/report/chat', data), 3, 1000)
}

export const getReportChatHistory = (reportId) => {
  return service.get(`/api/report/${reportId}/chat/history`)
}

export const clearReportChatHistory = (reportId) => {
  return service.delete(`/api/report/${reportId}/chat/history`)
}
