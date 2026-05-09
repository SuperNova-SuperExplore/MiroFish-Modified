<template>
  <div class="home-container">
    <div v-if="selectedMode" class="selected-mode-ribbon">
      <span>Mode aktif</span>
      <strong>{{ selectedMode.label || selectedMode.name }}</strong>
      <em>{{ selectedMode.description }}</em>
      <button @click="clearSelectedMode">×</button>
    </div>
    <!-- Catatan UI -->
    <nav class="navbar">
      <div class="nav-brand">MIROFISH</div>
      <div class="nav-links">
        <router-link to="/operations" class="github-link system-link">
          Riwayat <span class="arrow">◇</span>
        </router-link>
        <router-link to="/ai-settings" class="github-link system-link">
          AI Settings <span class="arrow">⚙</span>
        </router-link>
        <a href="https://github.com/SuperNova-SuperExplore/MiroFish-Modified" target="_blank" class="github-link">
          Buka GitHub <span class="arrow">↗</span>
        </a>
      </div>
    </nav>

    <div class="main-content">
      <!-- Catatan UI -->
      <section class="hero-section">
        <div class="hero-left">
          <div class="tag-row">
            <span class="orange-tag">Mesin simulasi kolektif yang ringkas</span>
            <span class="version-text">/ v0.1 pratinjau</span>
          </div>

          <h1 class="main-title">
            Unggah bahan mentah<br>
            <span class="gradient-text">simulasikan skenario</span>
          </h1>

          <div class="hero-desc">
            <p>
              Bahkan dari satu paragraf, <span class="highlight-bold">MiroFish</span>  dapat membaca benih realitas di dalamnya dan membangun dunia paralel berisi hingga <span class="highlight-orange">jutaan agent</span>. Dari sudut pandang strategis, lo bisa menyuntikkan variabel baru dan mencari <span class="highlight-code">“keputusan paling masuk akal”</span>
            </p>
            <p class="slogan-text">
              Latih keputusan sebelum dunia nyata bergerak<span class="blinking-cursor">_</span>
            </p>
          </div>

          <div class="decoration-square"></div>
        </div>

        <div class="hero-right">
          <!-- Catatan UI -->
          <div class="logo-container">
            <img src="../assets/logo/MiroFish_logo_left.jpeg" alt="MiroFish Logo" class="hero-logo" />
          </div>

          <button class="scroll-down-btn" @click="scrollToBottom">
            ↓
          </button>
        </div>
      </section>

      <section class="command-center-section">
        <div class="command-header">
          <div>
            <div class="panel-header"><span class="status-dot">■</span> Command Center</div>
            <h2 class="section-title">Pilih mode operasi</h2>
            <p class="section-desc">
              Mulai dari simulasi sosial penuh, prediksi project, pertanyaan spesifik, sampai blueprint design dan audit.
            </p>
          </div>
          <router-link to="/ai-settings" class="settings-card-link">
            <span>System Core</span>
            <strong>AI Settings</strong>
            <em>Atur provider & model →</em>
          </router-link>
        </div>

        <div v-if="modesLoading" class="mode-loading">Memuat mode operasi...</div>
        <div v-else class="mode-grid">
          <button
            v-for="mode in modeCards"
            :key="mode.id"
            class="mode-card"
            :class="`mode-${mode.id}`"
            @click="handleModeClick(mode)"
          >
            <div class="mode-topline">
              <span>{{ mode.category || 'mode' }}</span>
              <em>{{ mode.status || 'ready' }}</em>
            </div>
            <h3>{{ mode.label || mode.name }}</h3>
            <p>{{ mode.description }}</p>
            <div class="mode-badges">
              <span v-for="badge in mode.badges || []" :key="badge">{{ badge }}</span>
            </div>
            <div v-if="mode.best_for?.length" class="mode-best-for">
              <strong>Cocok untuk</strong>
              <ul>
                <li v-for="item in mode.best_for.slice(0, 3)" :key="item">{{ item }}</li>
              </ul>
            </div>
            <div class="mode-cta">{{ mode.cta || 'Buka mode' }} <span>→</span></div>
          </button>
        </div>
        <div v-if="modesError" class="mode-error">{{ modesError }}</div>
      </section>

      <!-- Catatan UI -->
      <section ref="fullPredictSection" class="dashboard-section">
        <!-- Catatan UI -->
        <div class="left-panel">
          <div class="panel-header">
            <span class="status-dot">■</span> Status sistem
          </div>

          <h2 class="section-title">Siap dipakai</h2>
          <p class="section-desc">
            Mesin prediksi siaga. Unggah dokumen bebas untuk memulai rangkaian simulasi.
          </p>

          <!-- Catatan UI -->
          <div class="metrics-row">
            <div class="metric-card">
              <div class="metric-value">Hemat biaya</div>
              <div class="metric-label">Simulasi umum ±$5/sesi</div>
            </div>
            <div class="metric-card">
              <div class="metric-value">Skala tinggi</div>
              <div class="metric-label">Mendukung simulasi agent masif</div>
            </div>
          </div>

          <!-- Catatan UI -->
          <div class="steps-container">
            <div class="steps-header">
               <span class="diamond-icon">◇</span> Alur kerja
            </div>
            <div class="workflow-list">
              <div class="workflow-item">
                <span class="step-num">01</span>
                <div class="step-info">
                  <div class="step-title">Bangun graf</div>
                  <div class="step-desc">Ekstraksi benih realitas, injeksi memori, dan GraphRAG</div>
                </div>
              </div>
              <div class="workflow-item">
                <span class="step-num">02</span>
                <div class="step-info">
                  <div class="step-title">Rancang simulasi</div>
                  <div class="step-desc">Full Predict memakai persona simulasi; Blueprint Lab memakai panel evaluator native</div>
                </div>
              </div>
              <div class="workflow-item">
                <span class="step-num">03</span>
                <div class="step-info">
                  <div class="step-title">Mulai simulasi</div>
                  <div class="step-desc">Simulasi paralel, parsing kebutuhan, dan update memori temporal</div>
                </div>
              </div>
              <div class="workflow-item">
                <span class="step-num">04</span>
                <div class="step-info">
                  <div class="step-title">Buat laporan</div>
                  <div class="step-desc">Full Predict memakai ReportAgent; Blueprint Lab memakai artifact native tanpa klaim tool palsu</div>
                </div>
              </div>
              <div class="workflow-item">
                <span class="step-num">05</span>
                <div class="step-info">
                  <div class="step-title">Interaksi lanjut</div>
                  <div class="step-desc">Tanya, audit, dan edit laporan dengan AI yang grounded ke dokumen/artifact</div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Catatan UI -->
        <div class="right-panel">
          <div class="console-box">
            <div v-if="selectedMode?.id === 'blueprint_lab'" class="blueprint-intake console-section">
              <div class="console-header">
                <span class="console-label">Blueprint Lab / Titik awal</span>
              </div>
              <div class="blueprint-options">
                <button
                  v-for="option in blueprintOptions"
                  :key="option.id"
                  class="blueprint-option"
                  :class="{ active: blueprintStartMode === option.id }"
                  @click="selectBlueprintStart(option.id)"
                >
                  <strong>{{ option.title }}</strong>
                  <span>{{ option.desc }}</span>
                </button>
              </div>

              <div v-if="blueprintStartMode === 'from_zero'" class="blueprint-idea-box">
                <textarea
                  v-model="blueprintIdea"
                  class="code-input blueprint-textarea"
                  rows="6"
                  placeholder="Apa yang ingin lo buat? Contoh: Gue mau bikin platform AI untuk bantu founder memprediksi risiko project dan audit blueprint bisnis."
                  :disabled="blueprintGenerating"
                ></textarea>
                <div class="blueprint-meta-grid">
                  <input v-model="blueprintTargetUser" class="topic-input" placeholder="Target user (opsional)" :disabled="blueprintGenerating" />
                  <input v-model="blueprintConstraints" class="topic-input" placeholder="Constraint/budget/deadline (opsional)" :disabled="blueprintGenerating" />
                </div>
                <div class="instruction-import-box">
                  <div>
                    <strong>Personality / Identity / Instruction AI</strong>
                    <span>Opsional. Upload .md/.txt biar AI menjabarkan blueprint sesuai gaya, prinsip, atau instruksi lo.</span>
                  </div>
                  <input
                    ref="blueprintInstructionInput"
                    type="file"
                    accept=".md,.txt,.markdown"
                    style="display:none"
                    @change="handleBlueprintInstructionFile"
                  />
                  <button class="toggle-btn instruction-btn" type="button" @click="blueprintInstructionInput?.click()" :disabled="blueprintGenerating">
                    Import .md/.txt
                  </button>
                </div>
                <div v-if="blueprintInstructionName" class="instruction-preview">
                  <span>✓ {{ blueprintInstructionName }}</span>
                  <button @click="clearBlueprintInstruction">hapus</button>
                </div>
                <textarea
                  v-if="blueprintInstructionText"
                  v-model="blueprintInstructionText"
                  class="code-input blueprint-textarea instruction-textarea"
                  rows="4"
                  placeholder="Instruction text"
                  :disabled="blueprintGenerating"
                ></textarea>
                <button class="generate-btn blueprint-generate" @click="handleGenerateBlueprintSeed" :disabled="!blueprintIdea.trim() || blueprintGenerating">
                  <span v-if="!blueprintGenerating">Jabarkan ide jadi blueprint awal</span>
                  <span v-else>Menjabarkan blueprint...</span>
                </button>
                <div class="seed-hint">AI akan membuat blueprint awal sebagai file seed .md, lalu tetap masuk pipeline MiroFish original.</div>
                <div v-if="blueprintStatus" class="blueprint-status" :class="{ error: blueprintStatusType === 'error', success: blueprintStatusType === 'success' }">
                  {{ blueprintStatus }}
                </div>
                <div v-if="blueprintPreview" class="blueprint-preview-card">
                  <div class="preview-kicker">Preview blueprint awal</div>
                  <strong>{{ blueprintPreview.title }}</strong>
                  <p>{{ blueprintPreview.summary }}</p>
                  <div v-if="blueprintPreview.features?.length" class="preview-tags">
                    <span v-for="feature in blueprintPreview.features" :key="feature">{{ feature }}</span>
                  </div>
                </div>
              </div>

              <div v-else-if="blueprintStartMode === 'audit_blueprint'" class="audit-mode-row">
                <span>Mode audit</span>
                <select v-model="blueprintAuditMode" class="audit-select">
                  <option value="balanced">Balanced</option>
                  <option value="technical">Teknis</option>
                  <option value="business">Bisnis</option>
                  <option value="risk">Risiko</option>
                  <option value="brutal">Brutal / Red Team</option>
                  <option value="investor">Investor</option>
                  <option value="ux">UX</option>
                </select>
              </div>
            </div>

            <!-- Catatan UI -->
            <div class="console-section">
              <div class="console-header">
                <span class="console-label">01 / Benih realitas</span>
                <div class="mode-toggle" v-if="selectedMode?.id !== 'blueprint_lab' || blueprintStartMode !== 'from_zero'">
                  <button
                    class="toggle-btn"
                    :class="{ active: seedMode === 'upload' }"
                    @click="seedMode = 'upload'"
                    :disabled="seedGenerating"
                  >Unggah manual</button>
                  <button
                    class="toggle-btn"
                    :class="{ active: seedMode === 'auto' }"
                    @click="seedMode = 'auto'"
                    :disabled="seedGenerating"
                  >Buat dengan AI</button>
                </div>
              </div>

              <!-- Manual upload mode -->
              <div v-if="seedMode === 'upload'">
                <div
                  class="upload-zone"
                  :class="{ 'drag-over': isDragOver, 'has-files': files.length > 0 }"
                  @dragover.prevent="handleDragOver"
                  @dragleave.prevent="handleDragLeave"
                  @drop.prevent="handleDrop"
                  @click="triggerFileInput"
                >
                  <input
                    ref="fileInput"
                    type="file"
                    multiple
                    accept=".pdf,.md,.txt"
                    @change="handleFileSelect"
                    style="display: none"
                    :disabled="loading"
                  />

                  <div v-if="files.length === 0" class="upload-placeholder">
                    <div class="upload-icon">↑</div>
                    <div class="upload-title">Tarik file ke sini</div>
                    <div class="upload-hint">atau klik untuk memilih file</div>
                  </div>

                  <div v-else class="file-list">
                    <div v-for="(file, index) in files" :key="index" class="file-item">
                      <span class="file-icon">📄</span>
                      <span class="file-name">{{ file.name }}</span>
                      <button @click.stop="removeFile(index)" class="remove-btn">×</button>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Auto generate mode -->
              <div v-else class="auto-seed-section">
                <div class="seed-topic-input">
                  <input
                    v-model="seedTopic"
                    type="text"
                    class="topic-input"
                    placeholder="Masukkan topik, contoh: AI Wars 2026 atau dampak kerja jarak jauh"
                    :disabled="seedGenerating"
                    @keyup.enter="handleGenerateSeed"
                  />
                  <button
                    class="generate-btn"
                    @click="handleGenerateSeed"
                    :disabled="!seedTopic.trim() || seedGenerating"
                  >
                    <span v-if="!seedGenerating">Riset & buat</span>
                    <span v-else class="gen-loading">Sedang dibuat...</span>
                  </button>
                </div>
                <div class="seed-hint">AI akan merangkum riset menjadi 5 dokumen seed multi-sudut.</div>

                <!-- Progress -->
                <div v-if="seedGenerating" class="seed-progress">
                  <div class="progress-bar-track">
                    <div class="progress-bar-fill" :style="{ width: seedProgress + '%' }"></div>
                  </div>
                  <div class="progress-text">{{ seedMessage }}</div>
                </div>

                <!-- Generated files -->
                <div v-if="files.length > 0 && !seedGenerating" class="file-list">
                  <div class="seed-success">✓ Berhasil dibuat {{ files.length }} dokumen seed</div>
                  <div v-for="(file, index) in files" :key="index" class="file-item">
                    <span class="file-icon">📄</span>
                    <span class="file-name">{{ file.name }}</span>
                    <button @click.stop="removeFile(index)" class="remove-btn">×</button>
                  </div>
                </div>
              </div>

              <div v-if="selectedMode?.id === 'blueprint_lab' && blueprintStartMode !== 'from_zero'" class="paste-blueprint-box">
                <textarea
                  v-model="blueprintPasteText"
                  class="code-input blueprint-textarea"
                  rows="5"
                  placeholder="Opsional: paste blueprint/PRD/rancangan di sini kalau tidak ingin upload file."
                ></textarea>
                <button class="generate-btn blueprint-generate" @click="addPastedBlueprintFile" :disabled="!blueprintPasteText.trim()">
                  Jadikan paste sebagai file blueprint
                </button>
              </div>
            </div>

            <!-- Catatan UI -->
            <div class="console-divider">
              <span>Parameter</span>
            </div>

            <!-- Catatan UI -->
            <div class="console-section">
              <div class="console-header">
                <span class="console-label">>_ 02 / {{ selectedMode?.id === 'blueprint_lab' ? 'Prompt blueprint' : 'Prompt simulasi' }}</span>
              </div>
              <div class="input-wrapper">
                <textarea
                  v-model="formData.simulationRequirement"
                  class="code-input"
                  :placeholder="selectedMode?.id === 'blueprint_lab' ? '// Tulis arahan blueprint, batasan, atau fokus evaluasi' : '// Tulis kebutuhan simulasi atau prediksi dalam bahasa natural'"
                  rows="6"
                  :disabled="loading"
                ></textarea>
                <div class="model-badge">Engine: MiroFish-V1.0</div>
              </div>
            </div>

            <!-- Catatan UI -->
            <div class="console-section btn-section">
              <button
                class="start-engine-btn"
                @click="startSimulation"
                :disabled="!canSubmit || loading"
              >
                <span v-if="!loading">Mulai engine</span>
                <span v-else>Menyiapkan...</span>
                <span class="btn-arrow">→</span>
              </button>
            </div>
          </div>
        </div>
      </section>

      <!-- Database riwayat -->
      <HistoryDatabase />
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import HistoryDatabase from '../components/HistoryDatabase.vue'
import { generateSeed } from '../api/graph'
import strategicApi from '../api/strategic'

const router = useRouter()

const modes = ref([])
const modesLoading = ref(false)
const modesError = ref('')
const fullPredictSection = ref(null)

const fallbackModes = [
  {
    id: 'full_predict',
    label: 'Prediksi Penuh',
    name: 'Full Predict',
    category: 'simulation',
    status: 'existing_pipeline',
    cta: 'Jalankan Simulasi Penuh',
    badges: ['Dalam', 'Multi-agent', 'Sosial'],
    description: 'Mode lengkap MiroFish untuk isu sosial luas: graph, persona, simulasi, interview, dan laporan.',
    best_for: ['Isu sosial luas dengan banyak aktor', 'Reaksi publik atau komunitas', 'Konflik, backlash, dan narasi dominan']
  },
  {
    id: 'project_prediction',
    label: 'Prediksi Project',
    category: 'focused_prediction',
    status: 'ready',
    cta: 'Analisis Project',
    badges: ['Fokus', 'Strategis', 'Roadmap'],
    description: 'Analisis peluang, risiko, bottleneck, dan roadmap dari project atau keputusan besar.',
    best_for: ['Project, bisnis, produk, atau keputusan besar', 'Risiko dan bottleneck', 'Roadmap 7/30/90 hari']
  },
  {
    id: 'question_prediction',
    label: 'Prediksi Pertanyaan',
    category: 'focused_prediction',
    status: 'ready',
    cta: 'Tanya Prediksi',
    badges: ['Cepat', 'Ringkas', 'Decision Support'],
    description: 'Ajukan satu pertanyaan spesifik dan dapatkan prediksi langsung, confidence, dan next action.',
    best_for: ['Satu pertanyaan spesifik', 'Membandingkan pilihan', 'Next best action cepat']
  },
  {
    id: 'blueprint_lab',
    label: 'Blueprint Lab',
    category: 'blueprint',
    status: 'ready',
    cta: 'Masuk Blueprint Lab',
    badges: ['Rancang', 'Audit', 'Revisi'],
    description: 'Rancang project dari nol, audit blueprint, lalu revisi berdasarkan kritik sistem.',
    best_for: ['Merancang produk/sistem/bisnis', 'Mengaudit blueprint', 'Revisi terarah']
  }
]

const modeCards = computed(() => modes.value.length ? modes.value : fallbackModes)

const loadModes = async () => {
  modesLoading.value = true
  modesError.value = ''
  try {
    const res = await strategicApi.getModes()
    modes.value = res.data || []
  } catch (err) {
    modesError.value = 'Gagal memuat mode dari backend. Mode fallback tetap tersedia.'
    modes.value = fallbackModes
  } finally {
    modesLoading.value = false
  }
}

const handleModeClick = (mode) => {
  if (mode.id === 'full_predict') {
    fullPredictSection.value?.scrollIntoView({ behavior: 'smooth', block: 'start' })
    return
  }
  selectOperationMode(mode)
}

const selectedMode = ref(null)

const modePromptMap = {
  project_prediction: 'Mode: Prediksi Project\n\nTujuan: Analisis peluang, risiko, bottleneck, skenario, dan roadmap dari project berikut.\n\nBrief project:\n',
  question_prediction: 'Mode: Prediksi Pertanyaan\n\nPertanyaan strategis yang ingin diprediksi:\n',
  blueprint_lab: 'Mode: Blueprint Lab\n\nTugas:\nGunakan blueprint sebagai rancangan utama. Pahami isi blueprint, petakan hubungan penting, lalu jalankan evaluasi Blueprint Lab native. Fokus pada tujuan, target user, fitur utama, alur penggunaan, kebutuhan teknis, risiko, asumsi, scope MVP, prioritas revisi, roadmap eksekusi, dan blueprint versi revisi bila diperlukan.\n\nBrief blueprint/project:\n'
}

const selectOperationMode = (mode) => {
  selectedMode.value = mode
  const prefix = modePromptMap[mode.id] || `Mode: ${mode.label || mode.name}\n\nBrief:\n`
  if (mode.id === 'blueprint_lab') {
    selectBlueprintStart(blueprintStartMode.value)
  } else if (!formData.value.simulationRequirement.trim() || formData.value.simulationRequirement.startsWith('Mode:')) {
    formData.value.simulationRequirement = prefix
  }
  fullPredictSection.value?.scrollIntoView({ behavior: 'smooth', block: 'start' })
}

const clearSelectedMode = () => {
  selectedMode.value = null
}

const selectBlueprintStart = (mode) => {
  blueprintStartMode.value = mode
  files.value = []
  blueprintPasteText.value = ''
  blueprintStatus.value = ''
  blueprintStatusType.value = ''
  blueprintPreview.value = null
  if (mode === 'from_zero') {
    seedMode.value = 'upload'
    formData.value.simulationRequirement = 'Mode: Blueprint Lab — Mulai dari Nol\n\nTugas:\nJabarkan ide mentah menjadi blueprint awal, pahami tujuan, target user, fitur utama, alur penggunaan, kebutuhan teknis, risiko, asumsi, dan dependency. Setelah blueprint_seed.md tersedia, jalankan evaluasi Blueprint Lab native untuk menghasilkan readiness score, risiko utama, scope MVP, prioritas revisi, roadmap eksekusi, dan blueprint versi revisi bila diperlukan.\n\nIde yang ingin dibuat:\n'
  } else if (mode === 'has_blueprint') {
    seedMode.value = 'upload'
    formData.value.simulationRequirement = 'Mode: Blueprint Lab — Punya Blueprint\n\nTugas:\nGunakan file/paste blueprint sebagai rancangan utama. Pahami isi blueprint, petakan hubungan penting, lalu jalankan evaluasi Blueprint Lab native. Fokus pada kelayakan, risiko, asumsi, dependency, scope MVP, prioritas revisi, roadmap eksekusi, dan blueprint versi revisi bila diperlukan.\n'
  } else if (mode === 'audit_blueprint') {
    seedMode.value = 'upload'
    formData.value.simulationRequirement = `Mode: Blueprint Lab — Audit Blueprint\n\nTugas:\nAudit blueprint dengan pendekatan ${blueprintAuditMode.value}. Gunakan evaluasi Blueprint Lab native untuk mencari kelemahan kritis, asumsi tersembunyi, risiko eksekusi, dependency yang belum jelas, overengineering, scope MVP yang perlu dipangkas, dan rekomendasi revisi prioritas. Hasil akhir harus berupa laporan evaluasi dan blueprint versi revisi bila diperlukan.\n`
  }
}

const objectToMarkdown = (title, data, level = 1) => {
  const heading = '#'.repeat(Math.min(level, 5))
  if (data === null || data === undefined) return `${heading} ${title}\n-\n`
  if (typeof data !== 'object') return `${heading} ${title}\n${data}\n`
  if (Array.isArray(data)) {
    const body = data.map(item => typeof item === 'object' ? `- ${JSON.stringify(item, null, 2)}` : `- ${item}`).join('\n')
    return `${heading} ${title}\n${body}\n`
  }
  let out = `${heading} ${title}\n`
  for (const [key, value] of Object.entries(data)) {
    out += '\n' + objectToMarkdown(key.replaceAll('_', ' '), value, level + 1)
  }
  return out
}

const handleBlueprintInstructionFile = async (event) => {
  const file = event.target.files?.[0]
  if (!file) return
  const ext = file.name.split('.').pop().toLowerCase()
  if (!['md', 'txt', 'markdown'].includes(ext)) {
    seedMessage.value = 'Instruction hanya support .md/.txt'
    return
  }
  blueprintInstructionName.value = file.name
  blueprintInstructionText.value = await file.text()
  event.target.value = ''
}

const clearBlueprintInstruction = () => {
  blueprintInstructionText.value = ''
  blueprintInstructionName.value = ''
}

const handleGenerateBlueprintSeed = async () => {
  if (!blueprintIdea.value.trim() || blueprintGenerating.value) return
  blueprintGenerating.value = true
  blueprintStatus.value = 'AI sedang menjabarkan ide menjadi blueprint awal...'
  blueprintStatusType.value = ''
  blueprintPreview.value = null
  seedMessage.value = 'Menjabarkan ide menjadi blueprint awal...'
  try {
    const instructionBlock = blueprintInstructionText.value.trim()
      ? `\n\nPERSONALITY / IDENTITY / INSTRUCTION UNTUK AI:\n${blueprintInstructionText.value.trim()}\n`
      : ''
    const res = await strategicApi.designBlueprint({
      brief: `${blueprintIdea.value}${instructionBlock}`,
      blueprint_type: 'project',
      target_user: blueprintTargetUser.value,
      constraints: blueprintConstraints.value,
      output_focus: ['roadmap', 'architecture', 'risk', 'mvp'],
      tags: ['blueprint-lab', 'from-zero']
    })
    const instructionMarkdown = instructionBlock ? `\n\n# AI Personality / Identity / Instruction\n\n${blueprintInstructionText.value.trim()}\n` : ''
    const output = res.data?.data || res.data || {}
    const markdown = `${instructionMarkdown}\n${objectToMarkdown('Blueprint Awal dari Ide', output)}`
    const blob = new Blob([markdown], { type: 'text/markdown' })
    files.value = [new File([blob], 'blueprint_seed.md', { type: 'text/markdown' })]
    blueprintPreview.value = {
      title: output.title || 'Blueprint awal berhasil dibuat',
      summary: output.executive_summary || output.solution_concept || 'Blueprint sudah disiapkan sebagai file seed.',
      features: (output.core_features || []).slice(0, 4).map(item => item.name || item.purpose || String(item))
    }
    formData.value.simulationRequirement = `Mode: Blueprint Lab — Mulai dari Nol\n\nIde awal user:\n${blueprintIdea.value}\n\n${blueprintInstructionText.value.trim() ? 'Instruksi/personality AI terlampir di blueprint_seed.md. Ikuti gaya, prinsip, batasan, dan identitas yang diberikan saat evaluasi blueprint dan penyusunan laporan.\n\n' : ''}Tugas:\nGunakan blueprint_seed.md sebagai rancangan awal. Pahami isi blueprint, petakan hubungan penting, lalu jalankan evaluasi Blueprint Lab native. Fokus pada tujuan, target user, fitur utama, alur penggunaan, kebutuhan teknis, risiko, asumsi, scope MVP, prioritas revisi, roadmap eksekusi, dan blueprint versi revisi bila diperlukan.\n`
    seedMessage.value = 'Blueprint awal berhasil dibuat sebagai blueprint_seed.md'
    blueprintStatus.value = '✓ Blueprint awal berhasil dibuat. File blueprint_seed.md sudah siap di Benih realitas.'
    blueprintStatusType.value = 'success'
  } catch (err) {
    seedMessage.value = 'Error: ' + (err.message || 'Gagal membuat blueprint')
    blueprintStatus.value = 'Gagal membuat blueprint: ' + (err.response?.data?.error || err.message || 'error tidak diketahui')
    blueprintStatusType.value = 'error'
  } finally {
    blueprintGenerating.value = false
  }
}

const addPastedBlueprintFile = () => {
  if (!blueprintPasteText.value.trim()) return
  const prefix = blueprintStartMode.value === 'audit_blueprint'
    ? `# Blueprint untuk Audit\n\nMode audit: ${blueprintAuditMode.value}\n\n`
    : '# Blueprint User\n\n'
  const blob = new Blob([prefix + blueprintPasteText.value], { type: 'text/markdown' })
  files.value = [new File([blob], 'blueprint_user_input.md', { type: 'text/markdown' })]
}

onMounted(loadModes)

// Catatan internal
const formData = ref({
  simulationRequirement: ''
})

// Catatan internal
const files = ref([])

// Catatan internal
const loading = ref(false)
const error = ref('')
const isDragOver = ref(false)

// Seed generator state
const seedMode = ref('upload')  // 'upload' or 'auto'
const seedTopic = ref('')
const seedGenerating = ref(false)
const seedProgress = ref(0)
const seedMessage = ref('')

const blueprintOptions = [
  { id: 'from_zero', title: 'Mulai dari Nol', desc: 'Belum punya blueprint. Mulai dari ide mentah dan biarkan AI menjabarkan draft awal.' },
  { id: 'has_blueprint', title: 'Punya Blueprint', desc: 'Sudah punya dokumen, PRD, proposal, roadmap, atau catatan rancangan.' },
  { id: 'audit_blueprint', title: 'Audit Blueprint', desc: 'Uji rancangan secara kritis: risiko, asumsi lemah, overengineering, dan blind spot.' }
]
const blueprintStartMode = ref('from_zero')
const blueprintIdea = ref('')
const blueprintTargetUser = ref('')
const blueprintConstraints = ref('')
const blueprintAuditMode = ref('balanced')
const blueprintPasteText = ref('')
const blueprintGenerating = ref(false)
const blueprintInstructionInput = ref(null)
const blueprintInstructionText = ref('')
const blueprintInstructionName = ref('')
const blueprintStatus = ref('')
const blueprintStatusType = ref('')
const blueprintPreview = ref(null)

// Catatan internal
const fileInput = ref(null)

// Catatan internal
const canSubmit = computed(() => {
  return formData.value.simulationRequirement.trim() !== '' && files.value.length > 0
})

// Auto seed generation
const handleGenerateSeed = async () => {
  if (!seedTopic.value.trim() || seedGenerating.value) return

  seedGenerating.value = true
  seedProgress.value = 5
  seedMessage.value = 'Initializing search...'
  files.value = []

  // Start a fake progress animation while waiting
  const progressInterval = setInterval(() => {
    if (seedProgress.value < 90) {
      seedProgress.value += Math.random() * 3
      const steps = [
        'Generating search queries...',
        'Searching web via Tavily...',
        'Collecting sources...',
        'Compiling Background...',
        'Compiling Key Actors...',
        'Compiling Data & Evidence...',
        'Compiling Public Sentiment...',
        'Compiling Scenarios...',
        'Finalizing seed documents...'
      ]
      const idx = Math.min(Math.floor(seedProgress.value / 11), steps.length - 1)
      seedMessage.value = steps[idx]
    }
  }, 2000)

  try {
    const res = await generateSeed({
      topic: seedTopic.value,
      lang: 'id',
      num_queries: 8
    })

    clearInterval(progressInterval)

    if (res.success && res.data?.seeds) {
      // Convert seed content to File objects
      const seedFiles = res.data.seeds.map((seed, i) => {
        const filename = `${String(i + 1).padStart(2, '0')}_${seed.id}.md`
        const blob = new Blob([seed.content], { type: 'text/markdown' })
        return new File([blob], filename, { type: 'text/markdown' })
      })

      files.value = seedFiles
      seedProgress.value = 100
      seedMessage.value = `Done! ${res.data.sources_count} sources → ${seedFiles.length} seed files (${(res.data.total_chars / 1000).toFixed(1)}K chars)`

      // Auto-fill simulation requirement if empty
      if (!formData.value.simulationRequirement.trim()) {
        formData.value.simulationRequirement = seedTopic.value
      }
    } else {
      seedMessage.value = 'Error: ' + (res.error || 'Unknown error')
    }
  } catch (err) {
    clearInterval(progressInterval)
    seedMessage.value = 'Error: ' + (err.message || 'Request failed')
  } finally {
    seedGenerating.value = false
  }
}

// Catatan internal
const triggerFileInput = () => {
  if (!loading.value) {
    fileInput.value?.click()
  }
}

// Catatan internal
const handleFileSelect = (event) => {
  const selectedFiles = Array.from(event.target.files)
  addFiles(selectedFiles)
}

// Catatan internal
const handleDragOver = (e) => {
  if (!loading.value) {
    isDragOver.value = true
  }
}

const handleDragLeave = (e) => {
  isDragOver.value = false
}

const handleDrop = (e) => {
  isDragOver.value = false
  if (loading.value) return

  const droppedFiles = Array.from(e.dataTransfer.files)
  addFiles(droppedFiles)
}

// Catatan internal
const addFiles = (newFiles) => {
  const validFiles = newFiles.filter(file => {
    const ext = file.name.split('.').pop().toLowerCase()
    return ['pdf', 'md', 'txt'].includes(ext)
  })
  files.value.push(...validFiles)
}

// Catatan internal
const removeFile = (index) => {
  files.value.splice(index, 1)
}

// Catatan internal
const scrollToBottom = () => {
  window.scrollTo({
    top: document.body.scrollHeight,
    behavior: 'smooth'
  })
}

// Catatan internal
const startSimulation = () => {
  if (!canSubmit.value || loading.value) return

  // Catatan internal
  import('../store/pendingUpload.js').then(({ setPendingUpload }) => {
    setPendingUpload(files.value, formData.value.simulationRequirement, selectedMode.value)

    // Catatan internal
    router.push({
      name: 'Process',
      params: { projectId: 'new' }
    })
  })
}
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Geist:wght@400;450;500;600;700;800&family=JetBrains+Mono:wght@400;500;600;700&family=Noto+Sans+SC:wght@400;500;700&display=swap');

:root {
  --ink: #111315;
  --ink-soft: #3f454d;
  --muted: #7a828c;
  --paper: #f7f4ee;
  --line: rgba(28, 33, 39, 0.11);
  --accent: #d96f32;
  --accent-dark: #9d4d25;
  --green: #6f8d71;
  --shadow: 0 34px 90px rgba(68, 57, 38, 0.13);
  --shadow-soft: 0 18px 55px rgba(68, 57, 38, 0.09);
  --font-mono: 'JetBrains Mono', ui-monospace, SFMono-Regular, monospace;
  --font-sans: 'Geist', 'Noto Sans SC', ui-sans-serif, system-ui, sans-serif;
  --ease-out: cubic-bezier(0.22, 1, 0.36, 1);
  --ease-spring: cubic-bezier(0.32, 0.72, 0, 1);
}

* { box-sizing: border-box; }

.home-container {
  min-height: 100dvh;
  position: relative;
  overflow-x: clip;
  background:
    radial-gradient(circle at 12% 8%, rgba(217,111,50,.18), transparent 31rem),
    radial-gradient(circle at 88% 18%, rgba(111,141,113,.13), transparent 28rem),
    linear-gradient(135deg, #faf7f1 0%, #eee8dc 48%, #f8f4ec 100%);
  font-family: var(--font-sans);
  color: var(--ink);
  font-feature-settings: 'ss01' 1, 'tnum' 1;
}

.home-container::before {
  content: '';
  position: fixed;
  inset: 0;
  z-index: 0;
  pointer-events: none;
  opacity: .34;
  background-image:
    linear-gradient(rgba(17,19,21,.035) 1px, transparent 1px),
    linear-gradient(90deg, rgba(17,19,21,.03) 1px, transparent 1px);
  background-size: 44px 44px;
  mask-image: radial-gradient(circle at 50% 8%, black, transparent 72%);
}

.home-container::after {
  content: '';
  position: fixed;
  inset: 0;
  z-index: 1;
  pointer-events: none;
  opacity: .038;
  background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='.85' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='256' height='256' filter='url(%23n)' opacity='.65'/%3E%3C/svg%3E");
}

.navbar, .main-content { position: relative; z-index: 2; }
.selected-mode-ribbon { position: sticky; top: 12px; z-index: 5; width: min(1120px, calc(100% - 48px)); margin: 12px auto 0; display: grid; grid-template-columns: auto auto 1fr auto; gap: 12px; align-items: center; padding: 12px 16px; color: var(--ink); border: 1px solid rgba(217,111,50,.22); border-radius: 999px; background: rgba(255,255,255,.78); box-shadow: 0 18px 50px rgba(83,67,38,.12); backdrop-filter: blur(18px); }
.selected-mode-ribbon span { font-family: var(--font-mono); color: var(--accent-dark); font-size: .72rem; text-transform: uppercase; letter-spacing: .12em; }
.selected-mode-ribbon strong { font-size: .9rem; }
.selected-mode-ribbon em { color: var(--muted); font-style: normal; font-size: .82rem; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.selected-mode-ribbon button { border: none; width: 28px; height: 28px; border-radius: 999px; background: rgba(17,19,21,.08); cursor: pointer; }

.navbar {
  width: min(1120px, calc(100% - 48px));
  height: 64px;
  margin: 24px auto 0;
  padding: 8px 10px 8px 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border: 1px solid rgba(255,255,255,.72);
  border-radius: 999px;
  background: rgba(255,255,255,.62);
  box-shadow: 0 18px 60px rgba(83,67,38,.10), inset 0 1px 0 rgba(255,255,255,.72);
  backdrop-filter: blur(22px) saturate(1.22);
}

.nav-brand {
  font-family: var(--font-mono);
  font-weight: 700;
  letter-spacing: .14em;
  font-size: .82rem;
  color: var(--ink);
  display: inline-flex;
  align-items: center;
  gap: 10px;
}

.nav-brand::before {
  content: '';
  width: 10px;
  height: 10px;
  border-radius: 999px;
  background: radial-gradient(circle, #fff 0 18%, var(--accent) 20% 100%);
  box-shadow: 0 0 0 6px rgba(217,111,50,.12), 0 0 26px rgba(217,111,50,.32);
}

.nav-links { display: flex; align-items: center; gap: 8px; }

.github-link {
  color: var(--ink);
  text-decoration: none;
  font-size: .86rem;
  font-weight: 600;
  display: inline-flex;
  align-items: center;
  gap: 10px;
  padding: 12px 14px 12px 18px;
  border-radius: 999px;
  background: rgba(17,19,21,.055);
  transition: transform .55s var(--ease-spring), background .55s var(--ease-spring), color .55s var(--ease-spring);
}

.github-link:hover { transform: translateY(-1px); background: var(--ink); color: #fff; }
.system-link { background: rgba(217,111,50,.12); color: var(--accent-dark); border: 1px solid rgba(217,111,50,.16); }
.system-link:hover { background: var(--accent); color: #fff; }

.arrow, .btn-arrow {
  display: inline-grid;
  place-items: center;
  width: 28px;
  height: 28px;
  border-radius: 999px;
  background: rgba(255,255,255,.75);
  color: var(--ink);
  font-family: var(--font-mono);
  transition: transform .55s var(--ease-spring), background .55s var(--ease-spring);
}

.github-link:hover .arrow { transform: translate(2px, -2px); }

.main-content { max-width: 1220px; margin: 0 auto; padding: 78px 28px 90px; }

.hero-section {
  display: grid;
  grid-template-columns: minmax(0, 1.05fr) minmax(330px, .72fr);
  gap: clamp(42px, 7vw, 96px);
  margin-bottom: 92px;
  align-items: center;
  min-height: calc(100dvh - 190px);
}

.hero-left { padding-right: 0; animation: riseIn .9s var(--ease-out) both; }

.tag-row { display: flex; flex-wrap: wrap; align-items: center; gap: 12px; margin-bottom: 26px; font-family: var(--font-mono); font-size: .72rem; }
.orange-tag, .version-text, .console-label, .panel-header, .steps-header, .model-badge, .seed-hint, .progress-text, .console-divider span { letter-spacing: .08em; }
.orange-tag { background: rgba(217,111,50,.13); color: var(--accent-dark); border: 1px solid rgba(217,111,50,.22); padding: 7px 12px; border-radius: 999px; font-weight: 700; box-shadow: inset 0 1px 0 rgba(255,255,255,.74); }
.version-text { color: var(--muted); font-weight: 600; }

.main-title {
  max-width: 780px;
  font-size: clamp(3.55rem, 8vw, 7.4rem);
  line-height: .88;
  font-weight: 760;
  margin: 0 0 34px;
  letter-spacing: -.07em;
  color: var(--ink);
  text-wrap: balance;
}
.gradient-text { background: linear-gradient(90deg, #171717 0%, #79573b 48%, var(--accent) 104%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; }

.hero-desc { font-size: clamp(1rem, 1.45vw, 1.13rem); line-height: 1.86; color: var(--ink-soft); max-width: 690px; margin-bottom: 42px; font-weight: 450; text-align: left; text-wrap: pretty; }
.hero-desc p { margin: 0 0 1.35rem; }
.highlight-bold { color: var(--ink); font-weight: 750; }
.highlight-orange { color: var(--accent-dark); font-weight: 750; font-family: var(--font-mono); }
.highlight-code { background: rgba(255,255,255,.62); padding: 3px 8px; border-radius: 9px; border: 1px solid var(--line); font-family: var(--font-mono); font-size: .9em; color: var(--ink); font-weight: 600; }
.slogan-text { width: fit-content; font-size: 1rem; font-weight: 650; color: var(--ink); border: 1px solid rgba(217,111,50,.18); border-left: 3px solid var(--accent); border-radius: 16px; padding: 13px 16px; background: rgba(255,255,255,.48); box-shadow: var(--shadow-soft); }
.blinking-cursor { color: var(--accent); animation: blink 1.2s step-end infinite; font-weight: 700; }
@keyframes blink { 0%,100%{opacity:1} 50%{opacity:0} }
.decoration-square { width: 64px; height: 2px; border-radius: 999px; background: linear-gradient(90deg, var(--accent), transparent); }

.hero-right { min-height: 560px; display: grid; align-items: center; justify-items: end; position: relative; animation: riseIn .9s .12s var(--ease-out) both; }
.logo-container { width: min(100%, 440px); aspect-ratio: 1 / 1; display: grid; place-items: center; padding: 14px; border-radius: 42px; background: rgba(255,255,255,.34); border: 1px solid rgba(255,255,255,.78); box-shadow: var(--shadow), inset 0 1px 0 rgba(255,255,255,.75); transform: rotate(1.5deg); }
.logo-container::before { content: ''; position: absolute; inset: 46px 18px auto auto; width: 150px; height: 150px; border-radius: 999px; background: rgba(217,111,50,.18); filter: blur(32px); z-index: -1; }
.hero-logo { max-width: 88%; width: 100%; filter: drop-shadow(0 24px 46px rgba(80,62,35,.18)); }
.scroll-down-btn { position: absolute; right: 18px; bottom: 30px; width: 52px; height: 52px; border: 1px solid rgba(255,255,255,.75); border-radius: 999px; background: rgba(255,255,255,.62); display: grid; place-items: center; cursor: pointer; color: var(--accent-dark); font-size: 1rem; box-shadow: var(--shadow-soft); transition: transform .6s var(--ease-spring), background .6s var(--ease-spring); }
.scroll-down-btn:hover { transform: translateY(4px); background: #fff; }

.command-center-section { margin-bottom: 34px; padding: clamp(22px, 3vw, 34px); border: 1px solid rgba(255,255,255,.72); border-radius: 38px; background: rgba(255,255,255,.34); box-shadow: var(--shadow); }
.command-header { display: grid; grid-template-columns: 1fr minmax(220px, 300px); gap: 22px; align-items: stretch; margin-bottom: 22px; }
.settings-card-link { display: grid; align-content: center; gap: 8px; min-height: 150px; padding: 22px; text-decoration: none; color: var(--ink); border-radius: 28px; border: 1px solid rgba(217,111,50,.18); background: rgba(255,255,255,.58); box-shadow: inset 0 1px 0 rgba(255,255,255,.78), 0 18px 50px rgba(83,67,38,.08); transition: transform .6s var(--ease-spring), background .6s var(--ease-spring); }
.settings-card-link:hover { transform: translateY(-3px); background: rgba(255,255,255,.82); }
.settings-card-link span, .mode-topline, .mode-cta { font-family: var(--font-mono); letter-spacing: .08em; text-transform: uppercase; }
.settings-card-link span { color: var(--accent-dark); font-size: .72rem; font-weight: 800; }
.settings-card-link strong { font-size: 1.55rem; letter-spacing: -.04em; }
.settings-card-link em { color: var(--muted); font-style: normal; font-size: .86rem; }
.mode-grid { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 14px; }
.mode-card { min-height: 360px; display: flex; flex-direction: column; align-items: stretch; gap: 14px; padding: 20px; color: var(--ink); text-align: left; cursor: pointer; border: 1px solid rgba(255,255,255,.72); border-radius: 28px; background: rgba(255,255,255,.56); box-shadow: inset 0 1px 0 rgba(255,255,255,.78), 0 16px 42px rgba(83,67,38,.07); transition: transform .65s var(--ease-spring), box-shadow .65s var(--ease-spring), background .65s var(--ease-spring); }
.mode-card:hover { transform: translateY(-5px); background: rgba(255,255,255,.78); box-shadow: 0 24px 70px rgba(83,67,38,.14); }
.mode-topline { display: flex; justify-content: space-between; gap: 10px; color: var(--muted); font-size: .64rem; }
.mode-topline em { color: var(--green); font-style: normal; }
.mode-card h3 { margin: 0; font-size: 1.48rem; line-height: 1.02; letter-spacing: -.055em; }
.mode-card p { margin: 0; color: var(--ink-soft); line-height: 1.62; font-size: .91rem; }
.mode-badges { display: flex; flex-wrap: wrap; gap: 7px; }
.mode-badges span { padding: 6px 9px; border-radius: 999px; background: rgba(217,111,50,.11); color: var(--accent-dark); font-size: .72rem; font-weight: 800; }
.mode-best-for { margin-top: auto; padding-top: 10px; border-top: 1px solid rgba(28,33,39,.08); }
.mode-best-for strong { display: block; margin-bottom: 8px; font-size: .78rem; color: var(--ink); }
.mode-best-for ul { margin: 0; padding-left: 16px; color: var(--muted); font-size: .78rem; line-height: 1.55; }
.mode-cta { display: flex; justify-content: space-between; align-items: center; margin-top: 4px; color: var(--ink); font-size: .72rem; font-weight: 900; }
.mode-loading, .mode-error { padding: 18px; border-radius: 20px; background: rgba(255,255,255,.52); color: var(--muted); }
.mode-error { margin-top: 12px; color: var(--accent-dark); }
.dashboard-section { display: grid; grid-template-columns: minmax(320px, .82fr) minmax(420px, 1.18fr); gap: 28px; padding: 8px; border: 1px solid rgba(255,255,255,.72); border-radius: 38px; background: rgba(255,255,255,.34); box-shadow: var(--shadow); scroll-margin-top: 28px; }
.left-panel, .right-panel { min-width: 0; display: flex; flex-direction: column; }
.left-panel { padding: clamp(24px, 3.2vw, 40px); border-radius: 31px; background: rgba(255,255,255,.52); border: 1px solid rgba(255,255,255,.7); box-shadow: inset 0 1px 0 rgba(255,255,255,.78); }
.panel-header, .steps-header, .console-header { font-family: var(--font-mono); font-size: .72rem; color: var(--muted); display: flex; align-items: center; gap: 9px; margin-bottom: 18px; }
.status-dot { color: var(--green); font-size: .72rem; text-shadow: 0 0 18px rgba(111,141,113,.55); }
.section-title { font-size: clamp(2.1rem, 4vw, 3.7rem); line-height: .98; font-weight: 750; letter-spacing: -.055em; margin: 0 0 18px; }
.section-desc { color: var(--ink-soft); margin: 0 0 28px; line-height: 1.74; max-width: 34rem; }
.metrics-row { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 12px; margin-bottom: 18px; }
.metric-card, .steps-container, .console-box, .input-wrapper, .file-item, .upload-zone, .seed-progress { border: 1px solid rgba(255,255,255,.76); background: rgba(255,255,255,.56); box-shadow: inset 0 1px 0 rgba(255,255,255,.78), 0 16px 36px rgba(83,67,38,.055); }
.metric-card { padding: 20px; border-radius: 24px; }
.metric-value { font-size: 1.35rem; font-weight: 760; letter-spacing: -.04em; margin-bottom: 6px; }
.metric-label { font-size: .84rem; line-height: 1.5; color: var(--muted); }
.steps-container { padding: 24px; border-radius: 28px; position: relative; overflow: hidden; }
.steps-container::before { content: ''; position: absolute; inset: 0 auto 0 34px; width: 1px; background: linear-gradient(transparent, rgba(217,111,50,.28), transparent); }
.workflow-list { display: flex; flex-direction: column; gap: 18px; position: relative; }
.workflow-item { display: flex; align-items: flex-start; gap: 18px; }
.step-num { flex: 0 0 auto; min-width: 40px; font-family: var(--font-mono); font-size: .76rem; font-weight: 700; color: var(--accent-dark); opacity: .82; }
.step-info { flex: 1; }
.step-title { font-weight: 720; font-size: .98rem; margin-bottom: 5px; }
.step-desc { font-size: .86rem; line-height: 1.58; color: var(--muted); }

.console-box { padding: 8px; border-radius: 34px; background: rgba(16,18,20,.88); border-color: rgba(255,255,255,.12); box-shadow: 0 34px 88px rgba(25,27,30,.22), inset 0 1px 0 rgba(255,255,255,.12); color: #f6f1e7; }
.console-section { padding: clamp(18px, 2.6vw, 30px); border-radius: 27px; }
.console-section.btn-section { padding-top: 0; }
.console-header { justify-content: space-between; color: rgba(246,241,231,.62); margin-bottom: 16px; }
.console-label { font-weight: 650; }
.mode-toggle { display: flex; gap: 4px; padding: 4px; border: 1px solid rgba(255,255,255,.1); border-radius: 999px; background: rgba(255,255,255,.06); }
.toggle-btn { background: transparent; border: none; border-radius: 999px; padding: 8px 12px; font-size: .75rem; font-weight: 650; color: rgba(246,241,231,.58); cursor: pointer; transition: transform .55s var(--ease-spring), background .55s var(--ease-spring), color .55s var(--ease-spring); }
.toggle-btn.active { background: #f6f1e7; color: #16181b; box-shadow: 0 8px 20px rgba(0,0,0,.16); }
.toggle-btn:hover:not(.active):not(:disabled) { color: #fff; transform: translateY(-1px); }
.toggle-btn:disabled { opacity: .48; cursor: not-allowed; }

.upload-zone { height: 214px; overflow-y: auto; display: flex; align-items: center; justify-content: center; cursor: pointer; border-style: dashed; border-radius: 25px; border-color: rgba(246,241,231,.18); background: rgba(255,255,255,.045); transition: transform .65s var(--ease-spring), border-color .65s var(--ease-spring), background .65s var(--ease-spring); }
.upload-zone.has-files { align-items: flex-start; }
.upload-zone:hover, .upload-zone.drag-over { background: rgba(255,255,255,.075); border-color: rgba(217,111,50,.48); transform: translateY(-2px); }
.upload-placeholder { text-align: center; color: rgba(246,241,231,.72); }
.upload-icon { width: 48px; height: 48px; border: 1px solid rgba(246,241,231,.16); border-radius: 16px; display: grid; place-items: center; margin: 0 auto 15px; color: #f6f1e7; background: rgba(255,255,255,.06); }
.upload-title { font-weight: 700; font-size: .98rem; margin-bottom: 6px; }
.upload-hint { font-family: var(--font-mono); font-size: .72rem; color: rgba(246,241,231,.44); }
.file-list { width: 100%; padding: 14px; display: flex; flex-direction: column; gap: 10px; }
.file-item { display: flex; align-items: center; padding: 10px 12px; border-radius: 16px; border-color: rgba(246,241,231,.13); background: rgba(255,255,255,.07); font-family: var(--font-mono); font-size: .8rem; color: rgba(246,241,231,.82); }
.file-name { flex: 1; margin: 0 10px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.remove-btn { background: rgba(255,255,255,.08); border: none; border-radius: 999px; width: 26px; height: 26px; cursor: pointer; color: rgba(246,241,231,.62); transition: transform .45s var(--ease-spring), color .45s var(--ease-spring); }
.remove-btn:hover { transform: scale(1.08); color: #fff; }
.console-divider { display: flex; align-items: center; margin: 0; }
.console-divider::before, .console-divider::after { content: ''; flex: 1; height: 1px; background: rgba(246,241,231,.11); }
.console-divider span { padding: 0 15px; font-family: var(--font-mono); font-size: .68rem; color: rgba(246,241,231,.32); }
.input-wrapper { position: relative; border-radius: 25px; border-color: rgba(246,241,231,.13); background: rgba(255,255,255,.055); overflow: hidden; }
.code-input, .topic-input { width: 100%; border: none; outline: none; font-family: var(--font-sans); color: #f6f1e7; background: transparent; }
.code-input { padding: 22px; padding-bottom: 50px; font-size: .98rem; line-height: 1.72; resize: vertical; min-height: 158px; }
.code-input::placeholder, .topic-input::placeholder { color: rgba(246,241,231,.34); }
.model-badge { position: absolute; bottom: 16px; right: 18px; font-family: var(--font-mono); font-size: .68rem; color: rgba(246,241,231,.38); }
.start-engine-btn, .generate-btn { border: none; cursor: pointer; font-weight: 760; transition: transform .6s var(--ease-spring), box-shadow .6s var(--ease-spring), background .6s var(--ease-spring), opacity .6s var(--ease-spring); }
.start-engine-btn { width: 100%; min-height: 68px; border-radius: 999px; padding: 10px 10px 10px 26px; background: #f6f1e7; color: #151719; font-size: 1rem; display: flex; justify-content: space-between; align-items: center; letter-spacing: -.01em; box-shadow: 0 20px 46px rgba(0,0,0,.22); }
.start-engine-btn:not(:disabled):hover { transform: translateY(-2px); box-shadow: 0 26px 55px rgba(0,0,0,.28); }
.start-engine-btn:active:not(:disabled) { transform: translateY(0) scale(.99); }
.start-engine-btn:disabled { opacity: .42; cursor: not-allowed; box-shadow: none; }
.start-engine-btn:hover .btn-arrow { transform: translateX(3px); background: rgba(217,111,50,.15); }
.auto-seed-section { padding: 0; }
.seed-topic-input { display: grid; grid-template-columns: 1fr auto; gap: 10px; margin-bottom: 10px; }
.topic-input { min-height: 50px; border-radius: 999px; padding: 0 18px; border: 1px solid rgba(246,241,231,.13); background: rgba(255,255,255,.055); }
.topic-input:focus { border-color: rgba(217,111,50,.5); }
.generate-btn { border-radius: 999px; padding: 0 18px; color: #151719; background: #f6f1e7; white-space: nowrap; }
.generate-btn:hover:not(:disabled) { transform: translateY(-1px); }
.generate-btn:disabled { opacity: .45; cursor: not-allowed; }
.seed-hint { font-family: var(--font-mono); font-size: .72rem; color: rgba(246,241,231,.42); }
.seed-progress { margin-top: 15px; padding: 14px; border-radius: 18px; border-color: rgba(246,241,231,.12); background: rgba(255,255,255,.055); }
.progress-bar-track { height: 6px; background: rgba(246,241,231,.11); border-radius: 999px; overflow: hidden; margin-bottom: 10px; }
.progress-bar-fill { height: 100%; background: linear-gradient(90deg, var(--accent), #f2bf7d); border-radius: 999px; transition: width .8s var(--ease-out); }
.progress-text { font-family: var(--font-mono); font-size: .72rem; color: rgba(246,241,231,.58); }
.seed-success { font-family: var(--font-mono); font-size: .78rem; color: #b8d0a9; margin-bottom: 4px; }
.blueprint-options { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 10px; margin-bottom: 16px; }
.blueprint-option { min-height: 116px; display: grid; align-content: start; gap: 8px; padding: 14px; color: rgba(246,241,231,.82); text-align: left; border: 1px solid rgba(246,241,231,.13); border-radius: 20px; background: rgba(255,255,255,.055); cursor: pointer; transition: transform .45s var(--ease-spring), border-color .45s var(--ease-spring), background .45s var(--ease-spring); }
.blueprint-option:hover, .blueprint-option.active { transform: translateY(-2px); border-color: rgba(217,111,50,.55); background: rgba(217,111,50,.13); }
.blueprint-option strong { color: #f6f1e7; font-size: .92rem; }
.blueprint-option span { color: rgba(246,241,231,.56); font-size: .78rem; line-height: 1.5; }
.blueprint-idea-box, .paste-blueprint-box { display: grid; gap: 12px; }
.blueprint-meta-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 10px; }
.blueprint-textarea { min-height: 130px; }
.blueprint-generate { width: fit-content; }
.audit-mode-row { display: flex; align-items: center; justify-content: space-between; gap: 12px; padding: 12px; border: 1px solid rgba(246,241,231,.13); border-radius: 18px; background: rgba(255,255,255,.055); color: rgba(246,241,231,.75); }
.audit-select { min-width: 220px; color: #f6f1e7; border: 1px solid rgba(246,241,231,.14); border-radius: 14px; background: rgba(16,18,20,.86); padding: 10px 12px; }
.instruction-import-box { display: flex; justify-content: space-between; align-items: center; gap: 14px; padding: 14px; border: 1px solid rgba(104,225,253,.18); border-radius: 18px; background: rgba(104,225,253,.065); }
.instruction-import-box strong { display: block; margin-bottom: 5px; color: #f6f1e7; font-size: .86rem; }
.instruction-import-box span { display: block; color: rgba(246,241,231,.56); font-size: .76rem; line-height: 1.5; }
.instruction-btn { white-space: nowrap; color: #68e1fd; border: 1px solid rgba(104,225,253,.28); }
.instruction-preview { display: flex; align-items: center; justify-content: space-between; gap: 10px; padding: 10px 12px; border-radius: 14px; background: rgba(124,255,178,.08); color: #b8d0a9; font-family: var(--font-mono); font-size: .76rem; }
.instruction-preview button { border: none; border-radius: 999px; padding: 6px 9px; background: rgba(255,255,255,.08); color: rgba(246,241,231,.72); cursor: pointer; }
.instruction-textarea { min-height: 96px; font-size: .78rem; color: rgba(246,241,231,.72); }
.blueprint-status { padding: 11px 13px; border-radius: 14px; border: 1px solid rgba(246,241,231,.12); background: rgba(255,255,255,.055); color: rgba(246,241,231,.68); font-size: .8rem; }
.blueprint-status.success { border-color: rgba(124,255,178,.2); background: rgba(124,255,178,.08); color: #b8d0a9; }
.blueprint-status.error { border-color: rgba(255,112,112,.24); background: rgba(255,112,112,.08); color: #ffb1b1; }
.blueprint-preview-card { display: grid; gap: 8px; padding: 14px; border: 1px solid rgba(217,111,50,.22); border-radius: 18px; background: rgba(217,111,50,.08); }
.preview-kicker { font-family: var(--font-mono); font-size: .68rem; color: var(--accent); text-transform: uppercase; letter-spacing: .1em; }
.blueprint-preview-card strong { color: #f6f1e7; }
.blueprint-preview-card p { margin: 0; color: rgba(246,241,231,.62); font-size: .82rem; line-height: 1.55; }
.preview-tags { display: flex; flex-wrap: wrap; gap: 6px; }
.preview-tags span { padding: 5px 8px; border-radius: 999px; background: rgba(255,255,255,.08); color: rgba(246,241,231,.72); font-size: .7rem; }
.gen-loading { animation: pulse-gen 1.4s var(--ease-out) infinite; }
@keyframes pulse-gen { 0%,100%{opacity:1} 50%{opacity:.52} }
@keyframes riseIn { from { opacity: 0; transform: translateY(26px); filter: blur(8px); } to { opacity: 1; transform: translateY(0); filter: blur(0); } }

@media (max-width: 1024px) {
  .hero-section, .dashboard-section, .command-header { grid-template-columns: 1fr; }
  .mode-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
  .hero-section { min-height: auto; }
  .hero-right { min-height: 360px; justify-items: center; }
  .logo-container { width: min(100%, 340px); transform: none; }
  .scroll-down-btn { display: none; }
}

@media (max-width: 720px) {
  .navbar { width: calc(100% - 24px); margin-top: 12px; padding-left: 16px; }
  .selected-mode-ribbon { width: calc(100% - 24px); grid-template-columns: 1fr auto; border-radius: 22px; }
  .selected-mode-ribbon span, .selected-mode-ribbon em { display: none; }
  .github-link { font-size: 0; padding: 10px; }
  .main-content { padding: 48px 14px 64px; }
  .main-title { font-size: clamp(3rem, 18vw, 4.4rem); }
  .dashboard-section, .command-center-section { padding: 6px; border-radius: 28px; }
  .mode-grid { grid-template-columns: 1fr; }
  .mode-card { min-height: auto; }
  .left-panel, .console-box { border-radius: 23px; }
  .metrics-row, .seed-topic-input { grid-template-columns: 1fr; }
  .console-header { align-items: flex-start; flex-direction: column; gap: 12px; }
  .mode-toggle { width: 100%; }
  .blueprint-options, .blueprint-meta-grid { grid-template-columns: 1fr; }
  .audit-mode-row, .instruction-import-box { display: grid; }
  .toggle-btn { flex: 1; }
}
</style>
