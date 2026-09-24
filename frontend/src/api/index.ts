import axios, { AxiosInstance } from 'axios'

const API_BASE_URL = '/api'

const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
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

// Auth API
export const authApi = {
  getSteamLoginUrl: async () => {
    const { data } = await apiClient.get<{ login_url: string }>('/auth/steam/login')
    return data.login_url
  },

  handleCallback: async (params: URLSearchParams) => {
    const { data } = await apiClient.get('/auth/steam/callback', {
      params: Object.fromEntries(params),
    })
    return data
  },
}

// Games API
export const gamesApi = {
  importGames: async (userId: number) => {
    const { data } = await apiClient.post(`/games/import/${userId}`)
    return data
  },

  getGames: async (userId: number) => {
    const { data } = await apiClient.get(`/games/${userId}`)
    return data
  },
}

// Status API
export const statusApi = {
  getPlayerStatus: async (userId: number) => {
    const { data } = await apiClient.get(`/status/${userId}`)
    return data
  },
}

export default apiClient
