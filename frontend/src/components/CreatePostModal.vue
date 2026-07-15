<template>
  <div class="modal-backdrop" @click.self="onClose" role="dialog" aria-modal="true">
    <div class="modal">
      <h3>새 게시글 작성</h3>
      <label><div>제목</div><input v-model="title" /></label>
      <label><div>본문</div><textarea v-model="content" rows="6" /></label>
      <label><div>비밀번호</div><input v-model="pwd" type="password" /></label>
      <div class="actions">
        <button @click="onClose" :disabled="saving">취소</button>
        <button @click="onSave" :disabled="saving || !canSave">{{ saving ? '저장중…' : '저장' }}</button>
      </div>
      <div v-if="error" class="error">{{ error }}</div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
const props = defineProps<{ show: boolean; place_id?: string | null }>()
const emit = defineEmits<{ (e: 'close'): void; (e: 'save', payload: { post_title: string; post_contents: string; post_pwd: string; place_id?: string | null }): void }>()
const title = ref(''), content = ref(''), pwd = ref(''), saving = ref(false), error = ref('')
const canSave = computed(() => title.value.trim() && content.value.trim() && pwd.value.trim())
function onClose() { if (!saving.value) emit('close') }
function onSave() { if (!canSave.value) return; saving.value = true; emit('save', { post_title: title.value.trim(), post_contents: content.value.trim(), post_pwd: pwd.value.trim(), place_id: props.place_id ?? null }); saving.value = false }
</script>

<style scoped>
/* reuse styles similar to EditPostModal.vue; adjust z-index if needed */
.modal-backdrop { position: fixed; inset:0; display:flex;align-items:center;justify-content:center; background: rgba(8,12,20,0.45); z-index:10000; }
.modal { background:#fff; padding:16px; border-radius:8px; z-index:10001; max-width:520px; width:100%; }
</style>