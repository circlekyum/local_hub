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
          <button class="chat-toggle" @click="$emit('open-chat')" aria-label="챗봇 열기">챗봇</button>
        </div>
      </div>

      <div v-if="loading" class="loading">검색 중...</div>

      <!-- 게시물 리스트 -->
      <div class="posts-wrap" v-if="isSearched">
        <!-- <h3 class="posts-title">{{ regionTitle }}</h3> -->
        <div class="posts-header">
          <h3 class="posts-title">{{ regionTitle }}</h3>
          <button class="write-btn" @click="onCreateClick" aria-label="글 작성">
            <span class="write-icon">✏️</span>
          </button>
        </div>

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

                <div class="actions">
                  <button class="icon-btn edit" @click.stop="onEdit(post)" aria-label="글 수정" title="수정">
                    <!-- pencil SVG (그레이) -->
                    <svg viewBox="0 0 24 24" width="16" height="16" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
                      <path d="M3 17.25V21h3.75L17.81 9.94l-3.75-3.75L3 17.25z" fill="#6b7280"/>
                      <path d="M20.71 7.04a1 1 0 0 0 0-1.41l-2.34-2.34a1 1 0 0 0-1.41 0l-1.83 1.83 3.75 3.75 1.83-1.83z" fill="#6b7280"/>
                    </svg>
                  </button>

                  <button class="icon-btn delete" @click.stop="onDelete(post)" aria-label="글 삭제" title="삭제">
                    <!-- trash SVG (그레이) -->
                    <svg viewBox="0 0 24 24" width="16" height="16" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
                      <path d="M9 3h6l1 2h5v2H3V5h5l1-2z" fill="#6b7280"/>
                      <path d="M6 9h12v10a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2V9z" fill="#6b7280"/>
                    </svg>
                  </button>
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
// import { storeToRefs } from 'pinia'
import { usePlaces } from '../stores/usePlaces'
import { fetchPostById, updatePost, deletePost } from '../services/api'

interface Post {
  post_id: string
  post_title: string
  date: string
  contents: string
  place_id?: string
}

const emit = defineEmits<{
  (e: 'open-post', post: Post): void
  (e: 'open-create'): void
  (e: 'open-chat'): void
  (e: 'open-create'): void // 글쓰기 창 열어달라는 신호
  // (e: 'edit-post', post: Post): void // 글 편집
  (e: 'request-edit', post: Post): void // 글 편집
  (e: 'delete-post', post: Post): void // 글 삭제

}>()

const store = usePlaces()
const q = ref(store.searchText)
const loading = store.loading
const places = store.places
const selected = store.selected
// const posts = store.posts
const posts = computed(() =>
  store.posts.map((p) => ({
    post_id: String(p.id),
    post_title: p.title ?? '',
    date: p.created_at ? new Date(p.created_at).toISOString().slice(0, 10) : '',
    contents: '', // 상세 내용은 별도 조회(openPost)에서 채웁니다
    place_id: selected?.id ?? undefined,
  }))
)
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
const postsList = ref<Post[]>([])
const activePost = ref<Post | null>(null)

const filteredSuggestions = computed(() => {
  const val = q.value.trim()
  if (!val) return []
  const lower = val.toLowerCase()
  return keywords.filter((k) => k.toLowerCase().includes(lower)).slice(0, 6)
})


// const showEditModal = ref(false)
// const editingPost = ref<Post | null>(null)

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

// function doSearch() {
//   isSearched.value = true
//   store.search(q.value)
//   showSuggestions.value = false
//   activeIndex.value = -1
//   loadPostsByName(q.value)
// }
async function doSearch() {
  const keyword = q.value.trim()
  if (!keyword) return

  isSearched.value = true
  showSuggestions.value = false
  activeIndex.value = -1
  console.log('실제 DB 검색 시작: ', keyword)
  await store.search(q.value)

  // 해당 장소의 post 보여주기 필요
  // posts value 활용하는 loadPosts 함수 필요!
  // loadPosts(selected.value?.id, q.value)
}
// function selectAndLoad(p: any) {
//   select(p)
//   loadPosts(p.id, p.name)
// }
async function selectAndLoad(p: any) {

  await store.selectPlace(p)
  isSearched.value = true;
}

function select(p: any) {
  store.selectPlace(p)
}

// function loadPosts(placeId?: string, placeName?: string) {
//   const key = placeId ?? placeName ?? q.value ?? 'default'
//   posts.value = makeDummyPostsFor(key)
//   activePost.value = null
// }


// function loadPostsByName(name: string) {
//   const key = (name || 'default').toLowerCase()
//   posts.value = makeDummyPostsFor(key)
//   activePost.value = null
// }

// function makeDummyPostsFor(key: string) {
//   if (dummyStore[key]) return dummyStore[key]

//   const arr: Post[] = [
//     {
//       post_id: key + '-1',
//       post_title: `${capitalize(key)}의 첫번째 추천 장소`,
//       date: '2026-07-14',
//       contents: `${capitalize(key)} 지역에 대해 작성된 더미 글 내용입니다. 상세 설명 A.`,
//       place_id: key,
//     },
//     {
//       post_id: key + '-2',
//       post_title: `${capitalize(key)}에서 가볼만한 카페 리스트`,
//       date: '2026-07-10',
//       contents: `${capitalize(key)} 지역의 카페들을 정리한 더미 내용입니다.`,
//       place_id: key,
//     },
//     {
//       post_id: key + '-3',
//       post_title: `${capitalize(key)} 숨겨진 명소 한곳`,
//       date: '2026-06-21',
//       contents: `${capitalize(key)}의 작은 명소를 소개하는 더미 글입니다.`,
//       place_id: key,
//     },
//   ]
//   dummyStore[key] = arr
//   return arr
// }

// function openPost(p: Post) {
//   // 상세 패널을 부모(App.vue)로 위임
//   emit('open-post', p)
// }
async function openPost(p: Post) {
  try {
    const id = Number(p.post_id)
    const detail = await fetchPostById(id)
    const payload = {
      post_id: String(detail.id),
      post_title: detail.title || detail.post_title || '',
      date: new Date(detail.created_at).toISOString().slice(0, 10),
      contents: detail.content ?? detail.post_contents ?? '',
      place_id: detail.place_id ?? p.place_id,
    }
    emit('open-post', payload)
  } catch (err) {
    console.error('openPost error', err)
    // fallback: emit list item without contents
    emit('open-post', p)
  }
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
  emit('open-create')
}

const regionTitle = computed(() => {
  return (selected && selected.value?.name ) || (q.value && q.value) || '선택된 지역'
})

// async function onEdit(p: Post) {
//   const pwd = prompt('수정하려면 비밀번호를 입력하세요.')
//   if (pwd == null) return

//   const newTitle = prompt('새 제목을 입력하세요', p.post_title)
//   if (newTitle == null) return

//   const newContent = prompt('새 내용을 입력하세요', p.contents ?? '')
//   if (newContent == null) return

//   try {
//     await updatePost(Number(p.post_id), {
//       post_title: newTitle,
//       post_contents: newContent,
//       post_pwd: pwd,
//     })

//     // 갱신: 선택된 장소가 있으면 장소별 재조회, 아니면 키워드 검색 재실행
//     if (selected?.value?.id) {
//       await store.selectPlace(selected.value.id)
//     } else {
//       await store.search(q.value)
//     }
//   } catch (err: any) {
//     if (err?.status === 403) {
//       alert('비밀번호가 일치하지 않습니다.')
//     } else {
//       console.error('update failed', err)
//       alert('수정에 실패했습니다.')
//     }
//   }
// }
function onEdit(p: Post) {
  emit('request-edit', p)
}

// async function onModalSave(payload: { post_id: string; post_title: string; post_contents: string; post_pwd: string }) {
//   try {
//     await updatePost(Number(payload.post_id), {
//       post_title: payload.post_title,
//       post_contents: payload.post_contents,
//       post_pwd: payload.post_pwd,
//     })
//     // 갱신
//     if (selected?.value?.id) {
//       await store.selectPlace(selected.value.id)
//     } else {
//       await store.search(q.value)
//     }
//     alert('수정되었습니다.')
//     showEditModal.value = false
//     editingPost.value = null
//   } catch (err: any) {
//     if (err?.status === 403) {
//       alert('비밀번호가 일치하지 않습니다.')
//     } else {
//       console.error(err)
//       alert('수정에 실패했습니다.')
//     }
//   }
// }

// function onModalClose() {
//   showEditModal.value = false
//   editingPost.value = null
// }


async function onDelete(p: Post) {
  const pwd = prompt('삭제하려면 비밀번호를 입력하세요.')
  if (pwd == null) return
  if (!confirm('정말 삭제하시겠습니까?')) return

  try {
    await deletePost(Number(p.post_id), pwd)

    if (selected?.value?.id) {
      await store.selectPlace(selected.value.id)
    } else {
      await store.search(q.value)
    }
  } catch (err: any) {
    if (err?.status === 403) {
      alert('비밀번호가 일치하지 않습니다.')
    } else {
      console.error('delete failed', err)
      alert('삭제에 실패했습니다.')
    }
  }
}

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
  width: 100%;
  max-width: 400px;
  height: 100%;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}
/* .search-center {
  margin: auto 0;
  width: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 12px;
  box-sizing: border-box;
} */

/* 검색창 감싸는 영역 */
.search-center {
  margin: auto 0;
  width: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 16px;
  box-sizing: border-box;
  transition: all 0.3s ease;
}
.search-panel.compact .search-center {
  margin: 12px 0;
  align-items: stretch;
  padding: 12px;
}

/* 패널 제목 */
/* .panel-title {
  margin: 0 0 12px 0;
  font-size: 18px;
  text-align: center;
} */
.panel-title {
  margin: 0 0 16px 0;
  font-size: 20px;
  font-weight: 700;
  color: #102a43;
  text-align: center;
}
.search-panel.compact .panel-title {
  font-size: 16px;
  margin-bottom: 8px;
  text-align: left;
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
  /* padding: 6px 8px; */
  padding: 11px 14px;
  border: 1px solid #d9e2ec;
  border-radius: 8px;
  font-size: 14px;
  color: #102a43;
  background-color: #fff;
  box-sizing: border-box;
  transition: all 0.2s ease;
}.controls input:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.15);
}
.controls input::placeholder {
  color: #788fa7;
  font-size: 13px;
  font-weight: 400;
}
/* 검색 버튼 */
.controls button {
  padding: 0 20px;
  background: #3b82f6;
  color: white;
  border: none;
  border-radius: 8px;
  font-weight: 700;
  font-size: 14px;
  cursor: pointer;
  white-space: nowrap;
  box-shadow: 0 2px 6px rgba(59, 130, 246, 0.2);
  transition: background 0.2s, transform 0.1s, opacity 0.2s;
}
.controls button:hover:not(:disabled) {
  background: #2563eb;
  transform: translateY(-1px);
}
.controls button:active:not(:disabled) {
  transform: translateY(0);
}
.controls button:disabled {
  background: #bcccdc;
  color: #f0f4f8;
  cursor: not-allowed;
  box-shadow: none;
}

.suggestions {
  position: absolute;
  top: calc(100% + 6px);
  left: 0;
  right: 0;
  background: #fff;
  border: 1px solid #e6e6e6;
  border-radius: 8px;
  max-height: 220px;
  overflow: auto;
  z-index: 30;
  list-style: none;
  margin: 0;
  padding: 6px 0;
  /* box-shadow: 0 6px 18px rgba(0, 0, 0, 0.08); */
  box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1), 0 8px 10px -6px rgba(0, 0, 0, 0.05);
}
.suggestions li {
  padding: 10px 14px;
  font-size: 13px;
  color: #334e68;
  cursor: pointer;
  transition: background 0.15s ease;
}

.suggestions li:hover,
.suggestions li.highlighted {
  background: #f0f7ff;
  color: #2563eb;
  font-weight: 600;
}
/* 게시글 헤더 */
.posts-header {
  display: flex;
  justify-content: space-between; /* 제목은 왼쪽 끝, 버튼은 오른쪽 끝으로 밀어냄 */
  align-items: center;            /* 세로 기준 정중앙 정렬 */
  margin: 12px 0 8px 0;
}
.posts-title {
  /* margin: 8px 0; */
  font-size: 16px;
  font-weight: 700;
  color: #102a43;
}
.write-btn {
  background: #3b82f6; /* 부드러운 파란색 */
  border: none;
  border-radius: 50%;   /* 동그란 모양 */
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  box-shadow: 0 2px 6px rgba(59, 130, 246, 0.3);
  transition: background 0.15s ease, transform 0.1s ease;
}
.write-btn:hover {
  background: #2563eb; /* 호버 시 조금 더 어두운 파란색 */
  transform: scale(1.05); /* 살짝 커지는 효과 */
}
.write-icon {
  font-size: 14px;
  color: white;
}

/* 게시글 노출 영역 */
.posts-wrap {
  padding: 8px 12px;
  border-top: 1px solid #eee;

  flex: 1;               /* 검색창을 제외한 남은 세로 공간을 전부 차지합니다 */
  min-height: 0;         /* flex 안에서 스크롤이 정상 작동하기 위한 CSS 필수 트릭 */
  /* overflow-y: auto;      세로로 내용이 넘치면 이 영역에만 스크롤바를 만듭니다 */
  display: flex;
  flex-direction: column; /*자식 요소들을 세로로 배치*/
}
/* 게시물 없을 때 */
.no-posts {
  padding: 24px 12px;
  color: #627d98;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  font-size: 14px;
  flex: 1;
}
.no-posts button {
  background: #3b82f6;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 6px;
  font-weight: 700;
  cursor: pointer;
  transition: background 0.2s;
}
.no-posts button:hover {
  background: #2563eb;
}

.posts-list {
  list-style: none;
  padding: 0;
  margin: 0;

  flex: 1;               /* 남은 세로 공간을 전부 차지 */
  overflow-y: auto; /* 세로로 내용이 넘치면 이 영역에만 스크롤바*/
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
/* 검색 결과 리스트 */
.results {
  list-style: none;
  padding: 0;
  margin: 8px 0 0 0;
  overflow: auto;
  flex: 1;
}
.results li {
  padding: 12px;
  border-bottom: 1px solid #f0f4f8;
  cursor: pointer;
  transition: background 0.2s;
}
.results li:hover {
  background: #f8fafc;
}
.results li.active {
  background: #f0f8ff;
}
.title {
  font-weight: 700;
  color: #102a43;
}
.addr {
  font-size: 12px;
  color: #627d98;
  margin-top: 4px;
}
.loading {
  font-style: italic;
  color: #627d98;
  margin: 12px;
  font-size: 14px;
  text-align: center;
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
.chat-toggle {
  margin-left: 8px;
  background: #06b6d4;
  color: #fff;
  border: none;
  padding: 8px 12px;
  border-radius: 6px;
  cursor: pointer;
}
.chat-toggle:disabled { opacity: 0.6; cursor: not-allowed; }


/* 편집, 삭제 아이콘 */
.actions {
  display: inline-flex;
  gap: 6px;
  align-items: center;
  margin-left: 8px;
}
.icon-btn {
  background: transparent;
  border: none;
  padding: 6px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  border-radius: 6px;
  transition: transform 0.08s ease, opacity 0.12s ease, filter 0.12s ease;
  filter: grayscale(100%);
  opacity: 0.85;
}
.icon-btn:hover {
  filter: grayscale(0%);
  opacity: 1;
  transform: translateY(-1px);
}
.icon-btn svg { display:block; }
.icon-btn.delete:hover svg { /* optional: red on hover */ fill: #dc2626; }
</style>
