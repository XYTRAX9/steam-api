import { defineStore } from 'pinia'
import { ref } from 'vue'
import { authApi, gamesApi, statusApi, type User, type Game, type PlayerStatus } from '@/api'

export const useUserStore = defineStore('user', () => {
  const currentUser = ref<User | null>(null)
  const games = ref<Game[]>([])
  const playerStatus = ref<PlayerStatus | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)
  let sessionRequest: Promise<User | null> | null = null

  const loadCurrentUser = (): Promise<User | null> => {
    if (!sessionRequest) {
      sessionRequest = authApi.getMe()
        .then((response) => {
          currentUser.value = response.data
          return response.data
        })
        .catch((err) => {
          currentUser.value = null
          if (err.response?.status === 401) return null
          error.value = err.response?.data?.detail || 'Failed to load user session'
          throw err
        })
        .finally(() => {
          sessionRequest = null
        })
    }
    return sessionRequest
  }

  const logout = async () => {
    await authApi.logout()
    currentUser.value = null
    games.value = []
    playerStatus.value = null
  }

  const getSteamLoginUrl = async () => {
    try {
      loading.value = true
      error.value = null
      const response = await authApi.getSteamLoginUrl()
      window.location.href = response.data.login_url
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Failed to get login URL'
      throw err
    } finally {
      loading.value = false
    }
  }

  const importGames = async (userId: number) => {
    try {
      loading.value = true
      error.value = null
      const response = await gamesApi.importGames(userId)
      return response.data
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Failed to import games'
      throw err
    } finally {
      loading.value = false
    }
  }

  const fetchGames = async (userId: number) => {
    try {
      loading.value = true
      error.value = null
      const response = await gamesApi.getGames(userId)
      games.value = response.data
      return response.data
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Failed to fetch games'
      throw err
    } finally {
      loading.value = false
    }
  }

  const fetchPlayerStatus = async (userId: number) => {
    try {
      loading.value = true
      error.value = null
      const response = await statusApi.getPlayerStatus(userId)
      playerStatus.value = response.data
      return response.data
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Failed to fetch player status'
      throw err
    } finally {
      loading.value = false
    }
  }

  return {
    currentUser,
    games,
    playerStatus,
    loading,
    error,
    loadCurrentUser,
    logout,
    getSteamLoginUrl,
    importGames,
    fetchGames,
    fetchPlayerStatus,
  }
})
