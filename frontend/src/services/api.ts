import type { Place } from '../stores/usePlaces'

export async function fetchPlaces(query: string): Promise<Place[]> {
  await new Promise((r) => setTimeout(r, 300)) // 모의 지연
  const sample: Place[] = [
    { id: '1', name: `${query} 관광지 A`, addr: '서울시 중구', lat: 37.5665, lng: 126.978 },
    { id: '2', name: `${query} 관광지 B`, addr: '서울시 종로구', lat: 37.572, lng: 126.9794 },
    { id: '3', name: `${query} 카페 C`, addr: '서울시 강남구', lat: 37.4979, lng: 127.0276 },
  ]
  return sample
}
