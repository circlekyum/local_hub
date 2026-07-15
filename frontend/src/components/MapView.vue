<template>
  <div ref="mapEl" class="map-root"></div>
</template>

<script setup lang="ts">
import { onMounted, ref, watch, onBeforeUnmount } from 'vue'
import L from 'leaflet'
import markerUrl from 'leaflet/dist/images/marker-icon.png'
import markerShadow from 'leaflet/dist/images/marker-shadow.png'
import { usePlaces } from '../stores/usePlaces'

// 마커 아이콘 전역 설정 (한 번만 실행되므로 유지)
L.Marker.prototype.options.icon = L.icon({
  iconUrl: markerUrl,
  shadowUrl: markerShadow,
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41],
})

const mapEl = ref<HTMLDivElement | null>(null)
let map: L.Map | null = null
let markersLayer: L.LayerGroup | null = null

const store = usePlaces()

// 리사이즈 핸들러는 컴포넌트 스코프에 선언하여 온마운트/언마운트 시점에 안전하게 참조하도록 합니다.
const onResize = () => {
  if (map) {
    map.invalidateSize()
  }
}

onMounted(() => {
  if (!mapEl.value) return

  // 1. 지도 인스턴스 생성
  map = L.map(mapEl.value).setView([37.5665, 126.978], 12)
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; OpenStreetMap contributors',
  }).addTo(map)

  markersLayer = L.layerGroup().addTo(map)

  // 처음 마커들을 한번 그려줍니다.
  renderMarkers()

  // 2. 레이아웃 갱신 처리 (double rAF & setTimeout)
  requestAnimationFrame(() => {
    requestAnimationFrame(() => {
      map?.invalidateSize()
    })
  })

  setTimeout(() => {
    map?.invalidateSize()
  }, 300)

  // 3. 리사이즈 이벤트 바인딩
  window.addEventListener('resize', onResize)
})

// 마커 렌더링 함수
function renderMarkers() {
  if (!markersLayer) return
  markersLayer.clearLayers()

  for (const p of store.places) {
    const m = L.marker([p.latitude, p.longitude]).addTo(markersLayer)
    m.bindPopup(`<strong>${p.name}</strong><div style="font-size:12px">${p.addr ?? ''}</div>`)
    m.on('click', () => store.selectPlace(p))
  }

  if (store.selected && map) {
    map.flyTo([store.selected.latitude, store.selected.longitude], 15)
  }
}

// Watchers
watch(
  () => store.places.slice(),
  () => {
    renderMarkers()
  },
)

watch(
  () => store.selected,
  (n) => {
    if (n && map) {
      map.flyTo([n.latitude, n.longitude], 15)
    }
  },
)

// 4. 단 하나의 통합된 clean-up 단계
onBeforeUnmount(() => {
  // 윈도우 리사이즈 이벤트 제거
  window.removeEventListener('resize', onResize)

  // Leaflet 인스턴스 안전하게 제거 및 가비지 컬렉션 유도
  if (map) {
    map.remove()
    map = null
  }
  markersLayer = null
})
</script>

<style scoped>
.map-root {
  width: 100%;
  height: 100%;
  min-height: 100%;
}
</style>
