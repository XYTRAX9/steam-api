import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useThemeStore = defineStore('theme', () => {
  const theme = ref<'light' | 'dark'>('light')

  const initTheme = () => {
    const saved = localStorage.getItem('theme') as 'light' | 'dark' | null
    if (saved) {
      theme.value = saved
    } else {
      const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches
      theme.value = prefersDark ? 'dark' : 'light'
    }
    applyTheme()
  }

  const toggleTheme = () => {
    theme.value = theme.value === 'light' ? 'dark' : 'light'
    localStorage.setItem('theme', theme.value)
    applyTheme()
  }

  const applyTheme = () => {
    document.body.setAttribute('data-theme', theme.value)
  }

  return {
    theme,
    initTheme,
    toggleTheme,
  }
})
