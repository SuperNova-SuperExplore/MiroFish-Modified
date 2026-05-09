<template>
  <main class="ops-list-page">
    <section class="hero panel">
      <div>
        <p class="eyebrow">Archive</p>
        <h1>Riwayat Operasi</h1>
        <p class="muted">Cari prediksi, blueprint, audit, dan revisi yang pernah dibuat.</p>
      </div>
      <router-link class="btn" to="/">Command Center</router-link>
    </section>

    <section class="panel filters">
      <input v-model="filters.q" placeholder="Cari judul, isi, tag..." @keyup.enter="load" />
      <select v-model="filters.mode" @change="load">
        <option value="">Semua mode</option>
        <option value="project_prediction">Prediksi Project</option>
        <option value="question_prediction">Prediksi Pertanyaan</option>
        <option value="blueprint_design">Blueprint Design</option>
        <option value="blueprint_audit">Blueprint Audit</option>
        <option value="blueprint_revision">Blueprint Revision</option>
      </select>
      <input v-model="filters.tag" placeholder="Tag" @keyup.enter="load" />
      <button class="btn" @click="load">Cari</button>
    </section>

    <section class="list">
      <router-link v-for="op in operations" :key="op.operation_id" class="op-card" :to="`/operations/${op.operation_id}`">
        <div><span>{{ op.mode }}</span><h2>{{ op.title || op.operation_id }}</h2><p>{{ op.created_at }}</p></div>
        <div class="tags"><em v-for="tag in op.tags" :key="tag">{{ tag }}</em></div>
      </router-link>
      <div v-if="!loading && operations.length === 0" class="panel muted">Belum ada operation.</div>
    </section>
  </main>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import strategicApi from '../api/strategic'
const operations = ref([])
const loading = ref(false)
const filters = reactive({ q: '', mode: '', tag: '', limit: 50 })
const load = async () => { loading.value = true; try { const res = await strategicApi.listOperations(filters); operations.value = res.data || [] } finally { loading.value = false } }
onMounted(load)
</script>

<style scoped>
.ops-list-page{min-height:100vh;padding:28px;color:#eef4ff;background:radial-gradient(circle at top right,rgba(200,169,106,.16),transparent 32%),#05070d}.panel,.op-card{border:1px solid rgba(255,255,255,.11);background:rgba(9,14,27,.82);border-radius:24px;padding:22px;box-shadow:0 22px 70px rgba(0,0,0,.28)}.hero{display:flex;justify-content:space-between;align-items:flex-start;gap:18px;margin-bottom:16px}.eyebrow{color:#68e1fd;letter-spacing:.16em;text-transform:uppercase;font-size:12px}h1{font-size:clamp(38px,6vw,72px);margin:8px 0;letter-spacing:-.06em}.muted{color:#8e9aaf}.btn{border:0;border-radius:999px;padding:12px 16px;font-weight:800;cursor:pointer;color:#041018;background:linear-gradient(135deg,#68e1fd,#c8a96a);text-decoration:none}.filters{display:grid;grid-template-columns:1fr 220px 180px auto;gap:10px;margin-bottom:16px}input,select{color:#eef4ff;border:1px solid rgba(255,255,255,.12);border-radius:14px;background:rgba(255,255,255,.06);padding:12px}.list{display:grid;gap:12px}.op-card{display:flex;justify-content:space-between;gap:16px;color:#eef4ff;text-decoration:none;transition:transform .3s}.op-card:hover{transform:translateY(-2px)}.op-card span{color:#68e1fd;font-size:12px;text-transform:uppercase;letter-spacing:.12em}.op-card h2{margin:8px 0;font-size:22px}.op-card p{color:#8e9aaf;margin:0}.tags{display:flex;gap:6px;flex-wrap:wrap;align-content:flex-start}.tags em{font-style:normal;color:#c8a96a;border:1px solid rgba(200,169,106,.24);border-radius:999px;padding:5px 8px;font-size:12px}@media(max-width:760px){.hero,.op-card{display:grid}.filters{grid-template-columns:1fr}}
</style>
