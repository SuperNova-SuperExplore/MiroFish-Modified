<template>
  <main class="strategic-placeholder">
    <section class="placeholder-card">
      <p class="eyebrow">Strategic Mode</p>
      <h1>{{ modeId }}</h1>
      <p>
        Runner mode ini jadi step berikutnya. Backend endpoint sudah siap; page ini sementara jadi landing route supaya Command Center bisa dinavigasi.
      </p>
      <div class="actions">
        <router-link to="/" class="btn">← Command Center</router-link>
        <router-link to="/ai-settings" class="btn muted">AI Settings</router-link>
      </div>
    </section>
  </main>
</template>

<script setup>
defineProps({
  modeId: {
    type: String,
    required: true
  }
})
</script>

<style scoped>
.strategic-placeholder {
  min-height: 100vh;
  display: grid;
  place-items: center;
  padding: 28px;
  color: #eef4ff;
  background:
    radial-gradient(circle at top left, rgba(104, 225, 253, 0.18), transparent 32%),
    #05070d;
}

.placeholder-card {
  max-width: 760px;
  padding: 34px;
  border-radius: 28px;
  border: 1px solid rgba(255,255,255,.12);
  background: rgba(9,14,27,.82);
  box-shadow: 0 28px 90px rgba(0,0,0,.34);
}

.eyebrow {
  color: #68e1fd;
  letter-spacing: .16em;
  text-transform: uppercase;
  font-size: 12px;
  margin-bottom: 12px;
}

h1 {
  margin: 0 0 14px;
  font-size: clamp(36px, 6vw, 72px);
  letter-spacing: -.06em;
}

p {
  color: #9da8bd;
  line-height: 1.7;
}

.actions {
  display: flex;
  gap: 12px;
  margin-top: 24px;
}

.btn {
  color: #041018;
  text-decoration: none;
  border-radius: 999px;
  padding: 12px 18px;
  font-weight: 800;
  background: linear-gradient(135deg, #68e1fd, #c8a96a);
}

.btn.muted {
  color: #eef4ff;
  border: 1px solid rgba(255,255,255,.14);
  background: rgba(255,255,255,.08);
}
</style>
