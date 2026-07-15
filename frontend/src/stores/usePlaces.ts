import { defineStore } from 'pinia'
import { ref } from 'vue'
import { fetchPlaceById, fetchPostsByPlace, fetchPostsByPlaceKeyword } from '../services/api'

import type { ApiPostListItem } from '../services/api'

export type Place = {
  id: string
  name: string
  addr?: string
  latitude: number
  longitude: number
}

export const usePlaces = defineStore('places', () => {
  const searchText = ref('')
  const places = ref<Place[]>([])
  const selected = ref<Place | null>(null)
  const posts = ref<ApiPostListItem[]>([])
  const loading = ref(false)

  async function search(q?: string) {
    const query = (q ?? searchText.value).trim()
    if (!query) {
      places.value = []
      selected.value = null
      posts.value = []
      return
    }
    loading.value = true
    try {
      const res = await fetchPostsByPlaceKeyword(query)
      console.log('search result', res)
      posts.value = res.posts ?? []

      if (res.place) {
        places.value = Array.isArray(res.place) ? res.place : [res.place]
        selected.value = places.value[0] ?? null
      } else {
        places.value = []
        selected.value = null
      }
    } finally {
      loading.value = false
    }
  }

  // function selectPlace(p: Place) {
  //   selected.value = p
  // }
  async function selectPlace(p: Place) {
    selected.value = p
    loading.value = true
    try {
      posts.value = await fetchPostsByPlace(p.id)
    } finally {
      loading.value = false
    }
  }


  return { searchText, places, selected, posts, loading, search, selectPlace }
})
