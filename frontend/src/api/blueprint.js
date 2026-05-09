import service, { requestWithRetry } from './index'

export const startBlueprintRun = (data) => {
  return requestWithRetry(() => service.post('/api/blueprint/runs', data), 1, 1000)
}

export const getBlueprintRun = (runId) => {
  return service.get(`/api/blueprint/runs/${runId}`)
}

export const getBlueprintRunBySimulation = (simulationId) => {
  return service.get(`/api/blueprint/runs/by-simulation/${simulationId}`)
}

export const getBlueprintEvents = (runId) => {
  return service.get(`/api/blueprint/runs/${runId}/events`)
}

export const getBlueprintArtifacts = (runId) => {
  return service.get(`/api/blueprint/runs/${runId}/artifacts`)
}
