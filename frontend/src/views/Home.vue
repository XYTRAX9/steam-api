<template>
  <div class="home">
    <div class="container">
      <div class="hero">
        <div class="hero-content">
          <h1 class="hero-title">
            Steam Integration API
          </h1>
          <p class="hero-description">
            Подключите свой Steam аккаунт и управляйте своей игровой библиотекой через единый интерфейс
          </p>

          <div class="hero-actions">
            <button @click="handleLogin" :disabled="loading" class="btn btn-primary">
              <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
                <path d="M10 1C5.02944 1 1 5.02944 1 10C1 14.9706 5.02944 19 10 19C14.9706 19 19 14.9706 19 10C19 5.02944 14.9706 1 10 1Z" stroke="currentColor" stroke-width="2"/>
                <path d="M10 10L6 13M10 10V5" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
              </svg>
              <span v-if="!loading">Войти через Steam</span>
              <span v-else>Загрузка...</span>
            </button>

            <a href="/docs" target="_blank" class="btn btn-secondary">
              <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
                <path d="M10 1L17 5V15L10 19L3 15V5L10 1Z" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/>
                <path d="M10 10V14M10 6V7" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
              </svg>
              API Docs
            </a>
          </div>

          <div v-if="error" class="error-message">
            {{ error }}
          </div>
        </div>

        <div class="hero-visual">
          <div class="card">
            <div class="card-header">
              <div class="status-indicator"></div>
              <span class="card-label">API Status</span>
            </div>
            <div class="card-body">
              <div class="metric">
                <div class="metric-value">99.9%</div>
                <div class="metric-label">Uptime</div>
              </div>
              <div class="metric">
                <div class="metric-value">&lt;50ms</div>
                <div class="metric-label">Latency</div>
              </div>
            </div>
          </div>

          <div class="card">
            <div class="card-header">
              <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                <rect width="16" height="16" rx="4" fill="currentColor" opacity="0.2"/>
                <path d="M8 4V12M4 8H12" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
              </svg>
              <span class="card-label">Features</span>
            </div>
            <div class="card-body">
              <ul class="feature-list">
                <li>Steam OAuth авторизация</li>
                <li>Импорт игр из библиотеки</li>
                <li>Отслеживание статуса игрока</li>
                <li>REST API с документацией</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()
const loading = ref(false)
const error = ref<string | null>(null)

const handleLogin = async () => {
  try {
    loading.value = true
    error.value = null
    const loginUrl = await userStore.getSteamLoginUrl()
    window.location.href = loginUrl
  } catch (err: any) {
    error.value = err.message || 'Не удалось получить URL для входа'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.home {
  padding: 64px 0;
}

.hero {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 64px;
  align-items: center;
}

.hero-content {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.hero-title {
  font-size: 56px;
  font-weight: 700;
  line-height: 1.1;
  letter-spacing: -0.02em;
  color: var(--text-primary);
}

.hero-description {
  font-size: 18px;
  line-height: 1.6;
  color: var(--text-secondary);
}

.hero-actions {
  display: flex;
  gap: 16px;
  margin-top: 16px;
}

.btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 14px 24px;
  border: none;
  border-radius: 10px;
  font-weight: 600;
  font-size: 15px;
  transition: all 0.2s;
  text-decoration: none;
}

.btn-primary {
  background: var(--accent);
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: var(--accent-hover);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0, 102, 255, 0.3);
}

.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-secondary {
  background: var(--glass-surface);
  color: var(--text-primary);
  border: 1px solid var(--glass-border);
}

.btn-secondary:hover {
  background: var(--glass-hover);
  transform: translateY(-1px);
}

.error-message {
  padding: 12px 16px;
  border-radius: 8px;
  background: rgba(255, 59, 59, 0.1);
  border: 1px solid rgba(255, 59, 59, 0.2);
  color: var(--error);
  font-size: 14px;
}

.hero-visual {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.card {
  background: var(--glass-surface);
  border: 1px solid var(--glass-border);
  border-radius: 16px;
  padding: 24px;
  backdrop-filter: blur(12px);
  transition: all 0.2s;
}

.card:hover {
  background: var(--glass-hover);
  transform: translateY(-2px);
}

.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 16px;
  color: var(--text-secondary);
}

.status-indicator {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--success);
  animation: pulse 2s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

.card-label {
  font-weight: 600;
  font-size: 14px;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.card-body {
  display: flex;
  gap: 32px;
}

.metric {
  flex: 1;
}

.metric-value {
  font-size: 32px;
  font-weight: 700;
  font-family: 'JetBrains Mono', monospace;
  color: var(--text-primary);
  margin-bottom: 4px;
}

.metric-label {
  font-size: 13px;
  color: var(--text-tertiary);
}

.feature-list {
  list-style: none;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.feature-list li {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 15px;
  color: var(--text-secondary);
}

.feature-list li::before {
  content: '';
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--accent);
}

@media (max-width: 968px) {
  .hero {
    grid-template-columns: 1fr;
    gap: 48px;
  }

  .hero-title {
    font-size: 40px;
  }

  .hero-description {
    font-size: 16px;
  }
}

@media (max-width: 640px) {
  .home {
    padding: 32px 0;
  }

  .hero-title {
    font-size: 32px;
  }

  .hero-actions {
    flex-direction: column;
  }

  .btn {
    width: 100%;
    justify-content: center;
  }

  .card-body {
    flex-direction: column;
    gap: 24px;
  }
}
</style>
