<template>
  <div class="callback">
    <div class="container">
      <div class="callback-content">
        <div v-if="loading" class="loading-state">
          <div class="spinner"></div>
          <h2>Авторизация через Steam</h2>
          <p>Обработка вашего входа...</p>
        </div>

        <div v-else-if="error" class="error-state">
          <svg width="64" height="64" viewBox="0 0 64 64" fill="none">
            <circle cx="32" cy="32" r="28" stroke="currentColor" stroke-width="2"/>
            <path d="M32 20V36M32 44V46" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
          </svg>
          <h2>Ошибка авторизации</h2>
          <p>{{ error }}</p>
          <RouterLink to="/" class="btn btn-primary">
            Вернуться на главную
          </RouterLink>
        </div>

        <div v-else class="success-state">
          <svg width="64" height="64" viewBox="0 0 64 64" fill="none">
            <circle cx="32" cy="32" r="28" stroke="currentColor" stroke-width="2"/>
            <path d="M20 32L28 40L44 24" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
          <h2>Успешная авторизация!</h2>
          <p>Перенаправление...</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter, RouterLink } from 'vue-router'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const userStore = useUserStore()
const loading = ref(true)
const error = ref<string | null>(null)

onMounted(async () => {
  try {
    const callbackError = new URLSearchParams(window.location.search).get('error')
    if (callbackError) {
      error.value = callbackError === 'steam_unavailable'
        ? 'Не удалось получить профиль Steam. Попробуйте позже.'
        : 'Не удалось подтвердить вход через Steam.'
      loading.value = false
      return
    }

    const user = await userStore.loadCurrentUser()
    if (!user) {
      error.value = 'Сессия не найдена. Войдите снова.'
      loading.value = false
      return
    }

    loading.value = false
    setTimeout(() => {
      router.replace('/games')
    }, 1500)
  } catch (err: any) {
    error.value = err.response?.data?.detail || 'Не удалось завершить авторизацию'
    loading.value = false
  }
})
</script>

<style scoped>
.callback {
  min-height: calc(100vh - 200px);
  display: flex;
  align-items: center;
  justify-content: center;
}

.callback-content {
  max-width: 440px;
  width: 100%;
  padding: 64px 32px;
  text-align: center;
}

.loading-state,
.error-state,
.success-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
}

.spinner {
  width: 56px;
  height: 56px;
  border: 3px solid var(--glass-border);
  border-top-color: var(--accent);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.error-state svg {
  color: var(--error);
  opacity: 0.9;
}

.success-state svg {
  color: var(--success);
  opacity: 0.9;
}

h2 {
  font-size: 24px;
  font-weight: 700;
  color: var(--text-primary);
  margin-top: 8px;
  letter-spacing: -0.01em;
}

p {
  font-size: 15px;
  color: var(--text-secondary);
  line-height: 1.6;
  font-weight: 500;
}

.btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 14px 28px;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  font-size: 14px;
  transition: all 0.15s cubic-bezier(0.4, 0, 0.2, 1);
  margin-top: 16px;
  text-decoration: none;
  cursor: pointer;
}

.btn-primary {
  background: var(--accent);
  color: #0B0E14;
}

.btn-primary:hover {
  background: var(--accent-hover);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(56, 189, 248, 0.35);
}

.btn-primary:active {
  transform: translateY(0);
}
</style>
