<template>
  <div ref="mapEl" class="map-root"></div>
</template>

<script setup lang="ts">
import { onMounted, ref, watch, onBeforeUnmount } from 'vue'
import L from 'leaflet'
import markerUrl from 'leaflet/dist/images/marker-icon.png'
import markerShadow from 'leaflet/dist/images/marker-shadow.png'
import { usePlaces } from '../stores/usePlaces'

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

onMounted(() => {
  map = L.map(mapEl.value as HTMLElement).setView([37.5665, 126.978], 12)
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; OpenStreetMap contributors',
  }).addTo(map)
  markersLayer = L.layerGroup().addTo(map)
  // 브라우저가 완전히 레이아웃을 계산하고 화면을 그린(Render) 직후에 실행되도록 보장합니다.
  requestAnimationFrame(() => {
    requestAnimationFrame(() => {
      if (map) {
        map.invalidateSize()
      }
    })
  })

  // 혹시 모를 CSS 트랜지션(애니메이션) 지연에 대비해 300ms 뒤에 한 번 더 맞춰줍니다.
  setTimeout(() => {
    if (map) {
      map.invalidateSize()
    }
  }, 300)
  // ------------------ [여기까지 수정] ------------------

  // 윈도우 리사이즈 시에도 invalidate
  const onResize = () => {
    map?.invalidateSize()
  }
  window.addEventListener('resize', onResize)

  // 컴포넌트 종료 때 이벤트 제거
  onBeforeUnmount(() => {
    window.removeEventListener('resize', onResize)
    if (map) map.remove()
  })
})

function renderMarkers() {
  if (!markersLayer) return
  markersLayer.clearLayers()
  for (const p of store.places) {
    const m = L.marker([p.lat, p.lng]).addTo(markersLayer)
    m.bindPopup(`<strong>${p.name}</strong><div style="font-size:12px">${p.addr ?? ''}</div>`)
    m.on('click', () => store.selectPlace(p))
  }
  if (store.selected && map) {
    map.flyTo([store.selected.lat, store.selected.lng], 15)
    L.popup()
  }
}

watch(
  () => store.places.slice(),
  () => {
    renderMarkers()
  },
)

watch(
  () => store.selected,
  (n) => {
    if (n && map) map.flyTo([n.lat, n.lng], 15)
  },
)

onBeforeUnmount(() => {
  if (map) map.remove()
})
</script>

<style scoped>
.map-root {
  width: 100%;
  height: 100%;
  min-height: 100%;
}
</style>
