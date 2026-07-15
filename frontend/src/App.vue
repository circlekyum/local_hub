<script setup lang="ts">
import { ref } from 'vue'
import SearchPanel from './components/SearchPanel.vue'
import MapView from './components/MapView.vue'

interface Post {
  post_id: string
  post_title: string
  date: string
  contents: string
  place_id?: string
}

const activePost = ref<Post | null>(null)

function openPost(p: Post) {
  // console.log('openPost received:', p)
  activePost.value = p
}
function closeDetail() {
  activePost.value = null
}
</script>

<template>
  <div class="app-layout">
    <aside class="left">
      <SearchPanel @open-post="openPost" />
    </aside>

    <main class="right">
      <MapView />

      <!-- 상세 패널: 왼쪽 검색창 바로 오른쪽, 지도 위에 떠 있도록 절대 위치 -->
      <transition name="slide">
        <section v-if="activePost" class="post-detail">
          <button class="close" @click="closeDetail">×</button>
          <h3 class="title">{{ activePost.post_title }}</h3>
          <div class="date">{{ activePost.date }}</div>
          <div class="body">{{ activePost.contents }}</div>
        </section>
      </transition>
    </main>
  </div>
</template>

<style scoped>
.app-layout {
  display: flex;
  width: 100vw;
  height: 100vh;
  overflow: hidden;
}

/* 왼쪽 검색 패널 고정 너비 */
.left {
  width: 40%;
  min-width: 300px;
  max-width: 500px;
  height: 100%;
  background: #fff;
  box-shadow: 2px 0 8px rgba(0, 0, 0, 0.12);
  z-index: 20;
  overflow-y: auto;
}

/* 오른쪽(지도) 영역은 상대 위치 유지 */
.right {
  flex: 1;
  position: relative;
  height: 100%;
  min-width: 0;
}

/* 상세 패널: .right 내부에서 절대 위치, 검색창 바로 오른쪽(왼쪽 패널과 맞닿는 지점 근처) */
.post-detail {
  position: absolute;
  left: 12px; /* .right의 왼쪽에서 약간 떨어진 위치 -> 검색창 바로 오른쪽 느낌 */
  top: 12px;
  width: 380px;
  max-width: calc(100% - 24px);
  height: auto;
  background: rgba(255, 255, 255, 0.98);
  border-left: 1px solid #e6e6e6;
  border-radius: 6px;
  padding: 16px;
  box-shadow: 0 8px 28px rgba(0, 0, 0, 0.18);
  z-index: 1000;
}

/* 애니메이션 */
.slide-enter-from {
  transform: translateY(-6px);
  opacity: 0;
}
.slide-enter-active {
  transition: all 0.18s ease;
}
.slide-leave-to {
  transform: translateY(-6px);
  opacity: 0;
}
.slide-leave-active {
  transition: all 0.14s ease;
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

.title {
  margin-top: 0;
}
.body {
  margin-top: 10px;
  white-space: pre-wrap;
}
</style>
