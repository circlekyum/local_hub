import type { Place } from '../stores/usePlaces'
const API_BASE = (import.meta.env.VITE_API_BASE as string) || ''

// export async function fetchPlaces(query: string): Promise<Place[]> {
//   await new Promise((r) => setTimeout(r, 200))

//   const q = query.trim().toLowerCase()
//   const lookup: Record<string, Place> = {
//     광화문: { id: 'gwanghwamun', name: '광화문', addr: '서울 종로구', lat: 37.5759, lng: 126.9768 },
//     경복궁: {
//       id: 'gyeongbokgung',
//       name: '경복궁',
//       addr: '서울 종로구',
//       lat: 37.5796,
//       lng: 126.977,
//     },
//     롯데타워: { id: 'lotte', name: '롯데타워', addr: '서울 송파구', lat: 37.5131, lng: 127.1025 },
//     여의도: { id: 'yeouido', name: '여의도', addr: '서울 영등포구', lat: 37.526, lng: 126.9247 },
//     남산타워: { id: 'namsan', name: '남산타워', addr: '서울 용산구', lat: 37.5512, lng: 126.9882 },
//     북촌한옥마을: {
//       id: 'bukchon',
//       name: '북촌한옥마을',
//       addr: '서울 종로구',
//       lat: 37.5826,
//       lng: 126.983,
//     },
//     명동: { id: 'myeongdong', name: '명동', addr: '서울 중구', lat: 37.5609, lng: 126.985 },
//     인사동: { id: 'insadong', name: '인사동', addr: '서울 종로구', lat: 37.572, lng: 126.985 },
//     홍대: { id: 'hongdae', name: '홍대', addr: '서울 마포구', lat: 37.5563, lng: 126.9239 },
//     강남역: { id: 'gangnam', name: '강남역', addr: '서울 강남구', lat: 37.4979, lng: 127.0276 },
//     청계천: { id: 'cheonggye', name: '청계천', addr: '서울 종로구', lat: 37.5683, lng: 126.9779 },
//     동대문: { id: 'dongdaemun', name: '동대문', addr: '서울 중구', lat: 37.5663, lng: 127.009 },
//     이태원: { id: 'itaewon', name: '이태원', addr: '서울 용산구', lat: 37.5345, lng: 126.9947 },
//   }

//   if (lookup[q]) return [lookup[q]]

//   // 기본 더미 응답 (키워드가 매칭되지 않을 때)
//   return [
//     { id: '1', name: `${query} 관광지 A`, addr: '서울시 중구', lat: 37.5665, lng: 126.978 },
//     { id: '2', name: `${query} 관광지 B`, addr: '서울시 종로구', lat: 37.572, lng: 126.9794 },
//     { id: '3', name: `${query} 카페 C`, addr: '서울시 강남구', lat: 37.4979, lng: 127.0276 },
//   ]
// }

export async function fetchPlaceById(placeId: string): Promise<Place> {
  const url = `${API_BASE}/api/places/${encodeURIComponent(placeId)}`
  const res = await fetch(url)
  if (!res.ok) throw new Error(`API error ${res.status}`)
  const p = await res.json()

  return {
    id: p.id,
    name: p.name ?? '',
    addr: p.address ?? p.region ?? '',
    latitude: p.latitude ?? 0,
    longitude: p.longitude ?? 0,
  } as Place
}

export type ApiPostListItem = {
  id: number
  title: string
  created_at: string
}

export async function fetchPostsByPlace(placeId: string): Promise<ApiPostListItem[]> {
  const url = `${API_BASE}/api/posts/by_place/${encodeURIComponent(placeId)}`
  const res = await fetch(url)
  if (!res.ok) throw new Error(`API error ${res.status}`)
  return (await res.json()) as ApiPostListItem[]
}

export async function fetchPostById(postId: number) {
  const url = `${API_BASE}/api/posts/${postId}`
  const res = await fetch(url)
  if (!res.ok) throw new Error(`API error ${res.status}`)
  return await res.json()
}

// 편의: 키워드로 place_id + posts 반환하는 백엔드 엔드포인트 사용
export async function fetchPostsByPlaceKeyword(keyword: string) {
  const params = new URLSearchParams({ keyword: keyword ?? '' })
  const url = `${API_BASE}/api/posts/by_place_keyword?${params.toString()}`
  const res = await fetch(url)
  if (!res.ok) throw new Error(`API error ${res.status}`)
  return await res.json() // { place_id: string | null, posts: PostListItem[] }
}