<template>
  <div class="search-panel" :class="{ compact: isSearched }">
    <div class="left-col">
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

      <!-- 게시물 리스트 -->
      <div class="posts-wrap" v-if="isSearched">
        <h3 class="posts-title">{{ regionTitle }}</h3>

        <div v-if="posts.length === 0" class="no-posts">
          <div>첫 글을 작성해보세요</div>
          <button @click="onCreateClick">글 작성</button>
        </div>

        <ul v-else class="posts-list">
          <!-- <li
            v-for="post in posts"
            :key="post.post_id"
            @click="openPost(post)"
            :class="{ selected: activePost?.post_id === post.post_id }"
          >
            <div class="post-title">{{ truncate(post.post_title, 60) }}</div>
            <div class="post-meta">{{ post.date }}</div>
          </li> -->
          <li
            v-for="post in posts"
            :key="post.post_id"
            @click="openPost(post)"
            :class="{ selected: activePost?.post_id === post.post_id }"
          >
            <div class="post-left">
              <div class="post-avatar" aria-hidden="true">{{ post.post_title.charAt(0) }}</div>
            </div>

            <div class="post-main">
              <div class="post-title">{{ truncate(post.post_title, 60) }}</div>
              <div class="post-excerpt">{{ truncate(post.contents, 120) }}</div>

              <div class="post-row">
                <div class="post-meta">{{ post.date }}</div>
                <div class="rating" aria-hidden="true">
                  <span class="star">★</span><span class="star">★</span><span class="star">★</span
                  ><span class="star muted">★</span><span class="star muted">★</span>
                </div>
              </div>
            </div>
          </li>
        </ul>
      </div>

      <ul class="results" v-if="places.length > 0">
        <li
          v-for="p in places"
          :key="p.id"
          @click="selectAndLoad(p)"
          :class="{ active: selected?.id === p.id }"
        >
          <div class="title">{{ p.name }}</div>
          <div class="addr">{{ p.addr }}</div>
        </li>
      </ul>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, computed } from 'vue'
import { usePlaces } from '../stores/usePlaces'

interface Post {
  post_id: string
  post_title: string
  date: string
  contents: string
  place_id?: string
}

const emit = defineEmits<{
  (e: 'open-post', post: Post): void
}>()

const store = usePlaces()
const q = ref(store.searchText)
const loading = store.loading
const places = store.places
const selected = store.selected

watch(q, (v) => {
  store.searchText = v
})

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
const isSearched = ref(false)

const dummyStore: Record<string, Post[]> = {}
const posts = ref<Post[]>([])
const activePost = ref<Post | null>(null)

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
  isSearched.value = true
  store.search(q.value)
  showSuggestions.value = false
  activeIndex.value = -1
  loadPostsByName(q.value)
}

function selectAndLoad(p: any) {
  select(p)
  loadPosts(p.id, p.name)
}

function select(p: any) {
  store.selectPlace(p)
}

function loadPosts(placeId?: string, placeName?: string) {
  const key = placeId ?? placeName ?? q.value ?? 'default'
  posts.value = makeDummyPostsFor(key)
  activePost.value = null
}

function loadPostsByName(name: string) {
  const key = (name || 'default').toLowerCase()
  posts.value = makeDummyPostsFor(key)
  activePost.value = null
}

function makeDummyPostsFor(key: string) {
  if (dummyStore[key]) return dummyStore[key]

  const arr: Post[] = [
    {
      post_id: key + '-1',
      post_title: `${capitalize(key)}의 첫번째 추천 장소`,
      date: '2026-07-14',
      contents: `${capitalize(key)} 지역에 대해 작성된 더미 글 내용입니다. 상세 설명 A.`,
      place_id: key,
    },
    {
      post_id: key + '-2',
      post_title: `${capitalize(key)}에서 가볼만한 카페 리스트`,
      date: '2026-07-10',
      contents: `${capitalize(key)} 지역의 카페들을 정리한 더미 내용입니다.`,
      place_id: key,
    },
    {
      post_id: key + '-3',
      post_title: `${capitalize(key)} 숨겨진 명소 한곳`,
      date: '2026-06-21',
      contents: `${capitalize(key)}의 작은 명소를 소개하는 더미 글입니다.`,
      place_id: key,
    },
  ]
  dummyStore[key] = arr
  return arr
}

function openPost(p: Post) {
  // 상세 패널을 부모(App.vue)로 위임
  emit('open-post', p)
}

function truncate(s: string, len = 60) {
  if (!s) return ''
  return s.length > len ? s.slice(0, len) + '…' : s
}

function capitalize(s: string) {
  if (!s) return ''
  return s.charAt(0).toUpperCase() + s.slice(1)
}

function onKeydown(e: KeyboardEvent) {
  if (!showSuggestions.value && (e.key === 'ArrowDown' || e.key === 'ArrowUp')) {
    if (q.value.trim().length >= 1 && filteredSuggestions.value.length > 0) {
      showSuggestions.value = true
      activeIndex.value = -1
    }
  }

  if (!showSuggestions.value) {
    if (e.key === 'Enter') doSearch()
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
  const ul = inputEl.value?.nextElementSibling as HTMLElement | null
  if (!ul) return
  const items = ul.querySelectorAll('li')
  const idx = activeIndex.value
  if (idx < 0 || idx >= items.length) return
  const el = items[idx] as HTMLElement
  el.scrollIntoView({ block: 'nearest' })
}

function onCreateClick() {
  alert('글 작성 기능은 다음 단계에서 구현합니다.')
}

const regionTitle = computed(() => {
  return (selected && selected.name) || (q.value && q.value) || '선택된 지역'
})
</script>

<style scoped>
.search-panel {
  height: 100%;
  width: 100%; /*부모 크기에 맞춤*/
  display: flex;
  gap: 12px;
  align-items: stretch;
  justify-content: center;
}
.left-col {
  /* width: 400px; */
  width: 100%;
  max-width: 400px;
  height: 100%;
  display: flex;
  flex-direction: column;
  overflow: hidden;
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
.search-panel.compact .search-center {
  margin: 12px 0;
  align-items: stretch;
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
.posts-wrap {
  padding: 8px 12px;
  border-top: 1px solid #eee;

  flex: 1;               /* 검색창을 제외한 남은 세로 공간을 전부 차지합니다 */
  min-height: 0;         /* flex 안에서 스크롤이 정상 작동하기 위한 CSS 필수 트릭 */
  overflow-y: auto;      /* 세로로 내용이 넘치면 이 영역에만 스크롤바를 만듭니다 */
}
.posts-title {
  margin: 8px 0;
  font-size: 16px;
}
.no-posts {
  padding: 12px;
  color: #666;
}
.posts-list {
  list-style: none;
  padding: 0;
  margin: 0;
}
/* .posts-list li {
  padding: 10px;
  border-bottom: 1px solid #eee;
  cursor: pointer;
} */
.posts-list li {
  display: flex;
  gap: 12px;
  padding: 12px;
  border-bottom: 1px solid #eee;
  cursor: pointer;
  align-items: flex-start;
  transition:
    background 0.12s ease,
    transform 0.08s ease;
}
.posts-list li:hover {
  background: #f8fbff;
  transform: translateY(-2px);
  box-shadow: 0 6px 18px rgba(13, 45, 78, 0.06);
}
/* 선택된 항목 강조 */
.posts-list li.selected {
  background: linear-gradient(90deg, rgba(240, 248, 255, 0.6), #fff);
  border-left: 3px solid #3b82f6;
}
/* .posts-list li.selected {
  background: #f0f8ff;
} */
.post-left {
  width: 48px;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
}
.post-avatar {
  width: 44px;
  height: 44px;
  border-radius: 50%;
  background: linear-gradient(135deg, #6fb1ff, #3b82f6);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 16px;
  box-shadow: 0 2px 8px rgba(59, 130, 246, 0.18);
}

.post-main {
  flex: 1;
  min-width: 0;
}
.post-title {
  font-weight: 700;
  margin-bottom: 6px;
  color: #102a43;
}
.post-excerpt {
  font-size: 13px;
  color: #475569;
  margin-bottom: 8px;
  white-space: normal;
  overflow: hidden;
  text-overflow: ellipsis;
}

.post-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
}
.post-meta {
  font-size: 12px;
  color: #7b8794;
}
/* .post-title {
  font-weight: 600;
}
.post-meta {
  font-size: 12px;
  color: #777;
} */

.rating {
  display: inline-flex;
  gap: 2px;
  align-items: center;
  font-size: 13px;
}
.rating .star {
  color: #f6b93b;
  text-shadow: 0 1px 0 rgba(0, 0, 0, 0.03);
}
.rating .star.muted {
  color: #e6e9ee;
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

/* 오른쪽 상세 패널 */
.detail-panel {
  width: 380px;
  background: #fff;
  border-left: 1px solid #e6e6e6;
  padding: 16px;
  box-sizing: border-box;
  position: relative;
}
.slide-enter-from {
  transform: translateX(100%);
}
.slide-enter-active {
  transition: transform 0.22s ease;
}
.slide-leave-to {
  transform: translateX(100%);
}
.slide-leave-active {
  transition: transform 0.2s ease;
}
.close {
  position: absolute;
  right: 8px;
  top: 8px;
  border: none;
  background: transparent;
  font-size: 20px;
  cursor: pointer;
}
.detail-title {
  margin-top: 0;
}
.detail-body {
  margin-top: 12px;
  white-space: pre-wrap;
}

/* 모바일/좁은 화면을 위한 간단한 반응형 */
@media (max-width: 520px) {
  .post-left {
    display: none;
  }
  .left-col {
    width: 100%;
  }
}
</style>
