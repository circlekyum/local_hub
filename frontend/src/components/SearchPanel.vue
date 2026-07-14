<template>
  <div class="search-panel">
    <div class="controls">
      <input v-model="q" @keyup.enter="doSearch" placeholder="검색어 입력" />
      <button @click="doSearch" :disabled="loading">검색</button>
    </div>

    <div v-if="loading" class="loading">검색 중...</div>

    <ul class="results">
      <li
        v-for="p in places"
        :key="p.id"
        @click="select(p)"
        :class="{ active: selected?.id === p.id }"
      >
        <div class="title">{{ p.name }}</div>
        <div class="addr">{{ p.addr }}</div>
      </li>
    </ul>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { usePlaces } from '../stores/usePlaces'

const store = usePlaces()
const q = ref(store.searchText)
const loading = store.loading
const places = store.places
const selected = store.selected

watch(q, (v) => {
  store.searchText = v
})

function doSearch() {
  store.search(q.value)
}

function select(p: any) {
  store.selectPlace(p)
}
</script>

<style scoped>
.search-panel {
  padding: 12px;
}
.controls {
  display: flex;
  gap: 8px;
  margin-bottom: 8px;
}
.controls input {
  flex: 1;
  padding: 6px 8px;
}
.results {
  list-style: none;
  padding: 0;
  margin: 0;
}
.results li {
  padding: 8px;
  border-bottom: 1px solid #eee;
  cursor: pointer;
}
.results li.active {
  background: #f0f8ff;
}
.title {
  font-weight: 600;
}
.addr {
  font-size: 12px;
  color: #666;
}
.loading {
  font-style: italic;
  margin-bottom: 8px;
}
</style>
