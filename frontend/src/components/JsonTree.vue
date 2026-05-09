<template>
  <div class="json-tree">
    <template v-if="isObject(value)">
      <div v-for="(val, key) in value" :key="key" class="entry">
        <h3>{{ label(key) }}</h3>
        <JsonTree :value="val" />
      </div>
    </template>
    <template v-else-if="Array.isArray(value)">
      <ul>
        <li v-for="(item, index) in value" :key="index">
          <JsonTree :value="item" />
        </li>
      </ul>
    </template>
    <p v-else>{{ value ?? '-' }}</p>
  </div>
</template>

<script setup>
defineProps({ value: { type: null, required: false, default: null } })
const isObject = value => value && typeof value === 'object' && !Array.isArray(value)
const label = key => String(key).replaceAll('_', ' ')
</script>

<style scoped>
.json-tree{color:#dce8ff;line-height:1.7}.entry{margin:0 0 18px;padding:0 0 14px;border-bottom:1px solid rgba(255,255,255,.07)}h3{margin:0 0 8px;color:#68e1fd;text-transform:capitalize;font-size:15px;letter-spacing:.02em}p{margin:0;white-space:pre-wrap}ul{margin:0;padding-left:20px}li{margin:8px 0}li>.json-tree{display:inline}
</style>
