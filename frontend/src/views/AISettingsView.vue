<template>
  <main class="ai-settings-page">
    <section class="hero-panel">
      <div>
        <p class="eyebrow">System Core</p>
        <h1>AI Provider Settings</h1>
        <p class="hero-copy">
          Pilih model yang akan menjalankan prediksi, blueprint, report, dan agent simulasi MiroFish.
        </p>
      </div>
      <router-link to="/" class="ghost-link">← Kembali ke Command Center</router-link>
    </section>

    <section class="status-grid">
      <article class="status-card primary">
        <span>Provider Aktif</span>
        <strong>{{ activeProvider?.name || 'Belum dipilih' }}</strong>
        <p>{{ activeProvider?.base_url || 'Fallback ke konfigurasi .env jika belum ada provider aktif.' }}</p>
      </article>
      <article class="status-card">
        <span>Model Aktif</span>
        <strong>{{ activeProvider?.default_model || '-' }}</strong>
        <p>{{ activeProvider?.provider_id || 'env' }}</p>
      </article>
      <article class="status-card">
        <span>Credential</span>
        <strong>{{ activeProvider?.api_key_masked || 'Tidak tersedia' }}</strong>
        <p>Key disimpan lokal di backend/uploads dan tidak masuk Git.</p>
      </article>
    </section>

    <section v-if="error" class="notice error">{{ error }}</section>
    <section v-if="successMessage" class="notice success">{{ successMessage }}</section>

    <section class="content-grid">
      <aside class="provider-list panel">
        <div class="section-head">
          <div>
            <p class="eyebrow">Providers</p>
            <h2>Daftar AI</h2>
          </div>
          <button class="secondary-button" @click="newProvider">+ Baru</button>
        </div>

        <div v-if="loading" class="empty-state">Memuat provider...</div>
        <div v-else-if="providers.length === 0" class="empty-state">
          Belum ada provider tersimpan. Tambahkan Sumopod, 9router, OpenRouter, atau API kompatibel OpenAI lain.
        </div>

        <button
          v-for="provider in providers"
          :key="provider.provider_id"
          class="provider-item"
          :class="{ active: form.provider_id === provider.provider_id }"
          @click="editProvider(provider)"
        >
          <div>
            <strong>{{ provider.name }}</strong>
            <span>{{ provider.default_model }}</span>
          </div>
          <em v-if="provider.is_active">aktif</em>
        </button>
      </aside>

      <section class="panel form-panel">
        <div class="section-head">
          <div>
            <p class="eyebrow">Configure</p>
            <h2>{{ isEditing ? 'Edit Provider' : 'Tambah Provider' }}</h2>
          </div>
          <button class="secondary-button" :disabled="saving" @click="saveProvider">
            {{ saving ? 'Menyimpan...' : 'Simpan' }}
          </button>
        </div>

        <div class="form-grid">
          <label>
            Provider ID
            <input v-model="form.provider_id" placeholder="sumopod / 9router / custom-ai" />
          </label>
          <label>
            Nama Provider
            <input v-model="form.name" placeholder="Sumopod" />
          </label>
          <label class="wide">
            Base URL
            <input v-model="form.base_url" placeholder="https://ai.sumopod.com atau http://localhost:20128" />
          </label>
          <label>
            Default Model
            <input v-model="form.default_model" placeholder="deepseek-v4-flash" />
          </label>
          <label>
            Models Manual
            <input v-model="modelsText" placeholder="model-a, model-b, model-c" />
          </label>
          <label class="wide">
            API Key / Token
            <input v-model="form.api_key" type="password" placeholder="sk-... / token gateway" autocomplete="off" />
            <small>Kosongkan atau isi ******** saat edit kalau tidak mau mengganti key lama.</small>
          </label>
          <label class="wide">
            Catatan
            <textarea v-model="form.notes" rows="3" placeholder="Contoh: Provider lokal 9router untuk mode hemat." />
          </label>
        </div>

        <div class="button-row">
          <button class="primary-button" :disabled="saving" @click="saveProvider">Simpan Provider</button>
          <button class="secondary-button" :disabled="testing || !form.provider_id" @click="testCurrentProvider">
            {{ testing ? 'Testing...' : 'Test Koneksi' }}
          </button>
          <button class="secondary-button" :disabled="activating || !form.provider_id" @click="activateCurrentProvider">
            {{ activating ? 'Mengaktifkan...' : 'Jadikan Aktif' }}
          </button>
          <button v-if="isEditing" class="danger-button" :disabled="deleting" @click="deleteCurrentProvider">
            {{ deleting ? 'Menghapus...' : 'Hapus' }}
          </button>
        </div>

        <div v-if="testResult" class="test-result">
          <span>Hasil test</span>
          <pre>{{ testResult }}</pre>
        </div>
      </section>
    </section>
  </main>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import aiApi from '../api/ai'

const providers = ref([])
const activeProvider = ref(null)
const loading = ref(false)
const saving = ref(false)
const testing = ref(false)
const activating = ref(false)
const deleting = ref(false)
const error = ref('')
const successMessage = ref('')
const testResult = ref('')
const modelsText = ref('')

const blankForm = () => ({
  provider_id: '',
  name: '',
  base_url: '',
  api_key: '',
  default_model: '',
  provider_type: 'openai_compatible',
  auth_type: 'api_key',
  notes: ''
})

const form = reactive(blankForm())
const isEditing = computed(() => providers.value.some(p => p.provider_id === form.provider_id))

const resetMessages = () => {
  error.value = ''
  successMessage.value = ''
}

const applyForm = provider => {
  Object.assign(form, {
    provider_id: provider.provider_id || '',
    name: provider.name || '',
    base_url: provider.base_url || '',
    api_key: '********',
    default_model: provider.default_model || '',
    provider_type: provider.provider_type || 'openai_compatible',
    auth_type: provider.auth_type || 'api_key',
    notes: provider.notes || ''
  })
  modelsText.value = (provider.models || []).join(', ')
}

const fetchProviders = async () => {
  loading.value = true
  resetMessages()
  try {
    const res = await aiApi.getProviders()
    providers.value = res.data.providers || []
    activeProvider.value = res.data.active || null
    if (!form.provider_id && providers.value.length) {
      const active = providers.value.find(p => p.is_active) || providers.value[0]
      applyForm(active)
    }
  } catch (err) {
    error.value = err.message || 'Gagal memuat provider AI.'
  } finally {
    loading.value = false
  }
}

const newProvider = () => {
  resetMessages()
  Object.assign(form, blankForm())
  modelsText.value = ''
  testResult.value = ''
}

const editProvider = provider => {
  resetMessages()
  applyForm(provider)
  testResult.value = ''
}

const providerPayload = () => ({
  ...form,
  models: modelsText.value.split(',').map(x => x.trim()).filter(Boolean)
})

const saveProvider = async () => {
  resetMessages()
  saving.value = true
  try {
    await aiApi.saveProvider(providerPayload())
    successMessage.value = 'Provider berhasil disimpan.'
    await fetchProviders()
  } catch (err) {
    error.value = err.message || 'Gagal menyimpan provider.'
  } finally {
    saving.value = false
  }
}

const activateCurrentProvider = async () => {
  resetMessages()
  activating.value = true
  try {
    if (!isEditing.value) await aiApi.saveProvider(providerPayload())
    await aiApi.activateProvider(form.provider_id)
    successMessage.value = 'Provider aktif berhasil diganti.'
    await fetchProviders()
  } catch (err) {
    error.value = err.message || 'Gagal mengaktifkan provider.'
  } finally {
    activating.value = false
  }
}

const testCurrentProvider = async () => {
  resetMessages()
  testing.value = true
  testResult.value = ''
  try {
    const payload = isEditing.value
      ? { provider_id: form.provider_id, max_tokens: 128 }
      : { ...providerPayload(), max_tokens: 128 }
    const res = await aiApi.testProvider(payload)
    testResult.value = JSON.stringify(res.data, null, 2)
    successMessage.value = 'Koneksi provider berhasil dites.'
  } catch (err) {
    error.value = err.message || 'Test koneksi gagal.'
  } finally {
    testing.value = false
  }
}

const deleteCurrentProvider = async () => {
  if (!window.confirm(`Hapus provider ${form.provider_id}?`)) return
  resetMessages()
  deleting.value = true
  try {
    await aiApi.deleteProvider(form.provider_id)
    successMessage.value = 'Provider berhasil dihapus.'
    newProvider()
    await fetchProviders()
  } catch (err) {
    error.value = err.message || 'Gagal menghapus provider.'
  } finally {
    deleting.value = false
  }
}

onMounted(fetchProviders)
</script>

<style scoped>
.ai-settings-page {
  min-height: 100vh;
  padding: 32px;
  color: #eef4ff;
  background:
    radial-gradient(circle at top left, rgba(92, 225, 255, 0.18), transparent 34%),
    radial-gradient(circle at top right, rgba(200, 169, 106, 0.12), transparent 30%),
    #05070d;
}

.hero-panel,
.panel,
.status-card,
.notice {
  border: 1px solid rgba(255, 255, 255, 0.1);
  background: rgba(9, 14, 27, 0.78);
  box-shadow: 0 24px 80px rgba(0, 0, 0, 0.32);
  backdrop-filter: blur(18px);
}

.hero-panel {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 24px;
  padding: 28px;
  border-radius: 28px;
}

.eyebrow {
  margin-bottom: 10px;
  color: #68e1fd;
  font-size: 12px;
  letter-spacing: 0.16em;
  text-transform: uppercase;
}

h1,
h2 {
  margin: 0;
  letter-spacing: -0.04em;
}

h1 {
  font-size: clamp(36px, 6vw, 72px);
}

h2 {
  font-size: 24px;
}

.hero-copy {
  max-width: 760px;
  margin-top: 14px;
  color: #9da8bd;
  line-height: 1.7;
}

.ghost-link {
  color: #c8a96a;
  text-decoration: none;
  white-space: nowrap;
}

.status-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 16px;
  margin: 18px 0;
}

.status-card {
  min-height: 150px;
  padding: 20px;
  border-radius: 22px;
}

.status-card.primary {
  border-color: rgba(104, 225, 253, 0.34);
}

.status-card span,
.test-result span {
  display: block;
  margin-bottom: 12px;
  color: #8e9aaf;
  font-size: 12px;
  letter-spacing: 0.12em;
  text-transform: uppercase;
}

.status-card strong {
  display: block;
  margin-bottom: 10px;
  font-size: 22px;
}

.status-card p,
.empty-state,
small {
  color: #8e9aaf;
  line-height: 1.6;
}

.notice {
  margin-bottom: 18px;
  padding: 14px 18px;
  border-radius: 16px;
}

.notice.error {
  border-color: rgba(255, 92, 122, 0.4);
  color: #ff9aac;
}

.notice.success {
  border-color: rgba(124, 255, 178, 0.35);
  color: #9dffc6;
}

.content-grid {
  display: grid;
  grid-template-columns: 360px 1fr;
  gap: 18px;
}

.panel {
  padding: 22px;
  border-radius: 26px;
}

.section-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 20px;
}

.provider-list {
  align-self: start;
}

.provider-item {
  width: 100%;
  display: flex;
  justify-content: space-between;
  gap: 14px;
  padding: 16px;
  margin-bottom: 10px;
  color: #eef4ff;
  text-align: left;
  border: 1px solid rgba(255, 255, 255, 0.09);
  border-radius: 18px;
  background: rgba(255, 255, 255, 0.035);
  cursor: pointer;
}

.provider-item.active,
.provider-item:hover {
  border-color: rgba(104, 225, 253, 0.45);
  background: rgba(104, 225, 253, 0.07);
}

.provider-item span {
  display: block;
  margin-top: 6px;
  color: #8e9aaf;
  font-size: 13px;
}

.provider-item em {
  color: #7cffb2;
  font-size: 12px;
  font-style: normal;
  text-transform: uppercase;
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 16px;
}

label {
  display: grid;
  gap: 8px;
  color: #dbe7ff;
  font-size: 13px;
}

label.wide {
  grid-column: 1 / -1;
}

input,
textarea {
  width: 100%;
  color: #eef4ff;
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 16px;
  background: rgba(255, 255, 255, 0.055);
  padding: 13px 14px;
  outline: none;
}

input:focus,
textarea:focus {
  border-color: rgba(104, 225, 253, 0.55);
  box-shadow: 0 0 0 4px rgba(104, 225, 253, 0.08);
}

.button-row {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-top: 20px;
}

button,
.primary-button,
.secondary-button,
.danger-button {
  border: 0;
  border-radius: 999px;
  padding: 12px 18px;
  font-weight: 700;
  cursor: pointer;
}

button:disabled {
  opacity: 0.55;
  cursor: not-allowed;
}

.primary-button {
  color: #041018;
  background: linear-gradient(135deg, #68e1fd, #c8a96a);
}

.secondary-button {
  color: #eef4ff;
  border: 1px solid rgba(255, 255, 255, 0.14);
  background: rgba(255, 255, 255, 0.075);
}

.danger-button {
  color: #fff;
  background: rgba(255, 92, 122, 0.18);
  border: 1px solid rgba(255, 92, 122, 0.35);
}

.test-result {
  margin-top: 20px;
  padding: 16px;
  border-radius: 18px;
  background: rgba(0, 0, 0, 0.22);
  border: 1px solid rgba(255, 255, 255, 0.08);
}

pre {
  overflow-x: auto;
  white-space: pre-wrap;
  color: #b8f7ff;
  line-height: 1.55;
}

@media (max-width: 980px) {
  .ai-settings-page {
    padding: 18px;
  }

  .hero-panel,
  .content-grid,
  .status-grid {
    grid-template-columns: 1fr;
  }

  .hero-panel {
    display: grid;
  }

  .form-grid {
    grid-template-columns: 1fr;
  }
}
</style>
