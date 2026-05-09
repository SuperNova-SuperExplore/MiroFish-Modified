<template>
  <main class="ops-page">
    <section class="panel" v-if="loading">Memuat operation...</section>
    <section class="panel" v-else-if="error">{{ error }}</section>
    <template v-else-if="operation">
      <section class="hero panel">
        <div>
          <p class="eyebrow">{{ operation.mode }}</p>
          <h1>{{ operation.title || operation.operation_id }}</h1>
          <p class="muted">{{ operation.operation_id }} · {{ operation.created_at }}</p>
        </div>
        <div class="hero-actions">
          <router-link class="btn muted-btn" to="/operations">Riwayat</router-link>
          <router-link class="btn muted-btn" to="/">Command Center</router-link>
        </div>
      </section>

      <section class="grid">
        <article class="panel main-output">
          <h2>Output</h2>
          <JsonTree :value="operation.output" />
        </article>
        <aside class="panel side">
          <h2>Metadata</h2>
          <label>Judul<input v-model="edit.title" /></label>
          <label>Status<input v-model="edit.status" /></label>
          <label>Tags<input v-model="tagsText" placeholder="mvp, penting" /></label>
          <label>Catatan<textarea v-model="edit.notes" rows="5" /></label>
          <button class="btn" @click="saveMeta">Simpan Metadata</button>
          <div v-if="message" class="notice">{{ message }}</div>

          <h2>Aksi Lanjutan</h2>
          <button v-for="action in actions" :key="action.id" class="action" @click="runAction(action)">
            <strong>{{ action.label }}</strong><span>{{ action.description }}</span>
          </button>
        </aside>
      </section>
    </template>
  </main>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import service from '../api/index'
import strategicApi from '../api/strategic'
import JsonTree from '../components/JsonTree.vue'

const props = defineProps({ operationId: { type: String, required: true } })
const router = useRouter()
const operation = ref(null)
const actions = ref([])
const loading = ref(false)
const error = ref('')
const message = ref('')
const tagsText = ref('')
const edit = reactive({ title: '', notes: '', status: '' })

const load = async () => {
  loading.value = true
  try {
    const res = await strategicApi.getOperation(props.operationId)
    operation.value = res.data
    edit.title = operation.value.title || ''
    edit.notes = operation.value.notes || ''
    edit.status = operation.value.status || ''
    tagsText.value = (operation.value.tags || []).join(', ')
    const next = await strategicApi.getNextActions(props.operationId)
    actions.value = next.data.actions || []
  } catch (e) { error.value = e.message } finally { loading.value = false }
}

const saveMeta = async () => {
  message.value = ''
  await service.patch(`/api/strategic/operations/${props.operationId}`, edit)
  await service.put(`/api/strategic/operations/${props.operationId}/tags`, { tags: tagsText.value })
  message.value = 'Metadata tersimpan.'
  await load()
}

const runAction = async (action) => {
  if (action.method === 'GET') {
    window.open(action.endpoint, '_blank')
    return
  }
  const res = await service.post(action.endpoint, action.payload_template || {})
  router.push({ name: 'OperationDetail', params: { operationId: res.operation_id } })
}

onMounted(load)
</script>

<style scoped>
.ops-page{min-height:100vh;padding:28px;color:#eef4ff;background:radial-gradient(circle at top left,rgba(104,225,253,.16),transparent 34%),#05070d}.panel{border:1px solid rgba(255,255,255,.11);background:rgba(9,14,27,.82);border-radius:26px;padding:24px;box-shadow:0 26px 80px rgba(0,0,0,.34)}.hero{display:flex;justify-content:space-between;gap:18px;margin-bottom:18px}.eyebrow{color:#68e1fd;letter-spacing:.16em;text-transform:uppercase;font-size:12px}h1{font-size:clamp(34px,5vw,64px);margin:8px 0;letter-spacing:-.06em}.muted{color:#8e9aaf}.grid{display:grid;grid-template-columns:1fr 360px;gap:18px}.main-output{overflow:auto}.side{display:grid;gap:14px;align-content:start}label{display:grid;gap:8px;color:#dbe7ff}input,textarea{color:#eef4ff;border:1px solid rgba(255,255,255,.12);border-radius:14px;background:rgba(255,255,255,.06);padding:12px}.btn{border:0;border-radius:999px;padding:12px 16px;font-weight:800;cursor:pointer;color:#041018;background:linear-gradient(135deg,#68e1fd,#c8a96a);text-decoration:none}.muted-btn{color:#eef4ff;background:rgba(255,255,255,.08);border:1px solid rgba(255,255,255,.14)}.hero-actions{display:flex;gap:10px;align-items:flex-start}.action{display:grid;gap:6px;text-align:left;color:#eef4ff;border:1px solid rgba(255,255,255,.1);border-radius:16px;background:rgba(255,255,255,.06);padding:14px;cursor:pointer}.action span{color:#8e9aaf;font-size:13px}.notice{color:#7cffb2}@media(max-width:900px){.hero,.grid{grid-template-columns:1fr;display:grid}.side{grid-row:auto}}
</style>
