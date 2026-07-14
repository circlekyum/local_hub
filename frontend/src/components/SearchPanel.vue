<template>
  <div class="search-panel">
    <div class="search-center">
      <h2 class="panel-title">어떤 장소를 알아볼까요?</h2>

      <div class="controls">
        <div class="input-wrap">
          <input
            v-model="q"
            @input="onInput"
            @keydown="onKeydown"
            placeholder="검색어 입력"
            autocomplete="off"
            ref="inputEl"
          />
          <ul v-if="showSuggestions" class="suggestions" role="listbox">
            <li
              v-for="(s, idx) in filteredSuggestions"
              :key="s"
              :class="{ highlighted: idx === activeIndex }"
              @click="chooseSuggestion(s)"
              @mouseover="activeIndex = idx"
              role="option"
              :aria-selected="idx === activeIndex"
            >
              {{ s }}
            </li>
          </ul>
        </div>

        <button @click="doSearch" :disabled="loading">검색</button>
      </div>
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
import { ref, watch, computed } from 'vue'
import { usePlaces } from '../stores/usePlaces'

const store = usePlaces()
const q = ref(store.searchText)
const loading = store.loading
const places = store.places
const selected = store.selected

watch(q, (v) => {
  store.searchText = v
})

// 더미 자동완성 키워드 (서울 주요 명소)
const keywords = [
  '광화문',
  '경복궁',
  '롯데타워',
  '여의도',
  '남산타워',
  '북촌한옥마을',
  '명동',
  '인사동',
  '홍대',
  '강남역',
  '청계천',
  '동대문',
  '이태원',
]

const showSuggestions = ref(false)
const activeIndex = ref(-1)
const inputEl = ref<HTMLInputElement | null>(null)

const filteredSuggestions = computed(() => {
  const val = q.value.trim()
  if (!val) return []
  const lower = val.toLowerCase()
  return keywords.filter((k) => k.toLowerCase().includes(lower)).slice(0, 6)
})

function onInput() {
  const has = filteredSuggestions.value.length > 0 && q.value.trim().length >= 1
  showSuggestions.value = has
  if (!has) activeIndex.value = -1
}

function chooseSuggestion(s: string) {
  q.value = s
  showSuggestions.value = false
  activeIndex.value = -1
  doSearch()
}

function doSearch() {
  store.search(q.value)
  showSuggestions.value = false
  activeIndex.value = -1
}

function select(p: any) {
  store.selectPlace(p)
}

// 키보드 탐색: ArrowDown, ArrowUp, Enter, Escape
function onKeydown(e: KeyboardEvent) {
  if (!showSuggestions.value && (e.key === 'ArrowDown' || e.key === 'ArrowUp')) {
    // 리스트가 닫혀있으면 열기 (한 글자 이상일 때)
    if (q.value.trim().length >= 1 && filteredSuggestions.value.length > 0) {
      showSuggestions.value = true
      activeIndex.value = -1
    }
  }

  if (!showSuggestions.value) {
    if (e.key === 'Enter') {
      doSearch()
    }
    return
  }

  if (e.key === 'ArrowDown') {
    e.preventDefault()
    activeIndex.value = Math.min(activeIndex.value + 1, filteredSuggestions.value.length - 1)
    scrollActiveIntoView()
  } else if (e.key === 'ArrowUp') {
    e.preventDefault()
    activeIndex.value = Math.max(activeIndex.value - 1, 0)
    scrollActiveIntoView()
  } else if (e.key === 'Enter') {
    e.preventDefault()
    if (activeIndex.value >= 0 && activeIndex.value < filteredSuggestions.value.length) {
      chooseSuggestion(filteredSuggestions.value[activeIndex.value])
    } else {
      doSearch()
    }
  } else if (e.key === 'Escape') {
    showSuggestions.value = false
    activeIndex.value = -1
  }
}

function scrollActiveIntoView() {
  // suggestion 항목이 보이도록 스크롤
  const ul = inputEl.value?.nextElementSibling as HTMLElement | null
  if (!ul) return
  const items = ul.querySelectorAll('li')
  const idx = activeIndex.value
  if (idx < 0 || idx >= items.length) return
  const el = items[idx] as HTMLElement
  el.scrollIntoView({ block: 'nearest' })
}
</script>

<style scoped>
.search-panel {
  height: 100%;
  display: flex;
  flex-direction: column;
}
.search-center {
  margin: auto 0;
  width: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 12px;
  box-sizing: border-box;
}
.panel-title {
  margin: 0 0 12px 0;
  font-size: 18px;
  text-align: center;
}
.controls {
  display: flex;
  gap: 8px;
  width: 100%;
  max-width: 420px;
  position: relative;
}
.input-wrap {
  flex: 1;
  position: relative;
}
.controls input {
  width: 100%;
  padding: 6px 8px;
  box-sizing: border-box;
}
.suggestions {
  position: absolute;
  top: calc(100% + 6px);
  left: 0;
  right: 0;
  background: #fff;
  border: 1px solid #e6e6e6;
  border-radius: 4px;
  max-height: 220px;
  overflow: auto;
  z-index: 30;
  list-style: none;
  margin: 0;
  padding: 6px 0;
  box-shadow: 0 6px 18px rgba(0, 0, 0, 0.08);
}
.suggestions li {
  padding: 8px 12px;
  cursor: pointer;
}
.suggestions li:hover,
.suggestions li.highlighted {
  background: #f5faff;
}
.results {
  list-style: none;
  padding: 0;
  margin: 8px 0 0 0;
  overflow: auto;
  flex: 1;
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
  margin: 8px 12px;
}
</style>
