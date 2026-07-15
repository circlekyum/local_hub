import { defineStore } from 'pinia'
import { ref } from 'vue'
import { fetchPlaces } from '../services/api'

export type Place = {
  id: string
  name: string
  addr?: string
  lat: number
  lng: number
}

export const usePlaces = defineStore('places', () => {
  const searchText = ref('')
  const places = ref<Place[]>([])
  const selected = ref<Place | null>(null)
  const loading = ref(false)

  async function search(q?: string) {
    const query = (q ?? searchText.value).trim()
    if (!query) {
      places.value = []
      selected.value = null
      return
    }
    loading.value = true
    try {
      const res = await fetchPlaces(query)
      places.value = res
      // 검색 후 첫 결과가 있으면 자동 선택(지도 줌인 트리거)
      selected.value = res.length > 0 ? res[0] : null
    } finally {
      loading.value = false
    }
  }

  function selectPlace(p: Place) {
    selected.value = p
  }

  return { searchText, places, selected, loading, search, selectPlace }
})
