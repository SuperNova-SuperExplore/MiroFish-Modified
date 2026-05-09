/* Internal note */
import { reactive } from 'vue'

const state = reactive({
  files: [],
  simulationRequirement: '',
  operationMode: null,
  isPending: false
})

export function setPendingUpload(files, requirement, operationMode = null) {
  state.files = files
  state.simulationRequirement = requirement
  state.operationMode = operationMode
  state.isPending = true
}

export function getPendingUpload() {
  return {
    files: state.files,
    simulationRequirement: state.simulationRequirement,
    operationMode: state.operationMode,
    isPending: state.isPending
  }
}

export function clearPendingUpload() {
  state.files = []
  state.simulationRequirement = ''
  state.operationMode = null
  state.isPending = false
}

export default state
