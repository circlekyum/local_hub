<script setup lang="ts">
import SearchPanel from './components/SearchPanel.vue'
import MapView from './components/MapView.vue'
</script>

<template>
  <div class="app-layout">
    <aside class="left"><SearchPanel /></aside>
    <main class="right"><MapView /></main>
  </div>
</template>

<!-- <style>
.app-layout {
  display: flex;
  height: 100vh;
}
.left {
  width: 30%;
  min-width: 280px;
  overflow: auto;
}
.right {
  flex: 1;
  min-height: 0;
  position: relative;
}
</style> -->

<style>
.app-layout {
  display: flex;
  height: 100vh;
  width: 100vw; /* 전체 화면 너비를 명시 */
  overflow: hidden; /* 스크롤 바 방지 */
}
.left {
  width: 30%;
  min-width: 280px;
  overflow: auto;
}
.right {
  flex: 1;
  min-width: 0; /* ★ 핵심: Flex 자식이 너비를 0에서부터 유연하게 채우도록 설정 */
  height: 100%; /* 높이도 부모(100vh)를 꽉 채우도록 설정 */
  position: relative;
}
</style>
