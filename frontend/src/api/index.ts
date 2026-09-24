import axios, { AxiosInstance } from 'axios'

const API_BASE_URL = '/api'

const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  withCredentials: true,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor
apiClient.interceptors.request.use(
  (config) => {
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      console.error('Unauthorized')
    }
    return Promise.reject(error)
  }
)

// Types
export interface User {
  id: number
  steam_id: string
  persona_name?: string
  avatar_url?: string
  profile_url?: string
}

export interface Game {
  id: number
  user_id: number
  app_id: number
  name: string
  playtime_forever: number
  playtime_2weeks?: number
  img_icon_url?: string
  img_logo_url?: string
}

export interface PlayerStatus {
  user_id: number
  steam_id: string
  persona_name: string
  avatar_url?: string
  profile_url?: string
  persona_state: number
  is_in_game: boolean
  game_id?: string
  game_name?: string
}

export interface ImportGamesResponse {
  games_added: number
  games_updated: number
  games_removed: number
}

// Auth API
export const authApi = {
  getSteamLoginUrl: () => {
    return apiClient.get<{ login_url: string }>('/auth/steam/login')
  },

  getMe: () => apiClient.get<User>('/auth/me'),
  logout: () => apiClient.post('/auth/logout'),
}

// Games API
export const gamesApi = {
  importGames: (userId: number) => {
    return apiClient.post<ImportGamesResponse>(`/games/import/${userId}`)
  },

  getGames: (userId: number) => {
    return apiClient.get<Game[]>(`/games/${userId}`)
  },
}

// Status API
export const statusApi = {
  getPlayerStatus: (userId: number) => {
    return apiClient.get<PlayerStatus>(`/status/${userId}`)
  },
}

export default apiClient
