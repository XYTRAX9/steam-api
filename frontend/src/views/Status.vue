<template>
  <div class="status">
    <div class="container">
      <div class="page-header">
        <div>
          <h1 class="page-title">Статус игрока</h1>
          <p class="page-description">Отслеживайте активность в реальном времени</p>
        </div>
        <button @click="handleRefresh" :disabled="loading || !userId" class="btn btn-primary">
          <svg width="20" height="20" viewBox="0 0 20 20" fill="none" :class="{ spin: loading }">
            <path d="M17 10C17 13.866 13.866 17 10 17C6.13401 17 3 13.866 3 10C3 6.13401 6.13401 3 10 3C11.5719 3 13.0239 3.52375 14.1922 4.41662"
                  stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
            <path d="M14 1V5H10" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
          Обновить
        </button>
      </div>

      <div v-if="error" class="error-banner">
        <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
          <circle cx="10" cy="10" r="8" stroke="currentColor" stroke-width="2"/>
          <path d="M10 6V10M10 14V14.5" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
        </svg>
        {{ error }}
      </div>

      <div v-if="loading && !playerStatus" class="loading-state">
        <div class="spinner"></div>
        <p>Загрузка статуса...</p>
      </div>

      <div v-else-if="playerStatus" class="status-content">
        <div class="profile-card">
          <div class="profile-header">
            <div class="avatar-wrapper">
              <img v-if="playerStatus.avatar_url"
                   :src="playerStatus.avatar_url"
                   :alt="playerStatus.persona_name"
                   class="avatar">
              <div v-else class="avatar-placeholder">
                <svg width="40" height="40" viewBox="0 0 40 40" fill="none">
                  <circle cx="20" cy="15" r="7" stroke="currentColor" stroke-width="2"/>
                  <path d="M8 33C8 26 13 22 20 22C27 22 32 26 32 33" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
                </svg>
              </div>
              <div class="status-dot" :class="statusClass"></div>
            </div>

            <div class="profile-info">
              <h2 class="profile-name">{{ playerStatus.persona_name }}</h2>
              <div class="profile-status">
                <span class="status-text">{{ statusText }}</span>
              </div>
              <a v-if="playerStatus.profile_url"
                 :href="playerStatus.profile_url"
                 target="_blank"
                 class="profile-link">
                Открыть профиль Steam
                <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                  <path d="M6 3H3V13H13V10M9 3H13M13 3V7M13 3L7 9" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
              </a>
            </div>
          </div>

          <div v-if="playerStatus.is_in_game && playerStatus.game_name" class="current-game">
            <div class="game-indicator">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
                <rect x="4" y="7" width="16" height="10" rx="2" stroke="currentColor" stroke-width="2"/>
                <circle cx="9" cy="12" r="2" stroke="currentColor" stroke-width="2"/>
                <circle cx="15" cy="12" r="2" stroke="currentColor" stroke-width="2"/>
              </svg>
            </div>
            <div class="game-info">
              <div class="game-label">Сейчас играет</div>
              <div class="game-title">{{ playerStatus.game_name }}</div>
            </div>
          </div>
        </div>

        <div class="stats-grid">
          <div class="stat-card">
            <div class="stat-icon" style="color: var(--accent);">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
                <circle cx="12" cy="12" r="9" stroke="currentColor" stroke-width="2"/>
                <path d="M12 6V12L16 14" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
              </svg>
            </div>
            <div class="stat-content">
              <div class="stat-label">User ID</div>
              <div class="stat-value">{{ playerStatus.user_id }}</div>
            </div>
          </div>

          <div class="stat-card">
            <div class="stat-icon" style="color: var(--success);">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
                <path d="M20 7L12 3L4 7M20 7L12 11M20 7V17L12 21M12 11L4 7M12 11V21M4 7V17L12 21" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/>
              </svg>
            </div>
            <div class="stat-content">
              <div class="stat-label">Состояние</div>
              <div class="stat-value">{{ getPersonaStateText(playerStatus.persona_state) }}</div>
            </div>
          </div>

          <div class="stat-card">
            <div class="stat-icon" style="color: var(--warning);">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
                <rect x="5" y="5" width="14" height="14" rx="2" stroke="currentColor" stroke-width="2"/>
                <path d="M9 9L15 15M15 9L9 15" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
              </svg>
            </div>
            <div class="stat-content">
              <div class="stat-label">В игре</div>
              <div class="stat-value">{{ playerStatus.is_in_game ? 'Да' : 'Нет' }}</div>
            </div>
          </div>
        </div>
      </div>

      <div v-else class="empty-state">
        <svg width="64" height="64" viewBox="0 0 64 64" fill="none">
          <circle cx="32" cy="26" r="10" stroke="currentColor" stroke-width="2"/>
          <path d="M16 52C16 42 23 36 32 36C41 36 48 42 48 52" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
        </svg>
        <h3>Нет данных</h3>
        <p>Загрузите статус игрока</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()
const userId = ref(1) // В продакшене получать из auth

const playerStatus = computed(() => userStore.playerStatus)
const loading = computed(() => userStore.loading)
const error = computed(() => userStore.error)

const statusClass = computed(() => {
  if (!playerStatus.value) return 'offline'
  if (playerStatus.value.is_in_game) return 'in-game'
  if (playerStatus.value.persona_state === 1) return 'online'
  return 'offline'
})

const statusText = computed(() => {
  if (!playerStatus.value) return 'Не в сети'
  if (playerStatus.value.is_in_game) return 'В игре'
  if (playerStatus.value.persona_state === 1) return 'В сети'
  if (playerStatus.value.persona_state === 3) return 'Не на месте'
  if (playerStatus.value.persona_state === 4) return 'Спит'
  return 'Не в сети'
})

const getPersonaStateText = (state: number) => {
  const states: Record<number, string> = {
    0: 'Не в сети',
    1: 'В сети',
    2: 'Занят',
    3: 'Не на месте',
    4: 'Спит',
    5: 'Хочет обменяться',
    6: 'Хочет играть',
  }
  return states[state] || 'Неизвестно'
}

const handleRefresh = async () => {
  if (!userId.value) return

  try {
    await userStore.fetchPlayerStatus(userId.value)
  } catch (err) {
    console.error('Failed to refresh status:', err)
  }
}

onMounted(async () => {
  if (userId.value) {
    try {
      await userStore.fetchPlayerStatus(userId.value)
    } catch (err) {
      console.error('Failed to load status:', err)
    }
  }
})
</script>

<style scoped>
.status {
  min-height: calc(100vh - 200px);
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 32px;
  gap: 24px;
}

.page-title {
  font-size: 40px;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 8px;
}

.page-description {
  font-size: 16px;
  color: var(--text-secondary);
}

.btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 12px 20px;
  border: none;
  border-radius: 10px;
  font-weight: 600;
  font-size: 15px;
  transition: all 0.2s;
  white-space: nowrap;
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

.spin {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.error-banner {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px 20px;
  border-radius: 12px;
  margin-bottom: 24px;
  font-size: 15px;
  font-weight: 500;
  background: rgba(255, 59, 59, 0.1);
  border: 1px solid rgba(255, 59, 59, 0.2);
  color: var(--error);
}

.loading-state,
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80px 24px;
  text-align: center;
}

.spinner {
  width: 48px;
  height: 48px;
  border: 4px solid var(--glass-border);
  border-top-color: var(--accent);
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 16px;
}

.loading-state p,
.empty-state p {
  color: var(--text-secondary);
  font-size: 16px;
  margin-top: 12px;
}

.empty-state svg {
  color: var(--text-tertiary);
  margin-bottom: 16px;
}

.empty-state h3 {
  font-size: 24px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 8px;
}

.status-content {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.profile-card {
  background: var(--glass-surface);
  border: 1px solid var(--glass-border);
  border-radius: 16px;
  padding: 32px;
  backdrop-filter: blur(12px);
}

.profile-header {
  display: flex;
  gap: 24px;
  align-items: flex-start;
  margin-bottom: 24px;
}

.avatar-wrapper {
  position: relative;
  flex-shrink: 0;
}

.avatar,
.avatar-placeholder {
  width: 80px;
  height: 80px;
  border-radius: 12px;
  background: var(--code-bg);
}

.avatar {
  object-fit: cover;
}

.avatar-placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-tertiary);
}

.status-dot {
  position: absolute;
  bottom: 4px;
  right: 4px;
  width: 16px;
  height: 16px;
  border-radius: 50%;
  border: 3px solid var(--glass-surface);
}

.status-dot.online {
  background: var(--success);
}

.status-dot.in-game {
  background: var(--accent);
  animation: pulse 2s ease-in-out infinite;
}

.status-dot.offline {
  background: var(--text-tertiary);
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.6; }
}

.profile-info {
  flex: 1;
  min-width: 0;
}

.profile-name {
  font-size: 28px;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 8px;
}

.profile-status {
  margin-bottom: 12px;
}

.status-text {
  font-size: 15px;
  color: var(--text-secondary);
  font-weight: 500;
}

.profile-link {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  color: var(--accent);
  font-size: 14px;
  font-weight: 600;
  transition: opacity 0.2s;
}

.profile-link:hover {
  opacity: 0.8;
}

.current-game {
  display: flex;
  gap: 16px;
  padding: 20px;
  background: var(--code-bg);
  border-radius: 12px;
  align-items: center;
}

.game-indicator {
  width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--glass-surface);
  border-radius: 10px;
  color: var(--accent);
  flex-shrink: 0;
}

.game-info {
  flex: 1;
  min-width: 0;
}

.game-label {
  font-size: 13px;
  color: var(--text-tertiary);
  margin-bottom: 4px;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  font-weight: 600;
}

.game-title {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 16px;
}

.stat-card {
  display: flex;
  gap: 16px;
  padding: 20px;
  background: var(--glass-surface);
  border: 1px solid var(--glass-border);
  border-radius: 12px;
  backdrop-filter: blur(12px);
  transition: all 0.2s;
}

.stat-card:hover {
  background: var(--glass-hover);
  transform: translateY(-2px);
}

.stat-icon {
  width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: currentColor;
  opacity: 0.1;
  border-radius: 10px;
  flex-shrink: 0;
}

.stat-icon svg {
  position: relative;
  z-index: 1;
  opacity: 10;
}

.stat-content {
  flex: 1;
  min-width: 0;
}

.stat-label {
  font-size: 13px;
  color: var(--text-tertiary);
  margin-bottom: 6px;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  font-weight: 600;
}

.stat-value {
  font-size: 20px;
  font-weight: 600;
  color: var(--text-primary);
}

@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
    align-items: flex-start;
  }

  .page-title {
    font-size: 32px;
  }

  .btn {
    width: 100%;
    justify-content: center;
  }

  .profile-card {
    padding: 24px;
  }

  .profile-header {
    flex-direction: column;
  }

  .stats-grid {
    grid-template-columns: 1fr;
  }
}
</style>
