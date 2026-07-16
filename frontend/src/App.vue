<script setup lang="ts">
import { ref } from 'vue'
import SearchPanel from './components/SearchPanel.vue'
import MapView from './components/MapView.vue'
import { usePlaces } from './stores/usePlaces' // 🌟 장소 데이터를 연동하기 위해 store 가져옴
import ChatPanel from './components/ChatPanel.vue'

const isChatOpen = ref(false)
function openChat() { isChatOpen.value = true }
function closeChat() { isChatOpen.value = false }
// post 관련
import EditPostModal from './components/EditPostModal.vue'
import CreatePostModal from './components/CreatePostModal.vue'
import { updatePost, createPost, fetchPostById } from './services/api' // fetchPostById for edit

import { onMounted } from 'vue'
// import { fetchAllPlaces } from './services/api'

interface Post {
  post_id: string
  post_title: string
  date: string
  contents: string
  place_id?: string
}

const store = usePlaces() // 🌟 선택된 장소(selected)를 가져오기 위한 스토어 연결
const activePost = ref<Post | null>(null)
const isWriting = ref(false) // 🌟 글쓰기 창 띄우기용 상태값

// 글쓰기 폼 데이터
const writeForm = ref({
  title: '',
  contents: '',
  password: ''
})

// onMounted(async () => {
//   try {
//     const all = await fetchAllPlaces()
//     store.places = all
//     console.log('all places loaded', all)
//   } catch (e) {
//     console.error('all places load failed', e)
//   }
// })

// 게시글 상세 열기
function openPost(p: Post) {
  isWriting.value = false // 글쓰기 창은 닫아줌
  activePost.value = p
}

function closeDetail() {
  activePost.value = null
}

// 🌟 글 작성 패널 열기
function openCreate() {
  activePost.value = null // 상세보기 창은 닫아줌
  // 폼 초기화
  writeForm.value = { title: '', contents: '', password: '' }
  isWriting.value = true
}
function closeWrite() {
  isWriting.value = false
}

// 🌟 저장하기 버튼 클릭 시 동작 (지금은 테스트용 로직)
// function handleSave() {
//   alert(`저장되었습니다!\n장소: ${store.selected?.name || '선택 없음'}\n제목: ${writeForm.value.title}`)
//   isWriting.value = false
// }
async function handleSave() {
  const payload = {
    post_title: writeForm.value.title,
    post_contents: writeForm.value.contents,
    post_pwd: writeForm.value.password,
    place_id: store.selected?.id ?? null
  }

  try {
    const res = await fetch('http://localhost:8000/api/posts', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    })

    if (res.status === 201) {
      const data = await res.json()
      isWriting.value = false
      alert('저장되었습니다.')
      // 필요하면 반환된 data를 사용해 UI 갱신 (예: 새로운 post id)
      console.log('created post:', data)
      // 저장 후 현재 선택된 장소 기준으로 게시물 목록을 갱신합니다.
      try {
        if (store.selected) {
          await store.selectPlace(store.selected)
        } else {
          // 선택된 장소가 없으면 현재 검색어로 재검색하여 목록 갱신
          await store.search()
        }
      } catch (err) {
        console.error('refresh posts error', err)
      }
    } else if (res.status === 422) {
      const err = await res.json()
      console.error(err)
      alert('입력값 오류: ' + JSON.stringify(err.errors))
    } else {
      const err = await res.json().catch(() => ({}))
      alert(err.detail || '저장에 실패했습니다.')
    }
  } catch (e) {
    console.error(e)
    alert('서버 요청 중 오류가 발생했습니다.')
  }
}

const showEditModal = ref(false)
const editingPost = ref(null as null | { post_id:string; post_title:string; contents:string; place_id?:string })
const showCreateModal = ref(false)

async function openEdit(post) {
  try {
    const id = Number(post.post_id ?? post.id)
    const detail = await fetchPostById(id)
    editingPost.value = {
      post_id: String(detail.id),
      post_title: detail.title || detail.post_title || '',
      contents: detail.content ?? detail.post_contents ?? '',
      place_id: detail.place_id ?? (store.selected?.id ?? undefined),
    }
    showEditModal.value = true
  } catch (err) {
    console.error('failed to load post detail for edit', err)
    alert('게시글 내용을 불러오지 못했습니다.')
  }
}

function onEditClose() {
  showEditModal.value = false
  editingPost.value = null
}

async function onEditSave(payload) {
  try {
    await updatePost(Number(payload.post_id), {
      post_title: payload.post_title,
      post_contents: payload.post_contents,
      post_pwd: payload.post_pwd,
    })
    // 갱신
    if (store.selected) await store.selectPlace(store.selected)
    else await store.search()
    alert('수정되었습니다.')
    onEditClose()
  } catch (e: any) {
    if (e?.status === 403) alert('비밀번호가 일치하지 않습니다.')
    else { console.error(e); alert('수정에 실패했습니다.') }
  }
}

function openCreateModal() {
  showCreateModal.value = true
}
function onCreateClose() { showCreateModal.value = false }

async function onCreateSave(payload) {
  try {
    await createPost({
      post_title: payload.post_title,
      post_contents: payload.post_contents,
      post_pwd: payload.post_pwd,
      place_id: payload.place_id ?? (store.selected?.id ?? null),
    })
    if (store.selected) await store.selectPlace(store.selected)
    else await store.search()
    alert('게시글이 등록되었습니다.')
    onCreateClose()
  } catch (e: any) {
    console.error(e)
    alert('등록에 실패했습니다.')
  }
}

</script>

<template>
  <div class="app-layout">
    <aside class="left">
      <SearchPanel @open-post="openPost" @open-create="openCreate" @open-chat="openChat" @request-edit="openEdit" />

      <!-- <SearchPanel @open-post="openPost" @open-create="openCreateModal" @open-chat="openChat" @request-edit="openEdit" /> -->

      <teleport to="body">
        <EditPostModal v-if="showEditModal" :show="showEditModal" :post="editingPost" @close="onEditClose" @save="onEditSave" />
        <CreatePostModal v-if="showCreateModal" :show="showCreateModal" :place_id="store.selected?.id ?? null" @close="onCreateClose" @save="onCreateSave" />
      </teleport>
    </aside>

    <main class="right">
      <MapView />

      <transition name="slide">
        <section v-if="activePost" class="post-detail">
          <button class="close" @click="closeDetail">×</button>
          <h3 class="title">{{ activePost.post_title }}</h3>
          <div class="date">{{ activePost.date }}</div>
          <div class="body">{{ activePost.contents }}</div>
        </section>
      </transition>

      <transition name="slide">
        <ChatPanel v-if="isChatOpen" @close="closeChat" />
      </transition>

      <transition name="slide">
        <section v-if="isWriting" class="post-detail write-panel">
          <button class="close" @click="closeWrite">×</button>
          <h3 class="title">새 글 쓰기</h3>
          
          <form @submit.prevent="handleSave" class="write-form">
            <div class="form-group">
              <label class="form-label">기록할 장소</label>
              <div class="place-badge">
                📍 {{ store.selected?.name || '먼저 장소를 검색 후 선택해 주세요' }}
              </div>
            </div>

            <div class="form-group">
              <input 
                v-model="writeForm.title" 
                type="text" 
                placeholder="제목을 입력하세요" 
                class="form-input" 
                required 
              />
            </div>

            <div class="form-group">
              <textarea 
                v-model="writeForm.contents" 
                placeholder="이 장소에 대한 추억이나 정보를 기록해 보세요." 
                class="form-textarea" 
                rows="6"
                required
              ></textarea>
            </div>

            <div class="form-group">
              <input 
                v-model="writeForm.password" 
                type="password" 
                placeholder="수정/삭제용 비밀번호 입력" 
                class="form-input" 
                required 
              />
            </div>

            <button type="submit" class="save-btn">기록하기</button>
          </form>
        </section>
      </transition>
    </main>
  </div>
</template>

<style scoped>
/* App.vue의 <style scoped> 맨 위에 추가 */
@import url('https://fonts.googleapis.com/css2?family=Nanum+Gothic:wght@400;700;800&display=swap');

/* 전체 화면 요소에 나눔고딕 적용 */
:deep(*) {
  font-family: 'Nanum Gothic', sans-serif;
}
/* --- 기존 스타일 코드는 그대로 유지합니다 --- */
.app-layout { display: flex; width: 100vw; height: 100vh; overflow: hidden; }
.left { width: 40%; min-width: 300px; max-width: 500px; height: 100%; background: #fff; box-shadow: 2px 0 8px rgba(0, 0, 0, 0.12); z-index: 20; overflow-y: auto; }
.right { flex: 1; position: relative; height: 100%; min-width: 0; }
.post-detail { position: absolute; left: 12px; top: 12px; width: 380px; max-width: calc(100% - 24px); height: auto; background: rgba(255, 255, 255, 0.98); border-left: 1px solid #e6e6e6; border-radius: 6px; padding: 16px; box-shadow: 0 8px 28px rgba(0, 0, 0, 0.18); z-index: 1000; }
.slide-enter-from { transform: translateY(-6px); opacity: 0; }
.slide-enter-active { transition: all 0.18s ease; }
.slide-leave-to { transform: translateY(-6px); opacity: 0; }
.slide-leave-active { transition: all 0.14s ease; }
.close { position: absolute; right: 8px; top: 8px; border: none; background: transparent; font-size: 20px; cursor: pointer; }
.title { margin-top: 0; color: #102a43; }
.body { margin-top: 10px; white-space: pre-wrap; }

/* 🌟 글쓰기 폼 전용 추가 CSS 스타일 */
.write-form {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-top: 16px;
}
.form-group {
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.form-label {
  font-size: 12px;
  font-weight: 600;
  color: #616e7c;
}
.place-badge {
  padding: 10px 12px;
  background: #f0f4f8;
  border-radius: 4px;
  font-size: 13px;
  color: #334e68;
  font-weight: bold;
}

/* 입력창 공통 스타일 스타일리시하게 변경 */
.form-input,
.form-textarea {
  padding: 10px 12px;
  border: 1px solid #d9e2ec;
  border-radius: 6px;
  font-size: 14px;
  color: #102a43;
  background-color: #fff;
  transition: all 0.2s ease;
}

/* 입력창 클릭(포커스) 시 부드러운 파란색 테두리 효과 */
.form-input:focus,
.form-textarea:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.15);
}

.form-input::placeholder,
.form-textarea::placeholder {
  font-family: 'Nanum Gothic', sans-serif;
  color: #788fa7;      /* 부드럽고 은은한 회색조로 변경 */
  font-size: 13px;     /* 본문보다 살짝 작게 */
  font-weight: 400;    /* 일반 두께 */
}

.save-btn {
  background: #3b82f6;
  color: white;
  border: none;
  padding: 10px;
  border-radius: 4px;
  font-weight: bold;
  cursor: pointer;
  transition: background 0.2s;
}
.save-btn:hover {
  background: #2563eb;
}
</style>