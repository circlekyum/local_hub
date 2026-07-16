<template>
  <section class="chat-panel" role="dialog" aria-label="챗봇">
    <header class="chat-header">
      <h4>지역정보 챗봇</h4>
      <button class="close" @click="$emit('close')">×</button>
    </header>

    <div class="chat-body" ref="bodyEl">
      <div v-for="(m, i) in messages" :key="i" :class="['msg', m.role]">
        <div class="bubble">{{ m.text }}</div>
      </div>
    </div>

    <form class="chat-input" @submit.prevent="send">
      <input v-model="q" placeholder="질문을 입력하세요. 예: '서울 벚꽃 명소 알려줘'" />
      <button type="submit" :disabled="sending">전송</button>
    </form>
  </section>
</template>

<script setup lang="ts">
import { ref, nextTick } from 'vue'
import { postChat } from '../services/api'

const emit = defineEmits<{
  (e: 'close'): void
}>()

const q = ref('')
const sending = ref(false)
const messages = ref<{ role: 'user' | 'bot'; text: string }[]>([])

const bodyEl = ref<HTMLElement | null>(null)
function scrollBottom() {
  nextTick(() => {
    if (bodyEl.value) bodyEl.value.scrollTop = bodyEl.value.scrollHeight
  })
}

async function send() {
  const text = q.value.trim()
  if (!text) return
  messages.value.push({ role: 'user', text })
  q.value = ''
  scrollBottom()
  sending.value = true
  try {
    const res = await postChat(text)
    messages.value.push({ role: 'bot', text: res.answer ?? '응답이 없습니다.' })
  } catch (err) {
    messages.value.push({ role: 'bot', text: '서버 요청 중 오류가 발생했습니다.' })
    console.error(err)
  } finally {
    sending.value = false
    scrollBottom()
  }
}
</script>

<style scoped>
.chat-panel {
  position: absolute;
  right: 12px;
  top: 12px;
  width: 360px;
  height: 560px;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 12px 40px rgba(16, 32, 56, 0.25);
  display: flex;
  flex-direction: column;
  z-index: 1200;
  overflow: hidden;
}
.chat-header {
  display:flex;
  align-items:center;
  justify-content:space-between;
  padding:12px 16px;
  border-bottom:1px solid #eef2f6;
  background:#f8fafc;
}
.chat-body {
  flex:1;
  padding:12px;
  overflow:auto;
  background: linear-gradient(#f7fbff, #fff);
}
.msg { margin:8px 0; display:flex; }
.msg.user { justify-content:flex-end; }
.msg.bot { justify-content:flex-start; }
.bubble {
  max-width:80%;
  padding:8px 12px;
  border-radius:12px;
  background:#e6f5ff;
  color:#02263a;
}
.msg.user .bubble { background:#3b82f6; color:#fff; }
.chat-input { display:flex; gap:8px; padding:10px; border-top:1px solid #eef2f6; }
.chat-input input { flex:1; padding:8px 10px; border:1px solid #dbe7f0; border-radius:8px; }
.chat-input button { padding:8px 12px; background:#06b6d4; color:#fff; border:none; border-radius:8px; }
.close { border:none; background:transparent; font-size:18px; cursor:pointer; }
</style>