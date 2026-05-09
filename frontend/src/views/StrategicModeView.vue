<template>
  <main class="runner-page">
    <section class="hero panel">
      <div>
        <p class="eyebrow">Strategic Runner</p>
        <h1>{{ title }}</h1>
        <p class="muted">{{ description }}</p>
      </div>
      <div class="hero-actions">
        <router-link class="btn muted-btn" to="/operations">Riwayat</router-link>
        <router-link class="btn muted-btn" to="/">Command Center</router-link>
      </div>
    </section>

    <section v-if="error" class="panel error">{{ error }}</section>

    <section class="grid">
      <article class="panel">
        <div v-if="isBlueprintLab" class="submodes">
          <button v-for="sub in blueprintSubModes" :key="sub.id" :class="{active: activeSubMode?.id === sub.id}" @click="selectSubMode(sub)">{{ sub.name }}</button>
        </div>

        <div class="form-grid">
          <label v-for="field in fields" :key="field.name" :class="{wide: ['textarea','multi_select','text_or_file','operation_ref'].includes(field.type)}">
            {{ field.label || field.name }}
            <textarea v-if="['textarea','text_or_file','operation_ref'].includes(field.type)" v-model="form[field.name]" rows="field.type === 'textarea' ? 7 : 4" :placeholder="placeholder(field)" />
            <select v-else-if="field.type === 'select'" v-model="form[field.name]">
              <option v-for="opt in field.options || []" :key="opt" :value="opt">{{ opt }}</option>
            </select>
            <input v-else-if="field.type === 'multi_select'" v-model="form[field.name]" :placeholder="`Pisahkan dengan koma: ${(field.options || []).join(', ')}`" />
            <input v-else v-model="form[field.name]" :placeholder="placeholder(field)" />
          </label>
        </div>

        <div class="buttons">
          <button class="btn" :disabled="submitting" @click="submit">{{ submitting ? 'Menjalankan...' : (activeConfig?.cta || mode?.cta || 'Jalankan') }}</button>
        </div>
      </article>

      <aside class="panel help">
        <h2>Cocok untuk</h2>
        <ul><li v-for="item in mode?.best_for || []" :key="item">{{ item }}</li></ul>
        <h2>Output</h2>
        <p class="muted">Hasil akan disimpan sebagai operation. Setelah selesai, lo bisa audit/revisi/export dari halaman detail.</p>
      </aside>
    </section>
  </main>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import service from '../api/index'
import strategicApi from '../api/strategic'

const props = defineProps({ modeId: { type: String, required: true } })
const router = useRouter()
const modes = ref([])
const mode = computed(() => modes.value.find(m => m.id === props.modeId))
const activeSubMode = ref(null)
const form = reactive({})
const error = ref('')
const submitting = ref(false)
const isBlueprintLab = computed(() => props.modeId === 'blueprint_lab')
const blueprintSubModes = computed(() => mode.value?.sub_modes || [])
const activeConfig = computed(() => isBlueprintLab.value ? activeSubMode.value : mode.value)
const fields = computed(() => activeConfig.value?.input_fields || [])
const title = computed(() => activeConfig.value?.name || mode.value?.label || props.modeId)
const description = computed(() => mode.value?.description || 'Jalankan mode strategis.')

const placeholder = field => field.default || field.label || field.name
const applyDefaults = () => {
  for (const key of Object.keys(form)) delete form[key]
  for (const field of fields.value) form[field.name] = field.default || ''
}
const selectSubMode = sub => { activeSubMode.value = sub; applyDefaults() }
const load = async () => {
  const res = await strategicApi.getModes(); modes.value = res.data || []
  if (isBlueprintLab.value && blueprintSubModes.value.length) activeSubMode.value = blueprintSubModes.value[0]
  applyDefaults()
}
const normalizePayload = () => {
  const payload = {}
  for (const field of fields.value) {
    let value = form[field.name]
    if (field.type === 'multi_select') value = String(value || '').split(',').map(x => x.trim()).filter(Boolean)
    payload[field.name] = value
  }
  return payload
}
const submit = async () => {
  error.value = ''; submitting.value = true
  try {
    const endpoint = activeConfig.value?.endpoint
    if (!endpoint) throw new Error('Endpoint mode belum tersedia.')
    const res = await service.post(endpoint, normalizePayload())
    router.push({ name: 'OperationDetail', params: { operationId: res.operation_id } })
  } catch (e) { error.value = e.message } finally { submitting.value = false }
}
onMounted(load)
</script>

<style scoped>
.runner-page{min-height:100vh;padding:28px;color:#eef4ff;background:radial-gradient(circle at top left,rgba(104,225,253,.16),transparent 34%),#05070d}.panel{border:1px solid rgba(255,255,255,.11);background:rgba(9,14,27,.82);border-radius:26px;padding:24px;box-shadow:0 26px 80px rgba(0,0,0,.34)}.hero{display:flex;justify-content:space-between;gap:18px;margin-bottom:18px}.eyebrow{color:#68e1fd;letter-spacing:.16em;text-transform:uppercase;font-size:12px}h1{font-size:clamp(36px,6vw,72px);margin:8px 0;letter-spacing:-.06em}.muted{color:#8e9aaf;line-height:1.7}.grid{display:grid;grid-template-columns:1fr 340px;gap:18px}.form-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:14px}label{display:grid;gap:8px;color:#dbe7ff}.wide{grid-column:1/-1}input,textarea,select{color:#eef4ff;border:1px solid rgba(255,255,255,.12);border-radius:14px;background:rgba(255,255,255,.06);padding:12px}textarea{resize:vertical}.btn{border:0;border-radius:999px;padding:12px 16px;font-weight:800;cursor:pointer;color:#041018;background:linear-gradient(135deg,#68e1fd,#c8a96a);text-decoration:none}.muted-btn{color:#eef4ff;background:rgba(255,255,255,.08);border:1px solid rgba(255,255,255,.14)}.hero-actions,.buttons,.submodes{display:flex;gap:10px;flex-wrap:wrap}.buttons{margin-top:18px}.submodes{margin-bottom:18px}.submodes button{color:#eef4ff;border:1px solid rgba(255,255,255,.13);border-radius:999px;background:rgba(255,255,255,.07);padding:10px 14px;cursor:pointer}.submodes button.active{color:#041018;background:#68e1fd}.help ul{padding-left:18px;color:#8e9aaf;line-height:1.7}.error{color:#ff9aac;margin-bottom:18px}@media(max-width:900px){.hero,.grid{display:grid;grid-template-columns:1fr}.form-grid{grid-template-columns:1fr}}
</style>
