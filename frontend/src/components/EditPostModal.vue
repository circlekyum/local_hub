<template>
  <div class="modal-backdrop" @click.self="onClose" role="dialog" aria-modal="true">
    <div class="modal">
      <h3 class="modal-title">게시글 수정</h3>

      <label class="field">
        <div class="label">제목</div>
        <input v-model="title" type="text" :disabled="saving" />
      </label>

      <label class="field">
        <div class="label">본문</div>
        <textarea v-model="content" rows="6" :disabled="saving" />
      </label>

      <label class="field">
        <div class="label">비밀번호</div>
        <input v-model="pwd" type="password" :disabled="saving" />
      </label>

      <div class="actions">
        <button class="btn secondary" @click="onClose" :disabled="saving">취소</button>
        <button class="btn primary" @click="onSave" :disabled="saving || !canSave">
          <span v-if="!saving">저장</span>
          <span v-else>저장중…</span>
        </button>
      </div>

      <div v-if="error" class="error">{{ error }}</div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, computed } from 'vue'

interface PostProps {
  post_id: string
  post_title: string
  contents: string
  place_id?: string
}

const props = defineProps<{
  show: boolean
  post: PostProps | null
}>()

const emit = defineEmits<{
  (e: 'close'): void
  (e: 'save', payload: { post_id: string; post_title: string; post_contents: string; post_pwd: string }): void
}>()

const title = ref('')
const content = ref('')
const pwd = ref('')
const saving = ref(false)
const error = ref('')

watch(
  () => props.post,
  (p) => {
    title.value = p?.post_title ?? ''
    content.value = p?.contents ?? ''
    pwd.value = ''
    error.value = ''
  },
  { immediate: true }
)

const canSave = computed(() => title.value.trim().length > 0 && content.value.trim().length > 0 && pwd.value.trim().length > 0)

function onClose() {
  if (!saving.value) emit('close')
}

async function onSave() {
  if (!canSave.value) return
  error.value = ''
  saving.value = true
  try {
    emit('save', {
      post_id: props.post!.post_id,
      post_title: title.value.trim(),
      post_contents: content.value.trim(),
      post_pwd: pwd.value.trim(),
    })
  } catch (e: any) {
    error.value = e?.message ?? '저장 중 오류가 발생했습니다.'
  } finally {
    saving.value = false
  }
}
</script>

<style scoped>
.modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(8, 12, 20, 0.45);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}
.modal {
  width: 100%;
  max-width: 520px;
  background: #ffffff;
  border-radius: 12px;
  padding: 20px;
  box-sizing: border-box;
  box-shadow: 0 18px 48px rgba(2, 6, 23, 0.32);
  color: #102a43;
}

/* 제목 */
.modal-title {
  margin: 0 0 14px 0;
  font-weight: 800;
  font-size: 18px;
  color: #102a43;
}
/* 필드 레이아웃 */
.field {
  margin-bottom: 12px;
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.label {
  font-size: 13px;
  color: #616e7c;
  font-weight: 600;
}
/* 입력창 공통 스타일 (글쓰기 폼과 통일) */
/* input, textarea { padding:10px; border:1px solid #e3e8ef; border-radius:6px; font-size:14px; } */
input[type="text"],
input[type="password"],
textarea {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #d9e2ec;
  border-radius: 8px;
  font-size: 14px;
  color: #102a43;
  background-color: #fff;
  transition: all 0.16s ease;
  box-sizing: border-box;
  resize: vertical;
}
/* 포커스 효과 */
input[type="text"]:focus,
input[type="password"]:focus,
textarea:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 4px rgba(59, 130, 246, 0.10);
}
/* 플레이스홀더 스타일을 글쓰기 폼과 통일 */
input::placeholder,
textarea::placeholder {
  font-family: 'Nanum Gothic', sans-serif;
  color: #788fa7;
  font-size: 13px;
  font-weight: 400;
}
/* 액션 버튼 */
.actions {
  display: flex;
  gap: 10px;
  justify-content: flex-end;
  margin-top: 8px;
}
.btn {
  padding: 9px 14px;
  border-radius: 8px;
  border: none;
  cursor: pointer;
  font-weight: 700;
  font-size: 14px;
}
.btn.secondary {
  background: #f0f4f8;
  color: #102a43;
}
.btn.primary {
  background: #3b82f6;
  color: #ffffff;
}
.btn.primary:hover {
  background: #2563eb;
}

/* 에러 메세지 강조 */
.error {
  margin-top: 10px;
  color: #b91c1c;
  font-size: 13px;
  background: rgba(185, 28, 28, 0.06);
  padding: 8px 10px;
  border-radius: 6px;
}

/* 반응형 여백 보정 */
@media (max-width: 520px) {
  .modal {
    margin: 16px;
  }
}
</style>