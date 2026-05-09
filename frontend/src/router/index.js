import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'
import Process from '../views/MainView.vue'
import SimulationView from '../views/SimulationView.vue'
import SimulationRunView from '../views/SimulationRunView.vue'
import ReportView from '../views/ReportView.vue'
import InteractionView from '../views/InteractionView.vue'
import AISettingsView from '../views/AISettingsView.vue'
import StrategicModeView from '../views/StrategicModeView.vue'
import OperationDetailView from '../views/OperationDetailView.vue'
import OperationsView from '../views/OperationsView.vue'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home
  },
  {
    path: '/process/:projectId',
    name: 'Process',
    component: Process,
    props: true
  },
  {
    path: '/simulation/:simulationId',
    name: 'Simulation',
    component: SimulationView,
    props: true
  },
  {
    path: '/simulation/:simulationId/start',
    name: 'SimulationRun',
    component: SimulationRunView,
    props: true
  },
  {
    path: '/report/:reportId',
    name: 'Report',
    component: ReportView,
    props: true
  },
  {
    path: '/interaction/:reportId',
    name: 'Interaction',
    component: InteractionView,
    props: true
  },
  {
    path: '/ai-settings',
    name: 'AISettings',
    component: AISettingsView
  },
  {
    path: '/strategic/:modeId',
    name: 'StrategicMode',
    component: StrategicModeView,
    props: true
  },
  {
    path: '/operations',
    name: 'Operations',
    component: OperationsView
  },
  {
    path: '/operations/:operationId',
    name: 'OperationDetail',
    component: OperationDetailView,
    props: true
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
